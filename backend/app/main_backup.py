# ============================================================
# GUARDNET-AI
# RESEARCH PUBLICATION EDITION
# FINAL MAIN API
# ============================================================

import os
import json
import time
import uuid
import inspect
from io import BytesIO
from typing import Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="GuardNet-AI Research Publication Edition",
    description=(
        "Multimodal AI System for Detecting Online Gambling "
        "Promotion and Supporting Digital Threat Intelligence"
    ),
    version="2.0.0",
    openapi_version="3.1.0",
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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CASES_FILE = os.path.join(BASE_DIR, "cases.json")
INSTAGRAM_RESULTS_FILE = os.path.join(
    BASE_DIR, "instagram_results.json"
)
THREAT_GRAPH_FILE = os.path.join(
    BASE_DIR, "threat_graph.json"
)


# ============================================================
# SAFE / CORRECT MODULE IMPORTS
#
# Nama import di bawah mengikuti struktur modul GuardNet-AI
# yang sudah digunakan pada backend project:
#
# app.ocr.engine
# app.vision.model
# app.models.classifier
# app.fusion.engine
# app.payment.detector
# app.payment.qris.decoder
# app.payment.intelligence
# app.graph.entity
# app.graph.digital_intelligence
# app.graph.correlation
# app.graph.threat_graph
# ============================================================

def optional_imports():
    modules = {}

    try:
        from app.models.classifier import classify_text
        modules["classify_text"] = classify_text
        print("[GuardNet-AI] Classifier import: OK")
    except Exception as e:
        modules["classify_text"] = None
        print("[GuardNet-AI] Classifier import: FAILED:", e)

    try:
        from app.ocr.engine import run_ocr
        modules["run_ocr"] = run_ocr
        print("[GuardNet-AI] OCR import: OK")
    except Exception as e:
        modules["run_ocr"] = None
        print("[GuardNet-AI] OCR import: FAILED:", e)

    try:
        from app.vision.model import analyze_image as analyze_visual
        modules["analyze_visual"] = analyze_visual
        print("[GuardNet-AI] Visual import: OK")
    except Exception as e:
        modules["analyze_visual"] = None
        print("[GuardNet-AI] Visual import: FAILED:", e)

    try:
        from app.fusion.engine import fusion_score
        modules["fusion_score"] = fusion_score
        print("[GuardNet-AI] Fusion import: OK")
    except Exception as e:
        modules["fusion_score"] = None
        print("[GuardNet-AI] Fusion import: FAILED:", e)

    try:
        from app.payment.detector import detect_payment
        modules["detect_payment"] = detect_payment
        print("[GuardNet-AI] Payment detector import: OK")
    except Exception as e:
        modules["detect_payment"] = None
        print("[GuardNet-AI] Payment detector import: FAILED:", e)

    try:
        from app.payment.qris.decoder import decode_qris
        modules["decode_qris"] = decode_qris
        print("[GuardNet-AI] QRIS decoder import: OK")
    except Exception as e:
        modules["decode_qris"] = None
        print("[GuardNet-AI] QRIS decoder import: FAILED:", e)

    try:
        from app.payment.intelligence import analyze_payment_intelligence
        modules["analyze_payment_intelligence"] = (
            analyze_payment_intelligence
        )
        print("[GuardNet-AI] Payment intelligence import: OK")
    except Exception as e:
        modules["analyze_payment_intelligence"] = None
        print(
            "[GuardNet-AI] Payment intelligence import: FAILED:",
            e,
        )

    try:
        from app.graph.entity import build_entities
        modules["build_entities"] = build_entities
        print("[GuardNet-AI] Entity import: OK")
    except Exception as e:
        modules["build_entities"] = None
        print("[GuardNet-AI] Entity import: FAILED:", e)

    try:
        from app.graph.digital_intelligence import build_digital_intelligence
        modules["build_digital_intelligence"] = build_digital_intelligence
        print("[GuardNet-AI] Digital intelligence import: OK")
    except Exception as e:
        modules["build_digital_intelligence"] = None
        print(
            "[GuardNet-AI] Digital intelligence import: FAILED:",
            e,
        )

    try:
        from app.graph.correlation import analyze_cross_content
        modules["analyze_cross_content"] = analyze_cross_content
        print("[GuardNet-AI] Correlation import: OK")
    except Exception as e:
        modules["analyze_cross_content"] = None
        print("[GuardNet-AI] Correlation import: FAILED:", e)

    try:
        from app.graph.threat_graph import build_threat_graph
        modules["build_threat_graph"] = build_threat_graph
        print("[GuardNet-AI] Threat graph import: OK")
    except Exception as e:
        modules["build_threat_graph"] = None
        print("[GuardNet-AI] Threat graph import: FAILED:", e)

    return modules


MODULES = optional_imports()

classify_text = MODULES["classify_text"]
run_ocr = MODULES["run_ocr"]
analyze_visual = MODULES["analyze_visual"]
fusion_score = MODULES["fusion_score"]
detect_payment = MODULES["detect_payment"]
decode_qris = MODULES["decode_qris"]
analyze_payment_intelligence = MODULES["analyze_payment_intelligence"]
build_entities = MODULES["build_entities"]
build_digital_intelligence = MODULES["build_digital_intelligence"]
analyze_cross_content = MODULES["analyze_cross_content"]
build_threat_graph = MODULES["build_threat_graph"]


# ============================================================
# JSON HELPERS
# ============================================================

def load_json_file(path, default):
    try:
        if not os.path.exists(path):
            return default

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return default


def save_json_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False,
        )


def load_cases():
    data = load_json_file(CASES_FILE, [])

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        cases = data.get("cases", [])
        if isinstance(cases, list):
            return cases

    return []


def save_case(case):
    cases = load_cases()
    cases.append(case)
    save_json_file(CASES_FILE, cases)
    return case


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_input_text(value: Any):
    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    if isinstance(value, list):
        result = []

        for item in value:
            if item is None:
                continue

            value_text = str(item).strip()

            if value_text:
                result.append(value_text)

        return "\n".join(result)

    return str(value).strip()


def normalize_comments(value):
    if value is None:
        return []

    if isinstance(value, list):
        return [
            str(x).strip()
            for x in value
            if x is not None and str(x).strip()
        ]

    if isinstance(value, str):
        value = value.strip()

        if not value:
            return []

        try:
            parsed = json.loads(value)

            if isinstance(parsed, list):
                return [
                    str(x).strip()
                    for x in parsed
                    if x is not None and str(x).strip()
                ]
        except Exception:
            pass

        return [value]

    return [str(value).strip()]


def combine_instagram_content(
    text="",
    caption="",
    comments=None,
    ocr_text="",
):
    sections = []

    text = normalize_input_text(text)
    caption = normalize_input_text(caption)
    comments = normalize_comments(comments)
    ocr_text = normalize_input_text(ocr_text)

    if text:
        sections.append(text)

    if caption:
        sections.append("[CAPTION]\n" + caption)

    if comments:
        sections.append(
            "[COMMENTS]\n" + "\n".join(comments)
        )

    if ocr_text:
        sections.append("[OCR]\n" + ocr_text)

    return "\n\n".join(sections).strip()


# ============================================================
# RESULT NORMALIZATION
# ============================================================

def safe_dict(value):
    return value if isinstance(value, dict) else {}


def normalize_classification(result):
    result = safe_dict(result)

    label = (
        result.get("label")
        or result.get("classification")
        or "C0"
    )

    try:
        score = float(result.get("score", 0))
    except Exception:
        score = 0.0

    probabilities = result.get("probabilities")

    if not isinstance(probabilities, dict):
        probabilities = {}

    return {
        **result,
        "label": label,
        "score": max(0.0, min(score, 1.0)),
        "probabilities": probabilities,
        "status": result.get("status", "success"),
    }


def normalize_payment_result(result):
    result = safe_dict(result)

    return {
        **result,
        "detected": bool(result.get("detected", False)),
        "evidence": (
            result.get("evidence", [])
            if isinstance(result.get("evidence", []), list)
            else []
        ),
        "risk": max(
            0.0,
            min(
                float(result.get("risk", 0) or 0),
                1.0,
            ),
        ),
    }


# ============================================================
# TEXT CLASSIFICATION
# ============================================================

def run_text_classifier(text):
    if not classify_text:
        return {
            "label": "C0",
            "score": 0.0,
            "probabilities": {},
            "status": "classifier_unavailable",
        }

    try:
        return normalize_classification(
            classify_text(text)
        )
    except Exception as e:
        return {
            "label": "C0",
            "score": 0.0,
            "probabilities": {},
            "status": "error",
            "error": str(e),
        }


# ============================================================
# PAYMENT INTELLIGENCE
# ============================================================

def run_payment_analysis(text, qris_result=None):
    qris_result = safe_dict(qris_result)

    detector_result = {}

    if detect_payment:
        try:
            detector_result = normalize_payment_result(
                detect_payment(text)
            )
        except Exception as e:
            detector_result = {
                "detected": False,
                "evidence": [],
                "risk": 0.0,
                "error": str(e),
            }
    else:
        detector_result = {
            "detected": False,
            "evidence": [],
            "risk": 0.0,
        }

    intelligence_result = {}

    if analyze_payment_intelligence:
        try:
            raw = analyze_payment_intelligence(
                text,
                qris_result,
            )

            if isinstance(raw, dict):
                intelligence_result = raw
        except Exception as e:
            intelligence_result = {
                "status": "error",
                "error": str(e),
            }

    evidence = []

    for source in (
        detector_result.get("evidence", []),
        intelligence_result.get("evidence", []),
    ):
        if isinstance(source, list):
            for item in source:
                if item not in evidence:
                    evidence.append(item)

    detected = (
        detector_result.get("detected", False)
        or bool(intelligence_result.get("detected", False))
        or bool(qris_result.get("detected", False))
        or bool(qris_result.get("is_qris", False))
    )

    risk_values = [
        float(detector_result.get("risk", 0) or 0),
        float(intelligence_result.get("risk", 0) or 0),
    ]

    if qris_result.get("detected") or qris_result.get("is_qris"):
        risk_values.append(1.0)

    risk = max(0.0, min(max(risk_values), 1.0))

    normalized = {
        **intelligence_result,
        "detected": detected,
        "evidence": evidence,
        "risk": round(risk, 3),
    }

    return (
        normalize_payment_result(detector_result),
        normalized,
    )


# ============================================================
# ENTITY + DIGITAL INTELLIGENCE
# ============================================================

def run_entities(text):
    if not build_entities:
        return {
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
            "status": "entity_unavailable",
        }

    try:
        result = build_entities(text)
        return safe_dict(result)
    except Exception as e:
        return {
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
            "status": "error",
            "error": str(e),
        }


def run_digital_intelligence(text, source="text_input"):
    if not build_digital_intelligence:
        return {
            "status": "unavailable",
            "account": [],
            "domain": [],
            "url": [],
            "contact": [],
        }

    try:
        result = build_digital_intelligence(
            text,
            source=source,
        )

        return safe_dict(result)

    except TypeError:
        try:
            result = build_digital_intelligence(text)
            return safe_dict(result)
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


# ============================================================
# OCR
# ============================================================

def run_ocr_analysis(image):
    if not run_ocr:
        return {
            "text": "",
            "status": "unavailable",
            "confidence": 0.0,
        }

    try:
        result = run_ocr(image)
        result = safe_dict(result)

        result.setdefault("text", "")
        result.setdefault("status", "success")

        return result

    except Exception as e:
        return {
            "text": "",
            "status": "error",
            "confidence": 0.0,
            "error": str(e),
        }


# ============================================================
# VISUAL
# ============================================================

def run_visual_analysis(image):
    if not analyze_visual:
        return {
            "visual_score": 0.0,
            "evidence": [],
            "status": "unavailable",
        }

    try:
        result = analyze_visual(image)
        return safe_dict(result)

    except Exception as e:
        return {
            "visual_score": 0.0,
            "evidence": [],
            "status": "error",
            "error": str(e),
        }


# ============================================================
# QRIS
# ============================================================

def run_qris_analysis(image):
    if not decode_qris:
        return {
            "detected": False,
            "is_qris": False,
            "evidence": [],
            "status": "unavailable",
        }

    try:
        result = decode_qris(image)
        return safe_dict(result)

    except Exception as e:
        return {
            "detected": False,
            "is_qris": False,
            "evidence": [],
            "status": "error",
            "error": str(e),
        }


# ============================================================
# FUSION
# ============================================================

def run_fusion(
    text_result,
    payment_result,
    entities,
    visual_result=None,
    ocr_result=None,
):
    if not fusion_score:
        return text_result

    try:
        result = fusion_score(
            text=text_result,
            payment=payment_result,
            entities=entities,
            visual=visual_result or {},
            ocr=ocr_result or {},
        )

        return normalize_classification(result)

    except TypeError:
        # Compatibility fallback for an older fusion signature.
        try:
            result = fusion_score(
                text=text_result,
                payment=payment_result,
                entities=entities,
            )

            return normalize_classification(result)

        except Exception as e:
            return {
                **text_result,
                "fusion_status": "error",
                "fusion_error": str(e),
            }

    except Exception as e:
        return {
            **text_result,
            "fusion_status": "error",
            "fusion_error": str(e),
        }


# ============================================================
# RISK / REVIEW PRIORITY
# ============================================================

def calculate_review_priority(
    classification,
    entities,
    payment,
    digital_intelligence,
    recurrence=0.0,
):
    classification = safe_dict(classification)
    entities = safe_dict(entities)
    payment = safe_dict(payment)
    digital_intelligence = safe_dict(digital_intelligence)

    try:
        confidence = float(
            classification.get(
                "confidence",
                classification.get("score", 0),
            )
            or 0
        )
    except Exception:
        confidence = 0.0

    evidence = classification.get("evidence", {})

    evidence_strength = 0.0

    if isinstance(evidence, dict):
        gambling = evidence.get("gambling_terms", [])
        promotional = evidence.get("promotional_terms", [])
        strong = evidence.get("strong_promotional_phrases", [])
        reasons = evidence.get("reasons", [])

        evidence_strength = min(
            (
                len(gambling)
                + len(promotional)
                + (2 * len(strong))
                + len(reasons)
            ) / 10.0,
            1.0,
        )

    entity_count = 0

    for key in (
        "account",
        "domain",
        "url",
        "phone",
        "bank_account",
        "payment_indicator",
        "threat_indicator",
    ):
        value = entities.get(key, [])
        if isinstance(value, list):
            entity_count += len(value)

    for key in (
        "account",
        "domain",
        "url",
        "contact",
    ):
        value = digital_intelligence.get(key, [])
        if isinstance(value, list):
            entity_count += len(value)

    entity_score = min(entity_count / 5.0, 1.0)

    try:
        payment_score = float(payment.get("risk", 0) or 0)
    except Exception:
        payment_score = 0.0

    recurrence = max(0.0, min(float(recurrence or 0), 1.0))

    score = (
        0.35 * confidence
        + 0.25 * evidence_strength
        + 0.15 * entity_score
        + 0.15 * payment_score
        + 0.10 * recurrence
    )

    score = max(0.0, min(score, 1.0))

    if score >= 0.75:
        priority = "HIGH"
    elif score >= 0.45:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return {
        "score": round(score, 3),
        "priority": priority,
        "components": {
            "classification_confidence": round(confidence, 3),
            "evidence_strength": round(evidence_strength, 3),
            "entity_correlation": round(entity_score, 3),
            "payment_correlation": round(payment_score, 3),
            "recurrence": round(recurrence, 3),
        },
    }


# ============================================================
# CASE CREATION
# ============================================================

def create_case(
    filename,
    caption,
    comments,
    combined_text,
    classification,
    ocr,
    visual,
    payment,
    payment_intelligence,
    qris,
    entities,
    digital_intelligence,
    correlation,
):
    cases = load_cases()

    case_id = f"CASE-{len(cases) + 1:04d}-{uuid.uuid4().hex[:6].upper()}"

    recurrence = safe_dict(correlation).get(
        "recurrence",
        {},
    )

    recurrence_score = (
        safe_dict(recurrence).get("score", 0)
        if isinstance(recurrence, dict)
        else 0
    )

    review_priority = calculate_review_priority(
        classification=classification,
        entities=entities,
        payment=payment,
        digital_intelligence=digital_intelligence,
        recurrence=recurrence_score,
    )

    case = {
        "case_id": case_id,
        "created_at": time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "status": "PENDING_REVIEW",
        "filename": filename,
        "caption": caption,
        "comments": comments,
        "combined_text": combined_text,
        "classification": classification,
        "ocr": ocr,
        "visual": visual,
        "payment": payment,
        "payment_intelligence": payment_intelligence,
        "qris": qris,
        "entities": entities,
        "digital_intelligence": digital_intelligence,
        "correlation": correlation,
        "review_priority": review_priority,
    }

    save_case(case)

    return case


# ============================================================
# CROSS-CONTENT CORRELATION
# ============================================================

def run_correlation(current_case, existing_cases):
    if not analyze_cross_content:
        return {
            "recurrence": {
                "count": 0,
                "score": 0,
                "level": "NONE",
            },
            "shared_indicators": [],
            "status": "unavailable",
        }

    try:
        return safe_dict(
            analyze_cross_content(
                current_case,
                existing_cases,
            )
        )

    except Exception as e:
        return {
            "recurrence": {
                "count": 0,
                "score": 0,
                "level": "NONE",
            },
            "shared_indicators": [],
            "status": "error",
            "error": str(e),
        }


# ============================================================
# TEXT ANALYSIS INTERNAL
# ============================================================

def analyze_text_internal(
    text,
    caption="",
    comments=None,
):
    comments = normalize_comments(comments)

    combined_text = combine_instagram_content(
        text=text,
        caption=caption,
        comments=comments,
    )

    classification = run_text_classifier(
        combined_text
    )

    payment, payment_intelligence = run_payment_analysis(
        combined_text
    )

    entities = run_entities(
        combined_text
    )

    digital_intelligence = run_digital_intelligence(
        combined_text,
        source="text_input",
    )

    # Text mode still uses the same fusion architecture.
    final_classification = run_fusion(
        text_result=classification,
        payment_result=payment,
        entities=entities,
        visual_result={},
        ocr_result={},
    )

    return {
        "text": combined_text,
        "classification": final_classification,
        "payment": payment,
        "payment_intelligence": payment_intelligence,
        "entities": entities,
        "digital_intelligence": digital_intelligence,
    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def home():
    return {
        "system": "GuardNet-AI",
        "edition": "Research Publication",
        "version": "2.0.0",
        "status": "running",
        "architecture": "multimodal",
        "classification": ["C0", "C1", "C2"],
        "endpoints": [
            "/health",
            "/analyze",
            "/api/analyze",
            "/analyze-image",
            "/api/analyze-image",
            "/api/detect-post",
            "/api/instagram-results",
            "/api/cases",
            "/api/cases/{case_id}",
            "/api/statistics",
            "/api/threat-graph",
            "/api/review/{case_id}",
        ],
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "GuardNet-AI",
        "version": "2.0.0",
        "modules": {
            "classifier": bool(classify_text),
            "ocr": bool(run_ocr),
            "visual": bool(analyze_visual),
            "fusion": bool(fusion_score),
            "payment_detector": bool(detect_payment),
            "payment_intelligence": bool(
                analyze_payment_intelligence
            ),
            "qris": bool(decode_qris),
            "entity": bool(build_entities),
            "digital_intelligence": bool(
                build_digital_intelligence
            ),
            "correlation": bool(analyze_cross_content),
            "threat_graph": bool(build_threat_graph),
        },
    }


# ============================================================
# POST /analyze
#
# JSON:
# {
#   "text": "...",
#   "caption": "...",
#   "comments": ["...", "..."]
# }
# ============================================================

@app.post("/analyze")
async def analyze_endpoint(request: Request):
    try:
        content_type = (
            request.headers.get("content-type", "")
            .lower()
        )

        text = ""
        caption = ""
        comments = []

        if "application/json" in content_type:
            payload = await request.json()

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
                        payload.get("comment", []),
                    )
                )

        elif "multipart/form-data" in content_type:
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

        elif "application/x-www-form-urlencoded" in content_type:
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

        result = analyze_text_internal(
            text=text,
            caption=caption,
            comments=comments,
        )

        return {
            "status": "success",
            "mode": "instagram-text",
            "input": {
                "text": text,
                "caption": caption,
                "comments": comments,
            },
            "combined_text": result["text"],
            **result,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# POST /api/analyze
# ============================================================

@app.post("/api/analyze")
async def api_analyze(request: Request):
    return await analyze_endpoint(request)


# ============================================================
# MULTIMODAL IMAGE ANALYSIS
# ============================================================

def analyze_uploaded_image(
    image,
    filename="unknown.jpg",
    caption="",
    comments=None,
):
    comments = normalize_comments(comments)

    # --------------------------------------------------------
    # OCR
    # --------------------------------------------------------

    ocr_result = run_ocr_analysis(image)

    ocr_text = normalize_input_text(
        ocr_result.get("text", "")
    )

    # --------------------------------------------------------
    # Native text + OCR
    # --------------------------------------------------------

    combined_text = combine_instagram_content(
        caption=caption,
        comments=comments,
        ocr_text=ocr_text,
    )

    # --------------------------------------------------------
    # TEXT CLASSIFIER
    # --------------------------------------------------------

    text_result = run_text_classifier(
        combined_text
    )

    # --------------------------------------------------------
    # VISUAL
    # --------------------------------------------------------

    visual_result = run_visual_analysis(
        image
    )

    # --------------------------------------------------------
    # QRIS
    # --------------------------------------------------------

    qris_result = run_qris_analysis(
        image
    )

    # --------------------------------------------------------
    # PAYMENT
    # --------------------------------------------------------

    payment, payment_intelligence = run_payment_analysis(
        combined_text,
        qris_result,
    )

    # --------------------------------------------------------
    # ENTITY
    # --------------------------------------------------------

    entity_result = run_entities(
        combined_text
    )

    # Add QRIS as a payment indicator when detected.
    if (
        qris_result.get("detected")
        or qris_result.get("is_qris")
    ):
        indicators = entity_result.setdefault(
            "payment_indicator",
            [],
        )

        if "QRIS" not in indicators:
            indicators.append("QRIS")

    # --------------------------------------------------------
    # DIGITAL INTELLIGENCE
    # --------------------------------------------------------

    digital_result = run_digital_intelligence(
        combined_text,
        source=filename,
    )

    # --------------------------------------------------------
    # FUSION
    # --------------------------------------------------------

    classification = run_fusion(
        text_result=text_result,
        payment_result=payment,
        entities=entity_result,
        visual_result=visual_result,
        ocr_result=ocr_result,
    )

    # --------------------------------------------------------
    # CORRELATION
    # --------------------------------------------------------

    temporary_case = {
        "case_id": "CURRENT",
        "filename": filename,
        "classification": classification,
        "entities": entity_result,
        "digital_intelligence": digital_result,
        "payment": payment,
        "payment_intelligence": payment_intelligence,
        "qris": qris_result,
        "ocr": ocr_result,
        "visual": visual_result,
    }

    existing_cases = load_cases()

    correlation = run_correlation(
        temporary_case,
        existing_cases,
    )

    # --------------------------------------------------------
    # CASE
    #
    # Sesuai rancangan penelitian:
    # C2 diteruskan ke evidence capture,
    # digital intelligence dan payment intelligence.
    # --------------------------------------------------------

    case = None

    if classification.get("label") == "C2":
        case = create_case(
            filename=filename,
            caption=caption,
            comments=comments,
            combined_text=combined_text,
            classification=classification,
            ocr=ocr_result,
            visual=visual_result,
            payment=payment,
            payment_intelligence=payment_intelligence,
            qris=qris_result,
            entities=entity_result,
            digital_intelligence=digital_result,
            correlation=correlation,
        )

    recurrence = safe_dict(correlation).get(
        "recurrence",
        {
            "count": 0,
            "score": 0,
            "level": "NONE",
        },
    )

    return {
        "status": "success",
        "mode": "multimodal",
        "filename": filename,
        "classification": classification,
        "caption": caption,
        "comments": comments,
        "combined_text": combined_text,
        "ocr": ocr_result,
        "visual": visual_result,
        "text": text_result,
        "payment": payment,
        "payment_intelligence": payment_intelligence,
        "qris": qris_result,
        "entities": entity_result,
        "digital_intelligence": digital_result,
        "cross_content_correlation": correlation,
        "recurrence": recurrence,
        "case": case,
    }


# ============================================================
# IMAGE ROUTES
# ============================================================

async def process_image_upload(
    image: UploadFile,
    caption: str = "",
    comments: str = "",
):
    contents = await image.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Image kosong.",
        )

    try:
        pil_image = Image.open(
            BytesIO(contents)
        )

        # Load image fully before UploadFile lifecycle changes.
        pil_image.load()

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"File bukan gambar yang valid: {e}",
        )

    result = analyze_uploaded_image(
        image=pil_image,
        filename=image.filename or "unknown.jpg",
        caption=caption,
        comments=comments,
    )

    return result


@app.post("/analyze-image")
async def analyze_image_endpoint(
    image: UploadFile = File(...),
    caption: str = Form(""),
    comments: str = Form(""),
):
    return await process_image_upload(
        image=image,
        caption=caption,
        comments=comments,
    )


@app.post("/api/analyze-image")
async def api_analyze_image(
    image: UploadFile = File(...),
    caption: str = Form(""),
    comments: str = Form(""),
):
    return await process_image_upload(
        image=image,
        caption=caption,
        comments=comments,
    )


@app.post("/api/detect-post")
async def detect_post(
    image: UploadFile = File(...),
    caption: str = Form(""),
    comments: str = Form(""),
):
    return await process_image_upload(
        image=image,
        caption=caption,
        comments=comments,
    )


# ============================================================
# INSTAGRAM RESULTS
# ============================================================

@app.get("/api/instagram-results")
def instagram_results():
    data = load_json_file(
        INSTAGRAM_RESULTS_FILE,
        [],
    )

    if not isinstance(data, list):
        data = []

    return {
        "status": "success",
        "count": len(data),
        "results": data,
    }


# ============================================================
# CASES
# ============================================================

@app.get("/api/cases")
def get_cases():
    cases = load_cases()

    return {
        "status": "success",
        "count": len(cases),
        "total": len(cases),
        "cases": cases,
    }


@app.get("/api/cases/{case_id}")
def get_case(case_id: str):
    cases = load_cases()

    for case in cases:
        if str(case.get("case_id")) == str(case_id):
            return {
                "status": "success",
                "case": case,
            }

    raise HTTPException(
        status_code=404,
        detail="Case not found",
    )


# ============================================================
# STATISTICS
# ============================================================

@app.get("/api/statistics")
def statistics():
    cases = load_cases()

    counts = {
        "C0": 0,
        "C1": 0,
        "C2": 0,
    }

    for case in cases:
        classification = case.get(
            "classification",
            {},
        )

        if isinstance(classification, dict):
            label = (
                classification.get("label")
                or classification.get("classification")
            )
        else:
            label = classification

        if label in counts:
            counts[label] += 1

    total = len(cases)

    return {
        "status": "success",
        "total": total,
        "total_cases": total,
        "classification": counts,
        "c0": counts["C0"],
        "c1": counts["C1"],
        "c2": counts["C2"],
    }


# ============================================================
# THREAT GRAPH
# ============================================================

@app.get("/api/threat-graph")
def threat_graph():
    cases = load_cases()

    if not build_threat_graph:
        stored = load_json_file(
            THREAT_GRAPH_FILE,
            {
                "nodes": [],
                "links": [],
            },
        )

        return {
            **safe_dict(stored),
            "status": "unavailable",
        }

    try:
        graph = build_threat_graph(cases)

        if not isinstance(graph, dict):
            graph = {
                "nodes": [],
                "links": [],
            }

        nodes = graph.get("nodes", [])
        links = graph.get("links", [])

        return {
            **graph,
            "status": "success",
            "node_count": len(nodes)
            if isinstance(nodes, list)
            else 0,
            "link_count": len(links)
            if isinstance(links, list)
            else 0,
        }

    except TypeError:
        # Compatibility fallback if the graph module expects no argument.
        try:
            graph = build_threat_graph()

            if not isinstance(graph, dict):
                graph = {
                    "nodes": [],
                    "links": [],
                }

            return {
                **graph,
                "status": "success",
            }

        except Exception as e:
            return {
                "nodes": [],
                "links": [],
                "node_count": 0,
                "link_count": 0,
                "status": "error",
                "error": str(e),
            }

    except Exception as e:
        return {
            "nodes": [],
            "links": [],
            "node_count": 0,
            "link_count": 0,
            "status": "error",
            "error": str(e),
        }


# ============================================================
# REVIEW
# ============================================================

@app.post("/api/review/{case_id}")
def review_case(case_id: str):
    cases = load_cases()

    for case in cases:
        if str(case.get("case_id")) == str(case_id):
            return {
                "status": "success",
                "case_id": case_id,
                "classification": case.get(
                    "classification",
                    {},
                ),
                "evidence": case.get(
                    "ocr",
                    {},
                ),
                "entities": case.get(
                    "entities",
                    {},
                ),
                "payment": case.get(
                    "payment",
                    {},
                ),
                "review_priority": case.get(
                    "review_priority",
                    {},
                ),
                "detail": "Case loaded successfully",
            }

    raise HTTPException(
        status_code=404,
        detail="Case not found",
    )


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def startup_event():
    print("=" * 60)
    print(" GuardNet-AI API STARTED")
    print("=" * 60)
    print("Version:", "2.0.0")
    print("Cases:", CASES_FILE)

    modules = {
        "Classifier": classify_text,
        "OCR": run_ocr,
        "Visual": analyze_visual,
        "Fusion": fusion_score,
        "Payment Detector": detect_payment,
        "Payment Intelligence": analyze_payment_intelligence,
        "QRIS": decode_qris,
        "Entity": build_entities,
        "Digital Intelligence": build_digital_intelligence,
        "Correlation": analyze_cross_content,
        "Threat Graph": build_threat_graph,
    }

    for name, module in modules.items():
        print(
            f"{name:24}: "
            + ("OK" if module else "UNAVAILABLE")
        )

    print("=" * 60)
