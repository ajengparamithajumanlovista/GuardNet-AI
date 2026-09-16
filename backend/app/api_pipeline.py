import io
import time

from PIL import Image
from fastapi import UploadFile

from app.ocr.engine import run_ocr
from app.vision.model import analyze_image as analyze_visual
from app.models.classifier import classify_text
from app.fusion.engine import fusion_score
from app.payment.qris.decoder import decode_qris
from app.payment.intelligence import analyze_payment_intelligence
from app.graph.entity import build_entities
from app.graph.digital_intelligence import build_digital_intelligence
from app.graph.correlation import analyze_cross_content


# ============================================================
# GUARDNET-AI
# MULTIMODAL ANALYSIS PIPELINE
# ============================================================
#
# Pipeline:
#
# Instagram image + caption
#          ↓
#         OCR
#          ↓
#       Visual
#          ↓
#        QRIS
#          ↓
#     Combined Text
#          ↓
#   Text Classification
#          ↓
# Payment Intelligence
#          ↓
# Entity Extraction
#          ↓
# Reliability-Aware Fusion
#          ↓
# Digital Intelligence
#          ↓
# Cross Content Correlation
#
# ============================================================


def normalize_payment_result(
    payment_intelligence
):
    """
    Normalize payment intelligence into the format
    required by fusion and frontend.
    """

    if not isinstance(
        payment_intelligence,
        dict
    ):
        payment_intelligence = {}


    evidence = payment_intelligence.get(
        "evidence",
        []
    )


    if not isinstance(
        evidence,
        list
    ):
        evidence = []


    return {

        "detected":
            bool(
                payment_intelligence.get(
                    "detected",
                    False
                )
            ),

        "evidence":
            evidence,

        "risk":
            float(
                payment_intelligence.get(
                    "risk",
                    0
                )
            ),

        "status":
            payment_intelligence.get(
                "status",
                "success"
            )

    }


# ============================================================
# SAFE QRIS RESULT
# ============================================================

def safe_qris_decode(
    image
):
    """
    Decode QR / QRIS safely.
    """

    try:

        result = decode_qris(
            image
        )

        if isinstance(
            result,
            dict
        ):
            return result


    except Exception as error:

        return {

            "detected":
                False,

            "is_qris":
                False,

            "type":
                None,

            "data":
                None,

            "merchant_name":
                None,

            "merchant_city":
                None,

            "mcc":
                None,

            "amount":
                None,

            "evidence":
                [],

            "error":
                str(error)

        }


    return {

        "detected":
            False,

        "is_qris":
            False,

        "type":
            None,

        "data":
            None,

        "merchant_name":
            None,

        "merchant_city":
            None,

        "mcc":
            None,

        "amount":
            None,

        "evidence":
            []

    }


# ============================================================
# MULTIMODAL ANALYSIS
# ============================================================

async def run_guardnet_analysis(
    image: UploadFile,
    caption: str = ""
):

    start_time = time.time()


    try:

        # ====================================================
        # 1. LOAD IMAGE
        # ====================================================

        content = await image.read()


        if not content:

            return {

                "status":
                    "error",

                "message":
                    "Image kosong."

            }


        img = Image.open(
            io.BytesIO(
                content
            )
        ).convert(
            "RGB"
        )


        # ====================================================
        # 2. OCR
        # ====================================================

        ocr_result = run_ocr(
            img
        )


        # ====================================================
        # 3. VISUAL
        # ====================================================

        visual_result = analyze_visual(
            img
        )


        # ====================================================
        # 4. QR / QRIS
        # ====================================================

        qris_result = safe_qris_decode(
            img
        )


        # ====================================================
        # 5. COMBINED TEXT
        # ====================================================

        ocr_text = str(
            ocr_result.get(
                "text",
                ""
            )
        )


        caption_text = str(
            caption or ""
        )


        combined_text = (

            caption_text.strip()

            + " "

            + ocr_text.strip()

        ).strip()


        # ====================================================
        # 6. TEXT CLASSIFICATION
        # ====================================================

        text_result = classify_text(
            combined_text
        )


        # ====================================================
        # 7. PAYMENT INTELLIGENCE
        # ====================================================

        try:

            payment_intelligence = (
                analyze_payment_intelligence(

                    combined_text,

                    qris_result

                )
            )

        except Exception as error:

            payment_intelligence = {

                "detected":
                    False,

                "evidence":
                    [],

                "risk":
                    0,

                "status":
                    "failed",

                "error":
                    str(error)

            }


        # ====================================================
        # 8. PAYMENT NORMALIZATION
        # ====================================================

        payment_result = (
            normalize_payment_result(
                payment_intelligence
            )
        )


        # ====================================================
        # 9. ENTITY EXTRACTION
        # ====================================================

        entity_result = build_entities(
            combined_text
        )


        if not isinstance(
            entity_result,
            dict
        ):

            entity_result = {}


        # ====================================================
        # 10. QRIS ENTITY
        # ====================================================

        qris_context = (

            qris_result.get(
                "detected",
                False
            )

            or

            payment_intelligence.get(
                "qris",
                {}
            ).get(
                "context_detected",
                False
            )

        )


        if qris_context:

            payment_indicators = (
                entity_result.setdefault(
                    "payment_indicator",
                    []
                )
            )


            if "QRIS" not in payment_indicators:

                payment_indicators.append(
                    "QRIS"
                )


        # ====================================================
        # 11. PHONE ENTITY
        # ====================================================

        phone_numbers = (
            payment_intelligence.get(
                "phone_number",
                []
            )
        )


        if isinstance(
            phone_numbers,
            list
        ):

            phones = (
                entity_result.setdefault(
                    "phone",
                    []
                )
            )


            for phone in phone_numbers:

                if isinstance(
                    phone,
                    dict
                ):

                    normalized = phone.get(
                        "normalized"
                    )

                else:

                    normalized = phone


                if (
                    normalized
                    and
                    normalized not in phones
                ):

                    phones.append(
                        normalized
                    )


        # ====================================================
        # 12. RELIABILITY-AWARE FUSION
        # ====================================================

        classification = fusion_score(

            text=
                text_result,

            payment=
                payment_result,

            entities=
                entity_result,

            visual=
                visual_result,

            ocr=
                ocr_result

        )


        # ====================================================
        # 13. DIGITAL INTELLIGENCE
        # ====================================================

        digital_result = (
            build_digital_intelligence(

                combined_text,

                source=
                    image.filename

            )
        )


        # ====================================================
        # 14. TEMPORARY CASE
        # ====================================================

        temporary_case = {

            "case_id":
                "CURRENT",

            "classification":
                classification,

            "entities":
                entity_result,

            "digital_intelligence":
                digital_result,

            "payment":
                payment_result,

            "payment_intelligence":
                payment_intelligence,

            "qris":
                qris_result

        }


        # ====================================================
        # 15. LOAD PREVIOUS CASES
        # ====================================================

        try:

            from app.main import load_json

            from app.main import CASE_FILE

            existing_cases = load_json(
                CASE_FILE,
                []
            )

        except Exception:

            existing_cases = []


        # ====================================================
        # 16. CROSS-CONTENT CORRELATION
        # ====================================================

        try:

            correlation = analyze_cross_content(

                temporary_case,

                existing_cases

            )

        except Exception as error:

            correlation = {

                "related_cases":
                    [],

                "related_case_count":
                    0,

                "shared_indicators":
                    {},

                "shared_indicator_count":
                    0,

                "correlation_level":
                    "NONE",

                "recurrence": {

                    "count":
                        0,

                    "score":
                        0,

                    "level":
                        "NONE"

                },

                "status":
                    "failed",

                "error":
                    str(error)

            }


        # ====================================================
        # 17. RECURRENCE
        # ====================================================

        recurrence = correlation.get(

            "recurrence",

            {

                "count":
                    0,

                "score":
                    0,

                "level":
                    "NONE"

            }

        )


        # ====================================================
        # 18. RESULT
        # ====================================================

        return {

            "status":
                "success",

            "mode":
                "multimodal",

            "filename":
                image.filename,

            "classification":
                classification,

            "caption":
                caption,

            "combined_text":
                combined_text,

            "text":
                text_result,

            "ocr":
                ocr_result,

            "visual":
                visual_result,

            "qris":
                qris_result,

            "payment":
                payment_result,

            "payment_intelligence":
                payment_intelligence,

            "entities":
                entity_result,

            "digital_intelligence":
                digital_result,

            "cross_content_correlation":
                correlation,

            "recurrence":
                recurrence,

            "processing_time":
                round(

                    time.time()
                    -
                    start_time,

                    3

                )

        }


    except Exception as error:

        return {

            "status":
                "error",

            "message":
                str(error),

            "processing_time":
                round(

                    time.time()
                    -
                    start_time,

                    3

                )

        }