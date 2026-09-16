# ============================================================
# GUARDNET-AI
# RESEARCH PUBLICATION EDITION
# MAIN API
# ============================================================

import os
import json
import uuid
import time
from datetime import datetime, timezone
from typing import Optional, Any

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException,
    Request
)

from fastapi.middleware.cors import CORSMiddleware

from PIL import Image


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="GuardNet-AI Research Publication Edition",
    description="Multimodal AI System for Detecting Online Gambling Promotion",
    version="1.6.0",
    openapi_version="3.1.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


CASES_FILE = os.path.join(
    BASE_DIR,
    "cases.json"
)


INSTAGRAM_RESULTS_FILE = os.path.join(
    BASE_DIR,
    "instagram_results.json"
)


# ============================================================
# SAFE IMPORTS
# ============================================================

# ------------------------------------------------------------
# CLASSIFIER
# ------------------------------------------------------------

try:

    from app.models.classifier import classify_text

except Exception as e:

    print(
        "[GuardNet-AI] Classifier import failed:",
        e
    )

    classify_text = None


# ------------------------------------------------------------
# OCR
# ------------------------------------------------------------

try:

    from app.ocr.engine import run_ocr

except Exception as e:

    print(
        "[GuardNet-AI] OCR import failed:",
        e
    )

    run_ocr = None


# ------------------------------------------------------------
# VISUAL
# ------------------------------------------------------------

try:

    from app.vision.model import analyze_image

except Exception as e:

    print(
        "[GuardNet-AI] Visual import failed:",
        e
    )

    analyze_image = None


# ------------------------------------------------------------
# PAYMENT
# ------------------------------------------------------------

try:

    from app.payment.detector import detect_payment

except Exception:

    try:

        from app.payment.intelligence import (
            detect_payment
        )

    except Exception as e:

        print(
            "[GuardNet-AI] Payment import failed:",
            e
        )

        detect_payment = None


# ------------------------------------------------------------
# QRIS
# ------------------------------------------------------------

try:

    from app.payment.qris.decoder import decode_qris

except Exception as e:

        print(
            "[GuardNet-AI] QRIS import failed:",
            e
        )

        decode_qris = None


# ------------------------------------------------------------
# PAYMENT INTELLIGENCE
# ------------------------------------------------------------

try:

    from app.payment.intelligence import (
        analyze_payment_intelligence
    )

except Exception as e:

    print(
        "[GuardNet-AI] Payment intelligence import failed:",
        e
    )

    analyze_payment_intelligence = None


# ------------------------------------------------------------
# ENTITY
# ------------------------------------------------------------

try:

    from app.graph.entity import (
        build_entities
    )

except Exception as e:

    print(
        "[GuardNet-AI] Entity import failed:",
        e
    )

    build_entities = None


# ------------------------------------------------------------
# FUSION
# ------------------------------------------------------------

try:

    from app.fusion.engine import fusion_score

except Exception as e:

    print(
        "[GuardNet-AI] Fusion import failed:",
        e
    )

    fusion_score = None


# ------------------------------------------------------------
# DIGITAL INTELLIGENCE
# ------------------------------------------------------------

try:

    from app.graph.digital_intelligence import (
        build_digital_intelligence
    )

except Exception as e:

    print(
        "[GuardNet-AI] Digital intelligence import failed:",
        e
    )

    build_digital_intelligence = None


# ------------------------------------------------------------
# THREAT GRAPH
# ------------------------------------------------------------

try:

    from app.graph.threat_graph import (
        build_threat_graph
    )

except Exception as e:

    print(
        "[GuardNet-AI] Threat graph import failed:",
        e
    )

    build_threat_graph = None


# ------------------------------------------------------------
# CORRELATION
# ------------------------------------------------------------

try:

    from app.graph.correlation import (
        analyze_cross_content
    )

except Exception as e:

    print(
        "[GuardNet-AI] Correlation import failed:",
        e
    )

    analyze_cross_content = None


# ============================================================
# JSON HELPERS
# ============================================================

def load_json_file(
    path,
    default
):

    try:

        if not os.path.exists(path):

            return default

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return default


def save_json_file(
    path,
    data
):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# CASE HELPERS
# ============================================================

def load_cases():

    data = load_json_file(
        CASES_FILE,
        []
    )

    if isinstance(
        data,
        list
    ):

        return data

    if isinstance(
        data,
        dict
    ):

        if isinstance(
            data.get("cases"),
            list
        ):

            return data["cases"]

    return []


def save_case(
    case
):

    cases = load_cases()

    cases.append(
        case
    )

    save_json_file(
        CASES_FILE,
        cases
    )

    return case


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_input_text(
    value: Any
):

    if value is None:

        return ""

    if isinstance(
        value,
        str
    ):

        return value.strip()

    if isinstance(
        value,
        list
    ):

        parts = []

        for item in value:

            if item is None:

                continue

            text = str(
                item
            ).strip()

            if text:

                parts.append(
                    text
                )

        return "\n".join(
            parts
        )

    return str(
        value
    ).strip()


# ============================================================
# COMBINE INSTAGRAM CONTENT
# ============================================================

def combine_instagram_content(
    text="",
    caption="",
    comments=None
):

    sections = []

    text = normalize_input_text(
        text
    )

    caption = normalize_input_text(
        caption
    )

    comments = comments or []

    comments_text = normalize_input_text(
        comments
    )

    if text:

        sections.append(
            text
        )

    if caption:

        sections.append(
            "[CAPTION]\n" +
            caption
        )

    if comments_text:

        sections.append(
            "[COMMENTS]\n" +
            comments_text
        )

    return "\n\n".join(
        sections
    ).strip()


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def home():

    return {

        "name":
            "GuardNet-AI Research Publication Edition",

        "version":
            "2.0.0",

        "description":
            "Multimodal AI System for Detecting Online Gambling Promotion",

        "status":
            "running",

        "endpoints": [

            "/health",

            "/analyze",

            "/api/analyze",

            "/analyze-image",

            "/api/analyze-image",

            "/api/detect-post",

            "/api/instagram-results",

            "/api/cases",

            "/api/statistics",

            "/api/threat-graph"

        ]

    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {

        "status":
            "healthy",

        "service":
            "GuardNet-AI",

        "version":
            "2.0.0",

        "modules": {

            "classifier":
                bool(classify_text),

            "ocr":
                bool(run_ocr),

            "visual":
                bool(analyze_image),

            "payment":
                bool(detect_payment),

            "payment_intelligence":
                bool(analyze_payment_intelligence),

            "qris":
                bool(decode_qris),

            "entity":
                bool(build_entities),

            "fusion":
                bool(fusion_score),

            "digital_intelligence":
                bool(build_digital_intelligence),

            "correlation":
                bool(analyze_cross_content),

            "threat_graph":
                bool(build_threat_graph)

        }

    }


# ============================================================
# CYBER INTELLIGENCE HELPERS
# ============================================================

def safe_dict(value):
    return value if isinstance(value, dict) else {}


def normalize_classification(value):
    result = safe_dict(value).copy()

    if "classification" not in result:
        if "label" in result:
            result["classification"] = result.get("label", "C0")
        else:
            result["classification"] = "C0"

    if "label" not in result:
        result["label"] = result.get("classification", "C0")

    try:
        result["risk_score"] = float(
            result.get(
                "risk_score",
                result.get("score", 0.0)
            ) or 0.0
        )
    except Exception:
        result["risk_score"] = 0.0

    return result


def run_digital_intelligence(
    text,
    source="instagram_post"
):
    if not build_digital_intelligence:
        return {
            "account": [],
            "url": [],
            "domain": [],
            "contact": [],
            "entity_count": 0,
            "graph_links": [],
            "status": "unavailable",
        }

    try:
        result = build_digital_intelligence(
            text,
            source=source
        )
        return safe_dict(result)

    except TypeError:
        try:
            result = build_digital_intelligence(text)
            return safe_dict(result)
        except Exception as e:
            return {
                "account": [],
                "url": [],
                "domain": [],
                "contact": [],
                "entity_count": 0,
                "graph_links": [],
                "status": "error",
                "error": str(e),
            }

    except Exception as e:
        return {
            "account": [],
            "url": [],
            "domain": [],
            "contact": [],
            "entity_count": 0,
            "graph_links": [],
            "status": "error",
            "error": str(e),
        }


def run_cross_content_correlation(
    current_case,
    existing_cases
):
    if not analyze_cross_content:
        return {
            "related_cases": [],
            "related_case_count": 0,
            "shared_indicators": {
                "account": [],
                "domain": [],
                "url": [],
                "contact": [],
                "payment": [],
            },
            "shared_indicator_count": 0,
            "strong_shared_indicator_count": 0,
            "correlation_level": "NONE",
            "recurrence": {
                "count": 0,
                "score": 0.0,
                "level": "NONE",
            },
            "status": "unavailable",
        }

    try:
        result = analyze_cross_content(
            current_case,
            existing_cases
        )
        return safe_dict(result)

    except Exception as e:
        return {
            "related_cases": [],
            "related_case_count": 0,
            "shared_indicators": {
                "account": [],
                "domain": [],
                "url": [],
                "contact": [],
                "payment": [],
            },
            "shared_indicator_count": 0,
            "strong_shared_indicator_count": 0,
            "correlation_level": "NONE",
            "recurrence": {
                "count": 0,
                "score": 0.0,
                "level": "NONE",
            },
            "status": "error",
            "error": str(e),
        }


def build_cyber_security_layer(
    classification,
    payment,
    qris,
    entities,
    digital_intelligence,
    correlation
):
    classification = normalize_classification(
        classification
    )
    payment = safe_dict(payment)
    qris = safe_dict(qris)
    entities = safe_dict(entities)
    digital_intelligence = safe_dict(
        digital_intelligence
    )
    correlation = safe_dict(correlation)

    label = classification.get(
        "classification",
        "C0"
    )

    try:
        risk_score = max(
            0.0,
            min(
                float(
                    classification.get(
                        "risk_score",
                        classification.get(
                            "score",
                            0.0
                        )
                    ) or 0.0
                ),
                1.0
            )
        )
    except Exception:
        risk_score = 0.0

    recurrence = safe_dict(
        correlation.get(
            "recurrence",
            {}
        )
    )

    recurrence_score = float(
        recurrence.get(
            "score",
            0.0
        ) or 0.0
    )

    payment_detected = bool(
        payment.get("detected", False)
        or qris.get("detected", False)
        or qris.get("is_qris", False)
    )

    entity_count = int(
        entities.get(
            "entity_count",
            digital_intelligence.get(
                "entity_count",
                0
            )
        ) or 0
    )

    strong_shared = int(
        correlation.get(
            "strong_shared_indicator_count",
            0
        ) or 0
    )

    # Security score combines the already-produced
    # multimodal risk with independent cyber indicators.
    security_score = max(
        risk_score,
        min(
            1.0,
            (
                risk_score * 0.70
                + recurrence_score * 0.15
                + (0.10 if payment_detected else 0.0)
                + min(entity_count, 5) * 0.01
                + min(strong_shared, 3) * 0.02
            )
        )
    )

    if label == "C2" or security_score >= 0.75:
        severity = "HIGH"
        action = "BLOCK_AND_REVIEW"
    elif label == "C1" or security_score >= 0.40:
        severity = "MEDIUM"
        action = "REVIEW"
    else:
        severity = "LOW"
        action = "ALLOW_WITH_MONITORING"

    alerts = []

    if label == "C2":
        alerts.append(
            "High-risk gambling promotion detected."
        )

    if payment_detected:
        alerts.append(
            "Payment-related indicator detected."
        )

    if strong_shared >= 1:
        alerts.append(
            "Shared digital indicator detected across cases."
        )

    if recurrence.get("level") in (
        "MEDIUM",
        "HIGH"
    ):
        alerts.append(
            "Potential recurring digital threat pattern detected."
        )

    if not alerts:
        alerts.append(
            "No critical cyber-security indicator detected."
        )

    return {
        "security_score": round(
            security_score,
            3
        ),
        "severity": severity,
        "action": action,
        "alerts": alerts,
        "controls": {
            "payment_monitoring":
                payment_detected,
            "entity_monitoring":
                entity_count > 0,
            "recurrence_monitoring":
                recurrence.get(
                    "level",
                    "NONE"
                ) != "NONE",
            "manual_review":
                severity in (
                    "MEDIUM",
                    "HIGH"
                ),
        },
        "status": "success",
    }


def build_case_record(
    filename,
    text,
    caption,
    comments,
    classification,
    entities,
    digital_intelligence,
    payment,
    qris,
    ocr,
    visual,
    correlation,
    security
):
    return {
        "case_id": str(
            uuid.uuid4()
        ),
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "source": "GuardNet-AI",
        "filename": filename,
        "text": text,
        "caption": caption,
        "comments": comments,
        "classification": classification,
        "entities": entities,
        "digital_intelligence": digital_intelligence,
        "payment": payment,
        "qris": qris,
        "ocr": ocr,
        "visual": visual,
        "correlation": correlation,
        "recurrence": correlation.get(
            "recurrence",
            {}
        ),
        "cyber_security": security,
        "status": (
            "PENDING_REVIEW"
            if security.get("severity")
            in ("MEDIUM", "HIGH")
            else "ANALYZED"
        ),
    }


# ============================================================
# TEXT ANALYSIS INTERNAL
# ============================================================

def analyze_text_internal(
    text,
    caption="",
    comments=None
):
    text = normalize_input_text(text)
    caption = normalize_input_text(caption)
    comments = comments or []

    if isinstance(comments, str):
        comments = [comments]

    combined_text = combine_instagram_content(
        text=text,
        caption=caption,
        comments=comments
    )

    classification = (
        classify_text(combined_text)
        if classify_text
        else {
            "label": "C0",
            "score": 0.0,
            "status": "unavailable",
        }
    )

    if detect_payment:
        try:
            payment = detect_payment(
                combined_text
            )
        except Exception as e:
            payment = {
                "detected": False,
                "evidence": [],
                "risk": 0.0,
                "error": str(e),
            }
    else:
        payment = {
            "detected": False,
            "evidence": [],
            "risk": 0.0,
        }

    if analyze_payment_intelligence:
        try:
            payment_intelligence = (
                analyze_payment_intelligence(
                    combined_text,
                    {}
                )
            )
            if not isinstance(
                payment_intelligence,
                dict
            ):
                payment_intelligence = {}
        except Exception as e:
            payment_intelligence = {
                "status": "error",
                "error": str(e),
            }
    else:
        payment_intelligence = {
            "status": "unavailable"
        }

    if build_entities:
        try:
            entities = build_entities(
                combined_text
            )
        except Exception as e:
            entities = {
                "account": [],
                "phone": [],
                "url": [],
                "domain": [],
                "bank_account": [],
                "payment_indicator": [],
                "threat_indicator": [],
                "nodes": [],
                "graph_links": [],
                "entity_count": 0,
                "error": str(e),
            }
    else:
        entities = {
            "account": [],
            "phone": [],
            "url": [],
            "domain": [],
            "bank_account": [],
            "payment_indicator": [],
            "threat_indicator": [],
            "nodes": [],
            "graph_links": [],
            "entity_count": 0,
        }

    digital_intelligence = run_digital_intelligence(
        combined_text,
        source="text_input"
    )

    if fusion_score:
        try:
            final_classification = fusion_score(
                text=classification,
                payment=payment,
                entities=entities,
                visual={},
                ocr={}
            )
        except TypeError:
            final_classification = fusion_score(
                text=classification,
                payment=payment,
                entities=entities
            )
        except Exception as e:
            final_classification = {
                **classification,
                "fusion_status": "error",
                "fusion_error": str(e),
            }
    else:
        final_classification = classification

    final_classification = normalize_classification(
        final_classification
    )

    current_case = {
        "case_id": "CURRENT_TEXT",
        "classification": final_classification,
        "entities": entities,
        "digital_intelligence": digital_intelligence,
        "payment": payment,
        "payment_intelligence": payment_intelligence,
    }

    correlation = run_cross_content_correlation(
        current_case,
        load_cases()
    )

    security = build_cyber_security_layer(
        final_classification,
        payment,
        {},
        entities,
        digital_intelligence,
        correlation
    )

    return {
        "text": combined_text,
        "classification": final_classification,
        "payment": payment,
        "payment_intelligence": payment_intelligence,
        "entities": entities,
        "digital_intelligence": digital_intelligence,
        "cross_content_correlation": correlation,
        "recurrence": correlation.get(
            "recurrence",
            {}
        ),
        "cyber_security": security,
    }



# ============================================================
# REQUEST FIELD HELPERS
# ============================================================

def normalize_comments(value):
    """
    Normalize comments coming from JSON, form-data, query string,
    a single string, or a JSON-encoded list.
    """
    if value is None:
        return []

    if isinstance(value, list):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    if isinstance(value, tuple):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    if isinstance(value, str):
        value = value.strip()

        if not value:
            return []

        if value.startswith("["):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [
                        str(item).strip()
                        for item in parsed
                        if str(item).strip()
                    ]
            except Exception:
                pass

        return [value]

    return [str(value).strip()]


async def parse_analyze_request(request: Request):
    """
    Parse /api/analyze consistently across:
      - application/json
      - multipart/form-data
      - application/x-www-form-urlencoded
      - query parameters as a final fallback
    """
    text = ""
    caption = ""
    comments = []

    content_type = (
        request.headers.get("content-type", "")
        .lower()
    )

    if "application/json" in content_type:
        try:
            payload = await request.json()
        except Exception:
            payload = {}

        if isinstance(payload, dict):
            text = normalize_input_text(
                payload.get("text", "")
            )
            caption = normalize_input_text(
                payload.get("caption", "")
            )
            comments = normalize_comments(
                payload.get(
                    "comments",
                    payload.get("comment", [])
                )
            )

    elif (
        "multipart/form-data" in content_type
        or
        "application/x-www-form-urlencoded" in content_type
    ):
        form = await request.form()

        text = normalize_input_text(
            form.get("text", "")
        )
        caption = normalize_input_text(
            form.get("caption", "")
        )
        comments = normalize_comments(
            form.get("comments", [])
        )

    # Query parameters are only fallback data.
    if not text and not caption and not comments:
        text = normalize_input_text(
            request.query_params.get("text", "")
        )
        caption = normalize_input_text(
            request.query_params.get("caption", "")
        )
        comments = normalize_comments(
            request.query_params.get("comments", "")
        )

    return text, caption, comments


# ============================================================
# POST /analyze
#
# IMPORTANT:
# Endpoint ini menerima:
#
# 1. JSON
# 2. Form
#
# sehingga extension Instagram tidak lagi terkena 422
# karena parameter text dianggap query parameter.
# ============================================================

@app.post("/analyze")
async def analyze_endpoint(
    request: Request
):
    """
    Text/Instagram analysis endpoint.

    Accepts JSON:
    {
        "text": "...",
        "caption": "...",
        "comments": ["...", "..."]
    }

    Also accepts form-data / urlencoded requests.
    """
    try:
        text, caption, comments = await parse_analyze_request(
            request
        )

        combined_text = combine_instagram_content(
            text=text,
            caption=caption,
            comments=comments
        )

        result = analyze_text_internal(
            text=text,
            caption=caption,
            comments=comments
        )

        return {
            "status": "success",
            "mode": "instagram-text",
            "input": {
                "text": text,
                "caption": caption,
                "comments": comments,
            },
            "combined_text": combined_text,
            **result,
        }

    except Exception as e:
        return {
            "status": "error",
            "mode": "instagram-text",
            "message": str(e),
        }


# ============================================================
# POST /api/analyze
# ============================================================

@app.post("/api/analyze")
async def api_analyze(
    request: Request
):
    return await analyze_endpoint(request)
# ============================================================
# IMAGE ANALYSIS
# ============================================================

def analyze_uploaded_image(
    image,
    caption="",
    comments=None,
    filename="uploaded_image"
):
    comments = comments or []

    # ========================================================
    # OCR
    # ========================================================
    if run_ocr:
        try:
            ocr_result = run_ocr(image)
        except Exception as e:
            ocr_result = {
                "text": "",
                "status": "failed",
                "error": str(e),
            }
    else:
        ocr_result = {
            "text": "",
            "status": "unavailable",
        }

    ocr_text = normalize_input_text(
        ocr_result.get("text", "")
    )

    native_text = combine_instagram_content(
        text="",
        caption=caption,
        comments=comments
    )

    combined_text = native_text

    if ocr_text:
        if combined_text:
            combined_text += "\n\n"
        combined_text += "[OCR]\n" + ocr_text

    # ========================================================
    # TEXT CLASSIFICATION
    # ========================================================
    if classify_text:
        try:
            text_classification = classify_text(
                combined_text
            )
        except Exception as e:
            text_classification = {
                "label": "C0",
                "score": 0.0,
                "status": "error",
                "error": str(e),
            }
    else:
        text_classification = {
            "label": "C0",
            "score": 0.0,
            "status": "unavailable",
        }

    # ========================================================
    # PAYMENT
    # ========================================================
    if detect_payment:
        try:
            payment_result = detect_payment(
                combined_text
            )
        except Exception as e:
            payment_result = {
                "detected": False,
                "evidence": [],
                "risk": 0.0,
                "error": str(e),
            }
    else:
        payment_result = {
            "detected": False,
            "evidence": [],
            "risk": 0.0,
        }

    if analyze_payment_intelligence:
        try:
            payment_intelligence = (
                analyze_payment_intelligence(
                    combined_text,
                    {}
                )
            )
            if not isinstance(
                payment_intelligence,
                dict
            ):
                payment_intelligence = {}
        except Exception as e:
            payment_intelligence = {
                "status": "error",
                "error": str(e),
            }
    else:
        payment_intelligence = {
            "status": "unavailable"
        }

    # ========================================================
    # QRIS
    # ========================================================
    if decode_qris:
        try:
            qris_result = decode_qris(
                image
            )
        except Exception as e:
            qris_result = {
                "detected": False,
                "is_qris": False,
                "evidence": [],
                "error": str(e),
            }
    else:
        qris_result = {
            "detected": False,
            "is_qris": False,
            "evidence": [],
        }

    # ========================================================
    # ENTITY
    # ========================================================
    if build_entities:
        try:
            entities = build_entities(
                combined_text
            )
        except Exception as e:
            entities = {
                "account": [],
                "phone": [],
                "url": [],
                "domain": [],
                "bank_account": [],
                "payment_indicator": [],
                "threat_indicator": [],
                "nodes": [],
                "graph_links": [],
                "entity_count": 0,
                "error": str(e),
            }
    else:
        entities = {
            "account": [],
            "phone": [],
            "url": [],
            "domain": [],
            "bank_account": [],
            "payment_indicator": [],
            "threat_indicator": [],
            "nodes": [],
            "graph_links": [],
            "entity_count": 0,
        }

    # ========================================================
    # DIGITAL INTELLIGENCE
    # ========================================================
    digital_intelligence = run_digital_intelligence(
        combined_text,
        source=filename or "instagram_post"
    )

    # ========================================================
    # VISUAL
    # ========================================================
    if analyze_image:
        try:
            visual_result = analyze_image(
                image
            )
        except Exception as e:
            visual_result = {
                "visual_score": 0.0,
                "evidence": [],
                "status": "failed",
                "error": str(e),
            }
    else:
        visual_result = {
            "visual_score": 0.0,
            "evidence": [],
            "status": "unavailable",
        }

    # ========================================================
    # MULTIMODAL FUSION
    # ========================================================
    if fusion_score:
        try:
            fusion_result = fusion_score(
                text=text_classification,
                payment=payment_result,
                entities=entities,
                visual=visual_result,
                ocr=ocr_result
            )
        except TypeError:
            fusion_result = fusion_score(
                text=text_classification,
                payment=payment_result,
                entities=entities
            )
        except Exception as e:
            fusion_result = {
                **text_classification,
                "fusion_status": "error",
                "fusion_error": str(e),
            }
    else:
        fusion_result = text_classification

    fusion_result = normalize_classification(
        fusion_result
    )

    # ========================================================
    # CROSS-CONTENT CORRELATION
    # ========================================================
    current_case = {
        "case_id": "CURRENT_IMAGE",
        "classification": fusion_result,
        "entities": entities,
        "digital_intelligence": digital_intelligence,
        "payment": payment_result,
        "payment_intelligence": payment_intelligence,
        "qris": qris_result,
    }

    existing_cases = load_cases()

    correlation = run_cross_content_correlation(
        current_case,
        existing_cases
    )

    recurrence = correlation.get(
        "recurrence",
        {
            "count": 0,
            "score": 0.0,
            "level": "NONE",
        }
    )

    # ========================================================
    # CYBER SECURITY LAYER
    # ========================================================
    cyber_security = build_cyber_security_layer(
        fusion_result,
        payment_result,
        qris_result,
        entities,
        digital_intelligence,
        correlation
    )

    # ========================================================
    # EXPLAINABLE AI
    # ========================================================
    explanation = fusion_result.get(
        "explanation"
    )

    if not explanation:
        explanation = {
            "risk_level":
                cyber_security.get(
                    "severity",
                    "LOW"
                ),
            "confidence_percent":
                round(
                    float(
                        fusion_result.get(
                            "confidence",
                            0.0
                        ) or 0.0
                    ) * 100,
                    1
                ),
            "multimodal":
                len(
                    fusion_result.get(
                        "active_modality_names",
                        []
                    )
                ) >= 2,
            "reasons":
                cyber_security.get(
                    "alerts",
                    []
                ),
        }

    # ========================================================
    # SAVE HIGH-RISK CASE
    # ========================================================
    case = None

    if fusion_result.get(
        "classification"
    ) == "C2":

        case = build_case_record(
            filename=filename,
            text=combined_text,
            caption=caption,
            comments=comments,
            classification=fusion_result,
            entities=entities,
            digital_intelligence=digital_intelligence,
            payment=payment_result,
            qris=qris_result,
            ocr=ocr_result,
            visual=visual_result,
            correlation=correlation,
            security=cyber_security
        )

        save_case(case)

    return {
        "status": "success",
        "mode": "multimodal",
        "filename": filename,
        "classification": fusion_result,
        "explainable_ai": explanation,
        "text": {
            "text": combined_text,
            "classification": text_classification,
            "payment": payment_result,
            "entities": entities,
        },
        "ocr": ocr_result,
        "visual": visual_result,
        "payment": payment_result,
        "payment_intelligence": payment_intelligence,
        "qris": qris_result,
        "entities": entities,
        "digital_intelligence": digital_intelligence,
        "cross_content_correlation": correlation,
        "recurrence": recurrence,
        "cyber_security": cyber_security,
        "fusion": fusion_result,
        "caption": caption,
        "comments": comments,
        "combined_text": combined_text,
        "case": case,
    }


# ============================================================
# POST /api/analyze-image
# ============================================================

@app.post("/api/analyze-image")
async def api_analyze_image(
    image: UploadFile = File(...),
    caption: str = Form(""),
    comments: str = Form("")
):

    try:

        contents = await image.read()

        from io import BytesIO

        pil_image = Image.open(
            BytesIO(contents)
        )


        # ----------------------------------------------------
        # COMMENTS
        # ----------------------------------------------------
        comment_list = normalize_comments(
            comments
        )

        result = analyze_uploaded_image(

            pil_image,
            caption,
            comment_list,
            filename=image.filename or "uploaded_image"
        )


        return {

            "filename":
                image.filename,

            **result

        }


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# ============================================================
# POST /analyze-image
# ============================================================

@app.post("/analyze-image")
async def analyze_image_endpoint(
    image: UploadFile = File(...),
    caption: str = Form(""),
    comments: str = Form("")
):

    return await api_analyze_image(
        image=image,
        caption=caption,
        comments=comments
    )


# ============================================================
# POST /api/detect-post
# ============================================================

@app.post("/api/detect-post")
async def detect_post(
    image: UploadFile = File(...),
    caption: str = Form(""),
    comments: str = Form("")
):

    return await api_analyze_image(
        image=image,
        caption=caption,
        comments=comments
    )


# ============================================================
# INSTAGRAM RESULTS
# ============================================================

@app.get("/api/instagram-results")
def instagram_results():

    data = load_json_file(
        INSTAGRAM_RESULTS_FILE,
        []
    )


    return {

        "status":
            "success",

        "count":
            len(data)
            if isinstance(
                data,
                list
            )
            else 0,

        "results":
            data

    }


# ============================================================
# CASES
# ============================================================

@app.get("/api/cases")
def get_cases():

    cases = load_cases()


    return {

        "status":
            "success",

        "count":
            len(cases),

        "cases":
            cases

    }


# ============================================================
# SINGLE CASE
# ============================================================

@app.get("/api/cases/{case_id}")
def get_case(
    case_id: str
):

    cases = load_cases()


    for case in cases:

        if str(
            case.get(
                "case_id"
            )
        ) == str(
            case_id
        ):

            return {

                "status":
                    "success",

                "case":
                    case

            }


    raise HTTPException(

        status_code=404,

        detail="Case not found"

    )


# ============================================================
# STATISTICS
# ============================================================

@app.get("/api/statistics")
def statistics():

    cases = load_cases()


    total = len(
        cases
    )


    c0 = 0
    c1 = 0
    c2 = 0


    for case in cases:

        classification = case.get(
            "classification",
            {}
        )


        if isinstance(
            classification,
            dict
        ):

            label = classification.get(
                "label"
            )

            if not label:

                label = classification.get(
                    "classification"
                )

        else:

            label = classification


        if label == "C0":

            c0 += 1

        elif label == "C1":

            c1 += 1

        elif label == "C2":

            c2 += 1


    return {

        "status":
            "success",

        "total_cases":
            total,

        "total":
            total,

        "classification": {

            "C0":
                c0,

            "C1":
                c1,

            "C2":
                c2

        },

        "c0":
            c0,

        "c1":
            c1,

        "c2":
            c2

    }


# ============================================================
# THREAT GRAPH
# ============================================================

@app.get("/api/threat-graph")
def threat_graph():

    cases = load_cases()


    if build_threat_graph:

        try:

            graph = build_threat_graph(
                cases
            )

            return graph

        except Exception as e:

            return {

                "nodes":
                    [],

                "links":
                    [],

                "node_count":
                    0,

                "link_count":
                    0,

                "status":
                    "failed",

                "error":
                    str(e)

            }


    return {

        "nodes":
            [],

        "links":
            [],

        "node_count":
            0,

        "link_count":
            0,

        "status":
            "unavailable"

    }


# ============================================================
# REVIEW CASE
# ============================================================

@app.post("/api/review/{case_id}")
def review_case(
    case_id: str
):

    cases = load_cases()


    for case in cases:

        if str(
            case.get(
                "case_id"
            )
        ) == str(
            case_id
        ):

            return {

                "status":
                    "success",

                "case_id":
                    case_id,

                "classification":
                    case.get(
                        "classification",
                        {}
                    ),

                "evidence":
                    case.get(
                        "evidence",
                        {}
                    ),

                "detail":
                    "Case loaded successfully"

            }


    raise HTTPException(

        status_code=404,

        detail="Case not found"

    )


# ============================================================
# STARTUP
# ============================================================

@app.on_event(
    "startup"
)
def startup_event():

    print(
        "=============================================="
    )

    print(
        " GuardNet-AI API STARTED"
    )

    print(
        "=============================================="
    )

    print(
        "Cases file:",
        CASES_FILE
    )

    print(
        "Classifier:",
        "OK"
        if classify_text
        else
        "UNAVAILABLE"
    )

    print(
        "OCR:",
        "OK"
        if run_ocr
        else
        "UNAVAILABLE"
    )

    print(
        "Visual:",
        "OK"
        if analyze_image
        else
        "UNAVAILABLE"
    )

    print(
        "Payment:",
        "OK"
        if detect_payment
        else
        "UNAVAILABLE"
    )

    print(
        "QRIS:",
        "OK"
        if decode_qris
        else
        "UNAVAILABLE"
    )

    print(
        "Entity:",
        "OK"
        if build_entities
        else
        "UNAVAILABLE"
    )

    print(
        "Fusion:",
        "OK"
        if fusion_score
        else
        "UNAVAILABLE"
    )

    print(
        "Payment Intelligence:",
        "OK"
        if analyze_payment_intelligence
        else
        "UNAVAILABLE"
    )

    print(
        "Digital Intelligence:",
        "OK"
        if build_digital_intelligence
        else
        "UNAVAILABLE"
    )

    print(
        "Correlation:",
        "OK"
        if analyze_cross_content
        else
        "UNAVAILABLE"
    )

    print(
        "Threat Graph:",
        "OK"
        if build_threat_graph
        else
        "UNAVAILABLE"
    )

    print(
        "=============================================="
    )