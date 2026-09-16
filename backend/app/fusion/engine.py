# ============================================================
# GUARDNET-AI
# RELIABILITY-AWARE MULTIMODAL FUSION ENGINE
# FINAL REVISED VERSION
# ============================================================

from typing import Any, Dict, List
import re


# ============================================================
# BASIC UTILITIES
# ============================================================

def clamp(value: Any, minimum: float = 0.0, maximum: float = 1.0) -> float:
    """
    Safely clamp a numeric value into [minimum, maximum].
    """
    try:
        value = float(value)
    except (TypeError, ValueError):
        return minimum

    return max(minimum, min(value, maximum))


def safe_list(value: Any) -> List:
    """
    Always return a list.
    """
    if isinstance(value, list):
        return value

    if value is None:
        return []

    return [value]


def normalize_text(value: Any) -> str:
    """
    Normalize text for evidence matching.
    """
    if value is None:
        return ""

    text = str(value).lower()

    text = re.sub(
        r"[^a-z0-9@._:/#\-\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# GAMBLING VOCABULARY
# ============================================================

GAMBLING_TERMS = {
    "judi",
    "judi online",
    "judi slot",
    "slot",
    "slots",
    "gacor",
    "scatter",
    "scater",
    "bet",
    "betting",
    "taruhan",
    "togel",
    "casino",
    "kasino",
    "jackpot",
    "spin",
    "deposit",
    "withdraw",
    "wd",
    "maxwin",
    "free spin",
    "bonus",
    "pragmatic",
    "zeus",
    "starlight",
    "mahjong",
}


PROMOTIONAL_TERMS = {
    "daftar",
    "daftar sekarang",
    "bonus",
    "bonus besar",
    "bonus new member",
    "bonus member baru",
    "promo",
    "promosi",
    "gampang menang",
    "mudah menang",
    "menang besar",
    "maxwin",
    "jackpot",
    "deposit sekarang",
    "main sekarang",
    "buruan",
    "klik link",
    "link di bio",
}


STRONG_GAMBLING_PHRASES = {
    "slot gacor",
    "slot gacor hari ini",
    "gampang menang",
    "mudah menang",
    "bonus besar",
    "deposit sekarang",
    "daftar sekarang",
    "main sekarang",
    "gampang scatter",
    "gampang scater",
    "scatter bosku",
    "tiap malem di kasi jatah",
}


# ============================================================
# TEXT SCORE
# ============================================================

def get_text_score(text: Dict[str, Any]) -> float:
    """
    Obtain classifier score from text modality.

    Supports:
        score
        risk_score
        confidence
    """

    if not text:
        return 0.0

    score = text.get("score")

    if score is None:
        score = text.get("risk_score")

    if score is None:
        score = text.get("gambling_relevance")

    if score is None:
        score = 0.0

    return clamp(score)


# ============================================================
# TEXT RELIABILITY
# ============================================================

def get_text_reliability(text: Dict[str, Any]) -> float:
    """
    Reliability of text classifier.

    Stronger when:
        - classifier succeeds
        - text exists
        - evidence exists
        - gambling/promotional terms exist
    """

    if not text:
        return 0.0

    reliability = 0.0

    if text.get("status") == "success":
        reliability += 0.40

    raw_text = normalize_text(
        text.get("text")
        or text.get("normalized_text")
        or ""
    )

    if len(raw_text) >= 20:
        reliability += 0.20

    elif len(raw_text) >= 5:
        reliability += 0.10

    evidence = text.get("evidence", {})

    if isinstance(evidence, dict):

        gambling_terms = safe_list(
            evidence.get("gambling_terms")
        )

        promotional_terms = safe_list(
            evidence.get("promotional_terms")
        )

        strong_phrases = safe_list(
            evidence.get("strong_promotional_phrases")
        )

        if gambling_terms:
            reliability += 0.15

        if promotional_terms:
            reliability += 0.10

        if strong_phrases:
            reliability += 0.15

    return clamp(reliability)


# ============================================================
# OCR SCORE
# ============================================================

def get_ocr_score(ocr: Dict[str, Any]) -> float:
    """
    Obtain OCR gambling score.

    If the OCR module already provides a score, use it.

    Otherwise derive a conservative score from:
        gambling_terms
        promotional_terms
        strong_promotional_phrases
    """

    if not ocr:
        return 0.0

    existing = ocr.get("score")

    if existing is None:
        existing = ocr.get("gambling_relevance")

    if existing is not None:
        base_score = clamp(existing)
    else:
        base_score = 0.0

    gambling_terms = safe_list(
        ocr.get("gambling_terms")
    )

    promotional_terms = safe_list(
        ocr.get("promotional_terms")
    )

    strong_phrases = safe_list(
        ocr.get("strong_promotional_phrases")
    )

    # Evidence directly produced by OCR.
    evidence_score = 0.0

    if gambling_terms:
        evidence_score += 0.20

    if len(gambling_terms) >= 2:
        evidence_score += 0.10

    if promotional_terms:
        evidence_score += 0.15

    if strong_phrases:
        evidence_score += 0.20

    if len(strong_phrases) >= 2:
        evidence_score += 0.10

    # Raw OCR text can contain misspellings such as:
    # "scater" instead of "scatter".
    raw_text = normalize_text(
        ocr.get("text")
        or ocr.get("raw_text")
        or ""
    )

    raw_gambling_hits = 0

    for term in GAMBLING_TERMS:
        if term in raw_text:
            raw_gambling_hits += 1

    if raw_gambling_hits >= 1:
        evidence_score += 0.15

    if raw_gambling_hits >= 2:
        evidence_score += 0.10

    return clamp(
        max(
            base_score,
            evidence_score
        )
    )


# ============================================================
# OCR RELIABILITY
# ============================================================

def get_ocr_reliability(ocr: Dict[str, Any]) -> float:
    """
    Reliability of OCR output.
    """

    if not ocr:
        return 0.0

    reliability = 0.0

    if ocr.get("status") == "success":
        reliability += 0.40

    confidence = ocr.get("confidence")

    if confidence is not None:
        reliability += 0.20 * clamp(confidence)

    quality = ocr.get("quality")

    if quality is not None:
        reliability += 0.15 * clamp(quality)

    text = str(
        ocr.get(
            "text",
            ""
        )
    ).strip()

    if len(text) >= 100:
        reliability += 0.15

    elif len(text) >= 20:
        reliability += 0.10

    elif len(text) >= 3:
        reliability += 0.05

    gambling_terms = safe_list(
        ocr.get("gambling_terms")
    )

    if gambling_terms:
        reliability += 0.10

    return clamp(reliability)


# ============================================================
# VISUAL SCORE
# ============================================================

def get_visual_score(
    visual: Dict[str, Any]
) -> float:

    if not visual:
        return 0.0

    return clamp(
        visual.get(
            "visual_score",
            0.0
        )
    )


# ============================================================
# VISUAL RELIABILITY
# ============================================================

def get_visual_reliability(
    visual: Dict[str, Any]
) -> float:

    if not visual:
        return 0.0

    reliability = 0.0

    if visual.get("status") == "success":
        reliability += 0.40

    try:

        width = int(
            visual.get(
                "width",
                0
            )
        )

        height = int(
            visual.get(
                "height",
                0
            )
        )

        if width >= 200 and height >= 200:
            reliability += 0.20

        elif width >= 100 and height >= 100:
            reliability += 0.10

    except (
        ValueError,
        TypeError
    ):
        pass

    try:

        contrast = float(
            visual.get(
                "contrast",
                0
            )
        )

        if contrast >= 10:
            reliability += 0.20

        elif contrast >= 5:
            reliability += 0.10

    except (
        ValueError,
        TypeError
    ):
        pass

    if visual.get("evidence"):
        reliability += 0.20

    return clamp(reliability)


# ============================================================
# PAYMENT SCORE
# ============================================================

def get_payment_score(
    payment: Dict[str, Any]
) -> float:

    if not payment:
        return 0.0

    if payment.get(
        "detected",
        False
    ):

        evidence = safe_list(
            payment.get(
                "evidence"
            )
        )

        lowered = [
            str(item).lower()
            for item in evidence
        ]

        if any(
            "qris" in item
            for item in lowered
        ):
            return 1.0

        return min(
            max(
                len(evidence),
                1
            ) / 4.0,
            1.0
        )

    return 0.0


# ============================================================
# PAYMENT RELIABILITY
# ============================================================

def get_payment_reliability(
    payment: Dict[str, Any]
) -> float:

    if not payment:
        return 0.0

    if payment.get(
        "detected",
        False
    ):

        evidence = safe_list(
            payment.get(
                "evidence"
            )
        )

        if evidence:
            return 0.95

        return 0.75

    # IMPORTANT:
    # If payment is absent, do NOT allow the payment modality
    # to dilute the risk of the other modalities.
    return 0.0


# ============================================================
# ENTITY SCORE
# ============================================================

def get_entity_score(
    entities: Dict[str, Any]
) -> float:

    if not entities:
        return 0.0

    evidence_count = 0

    if entities.get("account"):
        evidence_count += 1

    if (
        entities.get("phone")
        or
        entities.get("contact")
    ):
        evidence_count += 1

    if (
        entities.get("url")
        or
        entities.get("domain")
    ):
        evidence_count += 1

    if entities.get(
        "payment_indicator"
    ):
        evidence_count += 1

    if entities.get(
        "threat_indicator"
    ):
        evidence_count += 1

    return min(
        evidence_count / 5.0,
        1.0
    )


# ============================================================
# ENTITY RELIABILITY
# ============================================================

def get_entity_reliability(
    entities: Dict[str, Any]
) -> float:

    if not entities:
        return 0.0

    total_entities = 0

    for key in [

        "account",
        "phone",
        "contact",
        "url",
        "domain",
        "bank_account",
        "payment_indicator",
        "threat_indicator"

    ]:

        values = entities.get(
            key,
            []
        )

        if isinstance(
            values,
            list
        ):
            total_entities += len(
                values
            )

    if total_entities == 0:

        # Entity module executed successfully but found
        # no indicator. Give only a small reliability.
        return 0.20

    return min(
        0.40
        +
        (
            total_entities
            * 0.12
        ),
        1.0
    )


# ============================================================
# EVIDENCE EXTRACTION
# ============================================================

def extract_cross_modal_evidence(
    text,
    ocr,
    payment,
    entities,
    visual
):
    """
    Extract evidence shared across modalities.

    This is the important revision:
    evidence agreement can increase risk even when
    one modality has low confidence.
    """

    gambling_hits = set()
    promotional_hits = set()

    sources = []

    # --------------------------------------------------------
    # TEXT
    # --------------------------------------------------------

    if text:

        evidence = text.get(
            "evidence",
            {}
        )

        if isinstance(
            evidence,
            dict
        ):

            for item in safe_list(
                evidence.get(
                    "gambling_terms"
                )
            ):
                gambling_hits.add(
                    normalize_text(item)
                )

            for item in safe_list(
                evidence.get(
                    "promotional_terms"
                )
            ):
                promotional_hits.add(
                    normalize_text(item)
                )

            for item in safe_list(
                evidence.get(
                    "strong_promotional_phrases"
                )
            ):
                promotional_hits.add(
                    normalize_text(item)
                )

        if gambling_hits or promotional_hits:
            sources.append(
                "text"
            )

    # --------------------------------------------------------
    # OCR
    # --------------------------------------------------------

    if ocr:

        for item in safe_list(
            ocr.get(
                "gambling_terms"
            )
        ):
            gambling_hits.add(
                normalize_text(item)
            )

        for item in safe_list(
            ocr.get(
                "promotional_terms"
            )
        ):
            promotional_hits.add(
                normalize_text(item)
            )

        for item in safe_list(
            ocr.get(
                "strong_promotional_phrases"
            )
        ):
            promotional_hits.add(
                normalize_text(item)
            )

        raw_ocr = normalize_text(
            ocr.get("text")
            or ocr.get("raw_text")
            or ""
        )

        # Detect common OCR misspelling.
        if "scater" in raw_ocr:
            gambling_hits.add(
                "scatter"
            )

        if gambling_hits or promotional_hits:
            sources.append(
                "ocr"
            )

    # --------------------------------------------------------
    # PAYMENT
    # --------------------------------------------------------

    if payment:

        if payment.get(
            "detected",
            False
        ):
            sources.append(
                "payment"
            )

    # --------------------------------------------------------
    # ENTITY
    # --------------------------------------------------------

    if entities:

        if (
            entities.get("payment_indicator")
            or
            entities.get("threat_indicator")
            or
            entities.get("url")
            or
            entities.get("domain")
        ):
            sources.append(
                "entity"
            )

    # --------------------------------------------------------
    # VISUAL
    # --------------------------------------------------------

    if visual:

        if visual.get(
            "visual_score",
            0
        ) >= 0.40:

            sources.append(
                "visual"
            )

    return {
        "gambling_hits": sorted(
            x for x in gambling_hits
            if x
        ),
        "promotional_hits": sorted(
            x for x in promotional_hits
            if x
        ),
        "sources": sorted(
            set(sources)
        )
    }


# ============================================================
# ADAPTIVE WEIGHTS
# ============================================================

def calculate_adaptive_weights(
    reliabilities
):

    # IMPORTANT:
    # Payment gets a high priority ONLY when payment evidence
    # actually exists.
    #
    # Otherwise it receives zero weight instead of diluting
    # text/OCR evidence.

    base_weights = {

        "text": 0.45,

        "ocr": 0.25,

        "visual": 0.10,

        "payment": 0.15,

        "entity": 0.05

    }

    adjusted = {}

    for modality, base in base_weights.items():

        reliability = clamp(
            reliabilities.get(
                modality,
                0
            )
        )

        if reliability <= 0:

            adjusted[
                modality
            ] = 0.0

        else:

            adjusted[
                modality
            ] = (

                base
                *
                (
                    0.20
                    +
                    0.80 * reliability
                )

            )

    total = sum(
        adjusted.values()
    )

    if total <= 0:

        return {
            key: 0.0
            for key in base_weights
        }

    return {

        key:
            value / total

        for key, value
        in adjusted.items()

    }


# ============================================================
# CLASSIFICATION
# ============================================================

def classify_risk(
    risk_score,
    text_label=None,
    evidence=None
):

    risk_score = clamp(
        risk_score
    )

    if risk_score >= 0.75:

        label = "C2"

    elif risk_score >= 0.40:

        label = "C1"

    else:

        label = "C0"

    evidence = evidence or {}

    gambling_hits = safe_list(
        evidence.get(
            "gambling_hits"
        )
    )

    promotional_hits = safe_list(
        evidence.get(
            "promotional_hits"
        )
    )

    sources = safe_list(
        evidence.get(
            "sources"
        )
    )

    # --------------------------------------------------------
    # MULTIMODAL SAFETY RULE
    # --------------------------------------------------------
    #
    # If gambling evidence is independently detected in
    # text + OCR, do not classify it as C0.
    # --------------------------------------------------------

    if (
        len(gambling_hits) >= 1
        and
        "text" in sources
        and
        "ocr" in sources
        and
        risk_score >= 0.32
    ):

        if label == "C0":
            label = "C1"

    # --------------------------------------------------------
    # Strong gambling + promotion
    # --------------------------------------------------------

    if (
        len(gambling_hits) >= 1
        and
        len(promotional_hits) >= 1
        and
        len(sources) >= 2
        and
        risk_score >= 0.50
    ):

        if label == "C0":
            label = "C1"

    # --------------------------------------------------------
    # Strong text classifier result
    # --------------------------------------------------------

    if (
        text_label == "C2"
        and
        risk_score >= 0.50
    ):

        label = "C2"

    return label


# ============================================================
# EXPLAINABLE AI
# ============================================================

def build_explanation(
    classification,
    risk_score,
    confidence,
    evidence
):
    """
    Build a human-readable explanation from GuardNet-AI
    multimodal evidence.

    This function does not change the fusion score.
    It only explains the result.
    """

    evidence = evidence or {}

    cross_modal = evidence.get(
        "cross_modal",
        {}
    )

    if not isinstance(cross_modal, dict):
        cross_modal = {}

    gambling_hits = safe_list(
        cross_modal.get(
            "gambling_hits",
            []
        )
    )

    promotional_hits = safe_list(
        cross_modal.get(
            "promotional_hits",
            []
        )
    )

    evidence_sources = safe_list(
        cross_modal.get(
            "evidence_sources",
            []
        )
    )

    gambling_hits = list(
        dict.fromkeys(
            str(item).strip()
            for item in gambling_hits
            if str(item).strip()
        )
    )

    promotional_hits = list(
        dict.fromkeys(
            str(item).strip()
            for item in promotional_hits
            if str(item).strip()
        )
    )

    evidence_sources = list(
        dict.fromkeys(
            str(item).strip().lower()
            for item in evidence_sources
            if str(item).strip()
        )
    )

    source_labels = {
        "text": "Text Classification",
        "ocr": "OCR",
        "visual": "Visual Analysis",
        "payment": "Payment Detection",
        "entity": "Entity Extraction",
        "qris": "QRIS Detection",
        "graph": "Threat Graph",
        "cyber_intelligence": "Cyber Intelligence"
    }

    readable_sources = [
        source_labels.get(
            source,
            source
        )
        for source in evidence_sources
    ]

    classification = str(
        classification
    ).upper()

    if classification == "C2":
        risk_level = "HIGH"
        summary = (
            "Konten memiliki indikasi kuat terkait "
            "aktivitas atau promosi perjudian online."
        )

    elif classification == "C1":
        risk_level = "MEDIUM"
        summary = (
            "Konten memiliki indikator mencurigakan "
            "yang memerlukan pemeriksaan lebih lanjut."
        )

    else:
        risk_level = "LOW"
        summary = (
            "Tidak ditemukan indikator kuat aktivitas "
            "atau promosi perjudian online."
        )

    reasons = []

    if gambling_hits:
        reasons.append(
            "Indikator perjudian terdeteksi: "
            + ", ".join(gambling_hits)
            + "."
        )

    if promotional_hits:
        reasons.append(
            "Pola promosi mencurigakan terdeteksi: "
            + ", ".join(promotional_hits)
            + "."
        )

    if (
        "text" in evidence_sources
        and
        "ocr" in evidence_sources
    ):
        reasons.append(
            "Bukti perjudian terdeteksi secara konsisten "
            "pada Text Classification dan OCR."
        )

    if len(evidence_sources) >= 2:
        reasons.append(
            "Sistem menggunakan bukti multimodal dari "
            + ", ".join(readable_sources)
            + "."
        )

    if not reasons:
        reasons.append(
            "Tidak terdapat evidence kuat yang mendukung "
            "indikasi perjudian pada modalitas yang aktif."
        )

    try:
        confidence_percent = round(
            clamp(confidence) * 100,
            1
        )
    except (
        TypeError,
        ValueError
    ):
        confidence_percent = 0.0

    return {
        "summary": summary,
        "risk_level": risk_level,
        "classification": classification,
        "risk_score": round(
            clamp(risk_score),
            3
        ),
        "confidence_percent": confidence_percent,
        "reasons": reasons,
        "evidence_sources": readable_sources,
        "evidence_count": (
            len(gambling_hits)
            +
            len(promotional_hits)
        ),
        "multimodal": (
            len(evidence_sources) >= 2
        )
    }


# ============================================================
# MAIN FUSION
# ============================================================

def fusion_score(
    text,
    payment,
    entities,
    visual=None,
    ocr=None
):

    # ========================================================
    # 1. MODALITY SCORES
    # ========================================================

    text_score = get_text_score(
        text
    )

    ocr_score = get_ocr_score(
        ocr
    )

    visual_score = get_visual_score(
        visual
    )

    payment_score = get_payment_score(
        payment
    )

    entity_score = get_entity_score(
        entities
    )

    # ========================================================
    # 2. RELIABILITY
    # ========================================================

    reliability = {

        "text": round(
            get_text_reliability(
                text
            ),
            3
        ),

        "ocr": round(
            get_ocr_reliability(
                ocr
            ),
            3
        ),

        "visual": round(
            get_visual_reliability(
                visual
            ),
            3
        ),

        "payment": round(
            get_payment_reliability(
                payment
            ),
            3
        ),

        "entity": round(
            get_entity_reliability(
                entities
            ),
            3
        )

    }

    # ========================================================
    # 3. ADAPTIVE WEIGHTS
    # ========================================================

    weights = calculate_adaptive_weights(
        reliability
    )

    weights = {
        key:
            round(
                value,
                3
            )

        for key, value
        in weights.items()
    }

    # ========================================================
    # 4. BASE WEIGHTED FUSION
    # ========================================================

    active_modalities = []

    if reliability["text"] > 0:
        active_modalities.append(
            "text"
        )

    if reliability["ocr"] > 0:
        active_modalities.append(
            "ocr"
        )

    if reliability["visual"] > 0:
        active_modalities.append(
            "visual"
        )

    if reliability["payment"] > 0:
        active_modalities.append(
            "payment"
        )

    if reliability["entity"] > 0:
        active_modalities.append(
            "entity"
        )

    risk_score = (

        text_score
        *
        weights["text"]

        +

        ocr_score
        *
        weights["ocr"]

        +

        visual_score
        *
        weights["visual"]

        +

        payment_score
        *
        weights["payment"]

        +

        entity_score
        *
        weights["entity"]

    )

    risk_score = clamp(
        risk_score
    )

    # ========================================================
    # 5. CROSS-MODAL EVIDENCE
    # ========================================================

    cross_modal = extract_cross_modal_evidence(
        text,
        ocr,
        payment,
        entities,
        visual
    )

    gambling_hits = cross_modal[
        "gambling_hits"
    ]

    promotional_hits = cross_modal[
        "promotional_hits"
    ]

    evidence_sources = cross_modal[
        "sources"
    ]

    # ========================================================
    # 6. EVIDENCE AGREEMENT BOOST
    # ========================================================

    evidence_boost = 0.0

    # Text + OCR agreement.
    if (
        "text" in evidence_sources
        and
        "ocr" in evidence_sources
    ):

        evidence_boost += 0.10

    # Gambling + promotional evidence.
    if (
        gambling_hits
        and
        promotional_hits
    ):

        evidence_boost += 0.08

    # Payment evidence.
    if (
        payment_score >= 0.25
    ):

        evidence_boost += 0.08

    # Entity evidence.
    if (
        entity_score >= 0.20
    ):

        evidence_boost += 0.05

    # Maximum bounded boost.
    evidence_boost = min(
        evidence_boost,
        0.20
    )

    risk_score += evidence_boost

    risk_score = clamp(
        risk_score
    )

    # ========================================================
    # 7. STRONG TEXT PROTECTION
    # ========================================================

    text_label = None

    if text:

        text_label = text.get(
            "label"
        )

        if text_label is None:

            text_label = text.get(
                "classification"
            )

    # If text is clearly C2 and there is reasonable evidence,
    # don't let fusion downgrade it excessively.
    if (
        text_label == "C2"
        and
        text_score >= 0.70
        and
        risk_score >= 0.50
    ):

        risk_score = max(
            risk_score,
            0.70
        )

    # ========================================================
    # 8. FINAL CLASSIFICATION
    # ========================================================

    classification = classify_risk(
        risk_score,
        text_label,
        cross_modal
    )

    # ========================================================
    # 9. CONFIDENCE
    # ========================================================

    if active_modalities:

        weighted_reliability = sum(

            reliability[key]
            *
            weights[key]

            for key in weights

        )

        modality_agreement = (
            len(active_modalities)
            /
            5.0
        )

        evidence_agreement = min(
            len(evidence_sources)
            /
            4.0,
            1.0
        )

        confidence = (

            weighted_reliability
            * 0.55

            +

            modality_agreement
            * 0.20

            +

            evidence_agreement
            * 0.25

        )

    else:

        confidence = 0.0

    confidence = clamp(
        confidence
    )

    # ========================================================
    # 10. EVIDENCE SUMMARY
    # ========================================================

    evidence = {

        "text": {

            "score":
                round(
                    text_score,
                    3
                ),

            "label":
                text_label,

            "reliability":
                reliability["text"],

            "weight":
                weights["text"]

        },

        "ocr": {

            "score":
                round(
                    ocr_score,
                    3
                ),

            "gambling_terms":
                safe_list(
                    ocr.get(
                        "gambling_terms"
                    )
                    if ocr
                    else []
                ),

            "promotional_terms":
                safe_list(
                    ocr.get(
                        "promotional_terms"
                    )
                    if ocr
                    else []
                ),

            "reliability":
                reliability["ocr"],

            "weight":
                weights["ocr"]

        },

        "visual": {

            "score":
                round(
                    visual_score,
                    3
                ),

            "evidence":
                safe_list(
                    visual.get(
                        "evidence"
                    )
                    if visual
                    else []
                ),

            "reliability":
                reliability["visual"],

            "weight":
                weights["visual"]

        },

        "payment": {

            "score":
                round(
                    payment_score,
                    3
                ),

            "evidence":
                safe_list(
                    payment.get(
                        "evidence"
                    )
                    if payment
                    else []
                ),

            "reliability":
                reliability["payment"],

            "weight":
                weights["payment"]

        },

        "entity": {

            "score":
                round(
                    entity_score,
                    3
                ),

            "reliability":
                reliability["entity"],

            "weight":
                weights["entity"]

        },

        "cross_modal": {

            "gambling_hits":
                gambling_hits,

            "promotional_hits":
                promotional_hits,

            "evidence_sources":
                evidence_sources,

            "evidence_boost":
                round(
                    evidence_boost,
                    3
                )

        }

    }

    # ========================================================
    # 11. EXPLAINABLE AI
    # ========================================================

    explanation = build_explanation(
        classification=classification,
        risk_score=risk_score,
        confidence=confidence,
        evidence=evidence
    )

    # ========================================================
    # 12. FINAL RESPONSE
    # ========================================================

    return {

        "classification":
            classification,

        "risk_score":
            round(
                risk_score,
                3
            ),

        "confidence":
            round(
                confidence,
                3
            ),

        "active_modalities":
            len(
                active_modalities
            ),

        "active_modality_names":
            active_modalities,

        "reliability":
            reliability,

        "adaptive_weights":
            weights,

        "evidence":
            evidence,

        "explanation":
            explanation,

        "status":
            "success"

    }