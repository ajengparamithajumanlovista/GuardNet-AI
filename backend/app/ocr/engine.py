# ============================================================
# GUARDNET-AI
# OCR ENGINE
# FINAL GEMASTIK VERSION
#
# Fungsi utama:
# - menerima file path
# - menerima PIL.Image / JpegImageFile
# - menerima numpy.ndarray
# - preprocessing OCR
# - Tesseract OCR
# - normalisasi typo OCR
# - gambling evidence detection
# - promotional evidence detection
# - menghasilkan score + confidence + evidence
# ============================================================

from typing import Any, Dict, List, Tuple
import os
import re

# ------------------------------------------------------------
# OPTIONAL DEPENDENCIES
# ------------------------------------------------------------

try:
    import cv2
except Exception:
    cv2 = None

try:
    import numpy as np
except Exception:
    np = None

try:
    import pytesseract
except Exception:
    pytesseract = None


# ============================================================
# BASIC UTILITIES
# ============================================================

def clamp(
    value: Any,
    minimum: float = 0.0,
    maximum: float = 1.0
) -> float:

    try:
        value = float(value)
    except (TypeError, ValueError):
        return minimum

    return max(
        minimum,
        min(value, maximum)
    )


def safe_list(value: Any) -> List:

    if isinstance(value, list):
        return value

    if value is None:
        return []

    return [value]


def normalize_text(
    value: Any
) -> str:

    if value is None:
        return ""

    text = str(value).lower()

    # --------------------------------------------------------
    # OCR typo normalization
    # --------------------------------------------------------

    replacements = {

        # scatter
        "scater": "scatter",
        "scattter": "scatter",
        "scaterr": "scatter",

        # gambling
        "judii": "judi",
        "jud1": "judi",

        # slot
        "s1ot": "slot",

        # deposit
        "depos1t": "deposit",

        # jackpot
        "jackp0t": "jackpot",

        # gacor
        "gac0r": "gacor",

        # maxwin
        "maxw1n": "maxwin",

        # common OCR errors
        "spil link": "spill link",
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )

    # --------------------------------------------------------
    # Remove strange characters
    # --------------------------------------------------------

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
# VOCABULARY
# ============================================================

GAMBLING_TERMS = {

    "judi",
    "judi online",
    "judi slot",
    "perjudian",

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
    "free spin",
    "freespin",

    "deposit",
    "withdraw",
    "withdrawal",
    "wd",

    "maxwin",
    "max win",

    "bonus",

    "pragmatic",
    "zeus",
    "starlight",
    "mahjong",
}


PROMOTIONAL_TERMS = {

    "daftar",
    "daftar sekarang",

    "register",
    "registrasi",

    "bonus",
    "bonus besar",

    "bonus new member",
    "bonus member baru",

    "promo",
    "promosi",

    "gampang menang",
    "mudah menang",

    "menang",
    "menang besar",

    "maxwin",
    "jackpot",

    "deposit sekarang",
    "main sekarang",

    "buruan",

    "klik",
    "klik link",

    "link",
    "link di bio",

    "spill",
    "spill link",

    "coba",
    "mau coba",
}


STRONG_GAMBLING_PHRASES = {

    "judi online",
    "judi slot",

    "slot gacor",
    "slot gacor hari ini",

    "main slot",
    "main judi",

    "gampang menang",
    "mudah menang",

    "menang besar",

    "bonus besar",

    "deposit sekarang",
    "daftar sekarang",

    "klik link",
    "link di bio",

    "gampang scatter",
    "gampang scater",

    "scatter bosku",

    "free spin",

    "bonus new member",
    "bonus member baru",

    "tiap malem di kasi jatah",
}


STRONG_COMBINATIONS = [

    ("slot", "gacor"),
    ("slot", "bonus"),
    ("slot", "daftar"),
    ("slot", "deposit"),

    ("judi", "online"),
    ("judi", "daftar"),
    ("judi", "deposit"),

    ("gacor", "bonus"),

    ("scatter", "bonus"),
    ("scatter", "deposit"),
]


SUSPICIOUS_COMBINATIONS = [

    ("situs", "menang"),
    ("situs", "coba"),
    ("situs", "link"),
    ("situs", "spill"),

    ("menang", "link"),
    ("menang", "coba"),
    ("menang", "spill"),

    ("link", "coba"),
]


# ============================================================
# FIND TERMS
# ============================================================

def find_terms(
    text: str,
    terms
) -> List[str]:

    found = []

    if not text:
        return found

    for term in terms:

        if term in text:

            found.append(
                term
            )

    return list(
        dict.fromkeys(
            found
        )
    )


# ============================================================
# COMBINATION DETECTOR
# ============================================================

def find_combinations(
    text: str,
    combinations
) -> List[str]:

    found = []

    for first, second in combinations:

        if (
            first in text
            and
            second in text
        ):

            found.append(
                f"{first} + {second}"
            )

    return found


# ============================================================
# OCR TEXT CLASSIFICATION
# ============================================================

def classify_ocr_text(
    text: str
) -> Dict[str, Any]:

    normalized = normalize_text(
        text
    )

    gambling_terms = find_terms(
        normalized,
        GAMBLING_TERMS
    )

    promotional_terms = find_terms(
        normalized,
        PROMOTIONAL_TERMS
    )

    strong_promotional_phrases = find_terms(
        normalized,
        STRONG_GAMBLING_PHRASES
    )

    strong_combinations = find_combinations(
        normalized,
        STRONG_COMBINATIONS
    )

    suspicious_combinations = find_combinations(
        normalized,
        SUSPICIOUS_COMBINATIONS
    )

    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    gambling_relevance = 0.0

    promotional_intent = 0.0

    # Gambling evidence
    if gambling_terms:

        gambling_relevance += 0.30

    if len(gambling_terms) >= 2:

        gambling_relevance += 0.20

    if len(gambling_terms) >= 4:

        gambling_relevance += 0.15

    # Strong combinations
    if strong_combinations:

        gambling_relevance += 0.20

    # Promotional evidence
    if promotional_terms:

        promotional_intent += 0.20

    if len(promotional_terms) >= 2:

        promotional_intent += 0.15

    if strong_promotional_phrases:

        promotional_intent += 0.25

    if len(
        strong_promotional_phrases
    ) >= 2:

        promotional_intent += 0.10

    gambling_relevance = clamp(
        gambling_relevance
    )

    promotional_intent = clamp(
        promotional_intent
    )

    # --------------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------------

    score = max(
        gambling_relevance,
        promotional_intent
    )

    # Combined gambling + promotion
    if (
        gambling_relevance > 0
        and
        promotional_intent > 0
    ):

        score += 0.15

    # Strong combination
    if strong_combinations:

        score += 0.10

    # Strong phrase
    if strong_promotional_phrases:

        score += 0.10

    score = clamp(
        score
    )

    # --------------------------------------------------------
    # CLASSIFICATION
    # --------------------------------------------------------

    if score >= 0.75:

        label = "C2"

    elif score >= 0.40:

        label = "C1"

    else:

        label = "C0"

    # --------------------------------------------------------
    # REASONS
    # --------------------------------------------------------

    reasons = []

    if gambling_terms:

        reasons.append(
            "gambling_context"
        )

    if len(gambling_terms) >= 2:

        reasons.append(
            "multiple_gambling_terms"
        )

    if promotional_terms:

        reasons.append(
            "promotional_language"
        )

    if len(promotional_terms) >= 2:

        reasons.append(
            "multiple_promotional_terms"
        )

    if strong_promotional_phrases:

        reasons.append(
            "strong_promotional_phrase"
        )

    if len(
        strong_promotional_phrases
    ) >= 2:

        reasons.append(
            "multiple_strong_promotional_phrases"
        )

    if strong_combinations:

        reasons.append(
            "strong_gambling_combination"
        )

    if suspicious_combinations:

        reasons.append(
            "suspicious_context_combination"
        )

    if "deposit" in normalized:

        reasons.append(
            "payment_context"
        )

    # --------------------------------------------------------
    # CONTACT EVIDENCE
    # --------------------------------------------------------

    contact_evidence = []

    if (
        "http://" in normalized
        or
        "https://" in normalized
    ):

        contact_evidence.append(
            "url"
        )

    if (
        "link" in normalized
        or
        "link di bio" in normalized
    ):

        contact_evidence.append(
            "link"
        )

    # --------------------------------------------------------
    # NEGATIVE / SAFE CONTEXT
    # --------------------------------------------------------

    negative_context = []

    safe_phrases = [
        "jangan judi",
        "stop judi",
        "bahaya judi",
        "hindari judi",
        "anti judi",
        "judi berbahaya",
    ]

    for phrase in safe_phrases:

        if phrase in normalized:

            negative_context.append(
                phrase
            )

    # --------------------------------------------------------
    # Anti-gambling
    # --------------------------------------------------------

    anti_gambling_phrases = []

    for phrase in safe_phrases:

        if phrase in normalized:

            anti_gambling_phrases.append(
                phrase
            )

    # Safe context adjustment
    if anti_gambling_phrases:

        score = max(
            0.0,
            score - 0.30
        )

        if score < 0.40:

            label = "C0"

    return {

        "label":
            label,

        "score":
            round(
                score,
                3
            ),

        "gambling_terms":
            gambling_terms,

        "promotional_terms":
            promotional_terms,

        "strong_promotional_phrases":
            strong_promotional_phrases,

        "suspicious_combinations":
            suspicious_combinations,

        "strong_gambling_combinations":
            strong_combinations,

        "anti_gambling_phrases":
            anti_gambling_phrases,

        "negative_context":
            negative_context,

        "contact_evidence":
            contact_evidence,

        "reasons":
            reasons,

        "normalized_text":
            normalized,

        "gambling_relevance":
            round(
                gambling_relevance,
                3
            ),

        "promotional_intent":
            round(
                promotional_intent,
                3
            ),
    }


# ============================================================
# IMAGE INPUT CONVERSION
# ============================================================

def image_to_cv2(
    image_input
):

    if cv2 is None:

        raise RuntimeError(
            "OpenCV belum tersedia"
        )

    # --------------------------------------------------------
    # PIL.Image / JpegImageFile
    # --------------------------------------------------------

    if hasattr(
        image_input,
        "convert"
    ):

        pil_image = image_input.convert(
            "RGB"
        )

        if np is None:

            raise RuntimeError(
                "NumPy belum tersedia"
            )

        image = np.array(
            pil_image
        )

        image = cv2.cvtColor(
            image,
            cv2.COLOR_RGB2BGR
        )

        return image

    # --------------------------------------------------------
    # File path
    # --------------------------------------------------------

    if isinstance(
        image_input,
        (
            str,
            bytes,
            os.PathLike
        )
    ):

        path = os.fspath(
            image_input
        )

        if not os.path.exists(
            path
        ):

            raise FileNotFoundError(
                f"File tidak ditemukan: {path}"
            )

        image = cv2.imread(
            path
        )

        if image is None:

            raise ValueError(
                "Gambar gagal dibaca oleh OpenCV"
            )

        return image

    # --------------------------------------------------------
    # NumPy array
    # --------------------------------------------------------

    if np is not None:

        if isinstance(
            image_input,
            np.ndarray
        ):

            return image_input.copy()

    raise TypeError(
        "Input OCR harus berupa path, PIL.Image, "
        "atau numpy.ndarray"
    )


# ============================================================
# PREPROCESSING
# ============================================================

def preprocess_image(
    image
) -> List[Tuple[str, Any]]:

    variants = []

    if cv2 is None:

        return variants

    if image is None:

        return variants

    # --------------------------------------------------------
    # Grayscale
    # --------------------------------------------------------

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    variants.append(
        (
            "grayscale",
            gray
        )
    )

    # --------------------------------------------------------
    # CLAHE
    # --------------------------------------------------------

    try:

        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )

        clahe_image = clahe.apply(
            gray
        )

        variants.append(
            (
                "clahe",
                clahe_image
            )
        )

    except Exception:

        pass

    # --------------------------------------------------------
    # OTSU
    # --------------------------------------------------------

    try:

        _, otsu = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY
            +
            cv2.THRESH_OTSU
        )

        variants.append(
            (
                "otsu",
                otsu
            )
        )

    except Exception:

        pass

    # --------------------------------------------------------
    # ADAPTIVE THRESHOLD
    # --------------------------------------------------------

    try:

        adaptive = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            11
        )

        variants.append(
            (
                "adaptive",
                adaptive
            )
        )

    except Exception:

        pass

    # --------------------------------------------------------
    # UPSCALE
    # --------------------------------------------------------

    try:

        height, width = gray.shape[:2]

        if width < 1600:

            scale = 2.0

            upscaled = cv2.resize(
                gray,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_CUBIC
            )

            variants.append(
                (
                    "upscaled",
                    upscaled
                )
            )

    except Exception:

        pass

    return variants


# ============================================================
# TESSERACT OCR
# ============================================================

def tesseract_extract(
    image
) -> str:

    if pytesseract is None:

        raise RuntimeError(
            "pytesseract belum tersedia"
        )

    # --------------------------------------------------------
    # OCR configuration
    # --------------------------------------------------------

    configs = [

        "--psm 6",

        "--psm 11",

        "--psm 12",

    ]

    best_text = ""

    best_length = 0

    for config in configs:

        try:

            text = pytesseract.image_to_string(
                image,
                config=config
            )

            if text is None:

                continue

            text = str(
                text
            ).strip()

            # Prefer text with useful length
            if len(text) > best_length:

                best_text = text

                best_length = len(text)

        except Exception:

            continue

    return best_text


# ============================================================
# OCR SCORE
# ============================================================

def get_ocr_score(
    result: Dict[str, Any]
) -> float:

    if not result:

        return 0.0

    score = result.get(
        "score",
        0.0
    )

    return clamp(
        score
    )


# ============================================================
# OCR RELIABILITY
# ============================================================

def get_ocr_reliability(
    result: Dict[str, Any]
) -> float:

    if not result:

        return 0.0

    if result.get(
        "status"
    ) != "success":

        return 0.0

    confidence = clamp(
        result.get(
            "confidence",
            0.0
        )
    )

    quality = clamp(
        result.get(
            "quality",
            0.0
        )
    )

    text = result.get(
        "text",
        ""
    )

    if not text:

        return 0.0

    reliability = (
        confidence * 0.60
        +
        quality * 0.40
    )

    return round(
        clamp(
            reliability
        ),
        3
    )


# ============================================================
# MAIN OCR
# ============================================================

def run_ocr(
    image_input
) -> Dict[str, Any]:

    result = {

        "text": "",

        "raw_text": "",

        "normalized_text": "",

        "classification": {

            "label": "C0",

            "score": 0.0,

            "probabilities": {

                "C0": 1.0,

                "C1": 0.0,

                "C2": 0.0,
            },
        },

        "score": 0.0,

        "label": "C0",

        "confidence": 0.0,

        "quality": 0.0,

        "gambling_terms": [],

        "promotional_terms": [],

        "strong_promotional_phrases": [],

        "suspicious_combinations": [],

        "strong_gambling_combinations": [],

        "anti_gambling_phrases": [],

        "negative_context": [],

        "contact_evidence": [],

        "gambling_relevance": 0.0,

        "promotional_intent": 0.0,

        "preprocessing": None,

        "variants_tested": 0,

        "status": "success",
    }

    # --------------------------------------------------------
    # Dependency check
    # --------------------------------------------------------

    if cv2 is None:

        result["status"] = "failed"

        result["error"] = (
            "OpenCV tidak tersedia"
        )

        return result

    if pytesseract is None:

        result["status"] = "failed"

        result["error"] = (
            "pytesseract tidak tersedia"
        )

        return result

    # --------------------------------------------------------
    # Convert input
    # --------------------------------------------------------

    try:

        image = image_to_cv2(
            image_input
        )

    except Exception as e:

        result["status"] = "failed"

        result["error"] = str(e)

        return result

    # --------------------------------------------------------
    # Generate variants
    # --------------------------------------------------------

    try:

        variants = preprocess_image(
            image
        )

    except Exception as e:

        result["status"] = "failed"

        result["error"] = (
            "Preprocessing gagal: "
            +
            str(e)
        )

        return result

    result[
        "variants_tested"
    ] = len(
        variants
    )

    # --------------------------------------------------------
    # Candidate OCR results
    # --------------------------------------------------------

    candidates = []

    # Original
    try:

        original_text = tesseract_extract(
            image
        )

        candidates.append(
            (
                "original",
                original_text
            )
        )

    except Exception:

        pass

    # Preprocessed
    for (
        variant_name,
        variant_image
    ) in variants:

        try:

            text = tesseract_extract(
                variant_image
            )

            candidates.append(
                (
                    variant_name,
                    text
                )
            )

        except Exception:

            continue

    # --------------------------------------------------------
    # Select best candidate
    #
    # Prioritize:
    # 1. gambling evidence
    # 2. promotional evidence
    # 3. text quality
    # --------------------------------------------------------

    best = None

    best_score = -1.0

    for (
        variant_name,
        text
    ) in candidates:

        if not text:

            continue

        evidence = classify_ocr_text(
            text
        )

        normalized = evidence[
            "normalized_text"
        ]

        evidence_score = (
            evidence["score"]
        )

        gambling_bonus = min(
            len(
                evidence[
                    "gambling_terms"
                ]
            )
            * 0.15,
            0.45
        )

        phrase_bonus = min(
            len(
                evidence[
                    "strong_promotional_phrases"
                ]
            )
            * 0.10,
            0.30
        )

        length_bonus = min(
            len(normalized)
            /
            1000.0,
            0.15
        )

        total_score = (
            evidence_score
            +
            gambling_bonus
            +
            phrase_bonus
            +
            length_bonus
        )

        if total_score > best_score:

            best_score = total_score

            best = {

                "variant":
                    variant_name,

                "text":
                    text,

                "evidence":
                    evidence,
            }

    # --------------------------------------------------------
    # No OCR text
    # --------------------------------------------------------

    if best is None:

        result["status"] = "success"

        result["preprocessing"] = None

        return result

    # --------------------------------------------------------
    # Extract selected evidence
    # --------------------------------------------------------

    text = best[
        "text"
    ].strip()

    evidence = best[
        "evidence"
    ]

    normalized = evidence[
        "normalized_text"
    ]

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence = 0.0

    text_length = len(
        normalized
    )

    if text_length >= 300:

        confidence += 0.45

    elif text_length >= 150:

        confidence += 0.40

    elif text_length >= 80:

        confidence += 0.35

    elif text_length >= 40:

        confidence += 0.25

    elif text_length >= 10:

        confidence += 0.15

    if evidence[
        "gambling_terms"
    ]:

        confidence += 0.20

    if evidence[
        "promotional_terms"
    ]:

        confidence += 0.10

    if evidence[
        "strong_promotional_phrases"
    ]:

        confidence += 0.15

    confidence = clamp(
        confidence
    )

    # --------------------------------------------------------
    # Quality
    # --------------------------------------------------------

    quality = 0.0

    if text_length >= 300:

        quality = 0.90

    elif text_length >= 150:

        quality = 0.80

    elif text_length >= 80:

        quality = 0.70

    elif text_length >= 40:

        quality = 0.60

    elif text_length >= 10:

        quality = 0.40

    elif text_length > 0:

        quality = 0.20

    # --------------------------------------------------------
    # Classification probabilities
    # --------------------------------------------------------

    score = clamp(
        evidence["score"]
    )

    if evidence[
        "label"
    ] == "C2":

        probabilities = {

            "C0": round(
                max(
                    0.01,
                    1.0 - score - 0.05
                ),
                3
            ),

            "C1": round(
                min(
                    0.25,
                    score * 0.30
                ),
                3
            ),

            "C2": round(
                max(
                    0.0,
                    score
                ),
                3
            ),
        }

    elif evidence[
        "label"
    ] == "C1":

        probabilities = {

            "C0": round(
                max(
                    0.05,
                    1.0 - score
                ),
                3
            ),

            "C1": round(
                max(
                    0.05,
                    score
                ),
                3
            ),

            "C2": 0.05,
        }

    else:

        probabilities = {

            "C0": round(
                max(
                    0.05,
                    1.0 - score
                ),
                3
            ),

            "C1": round(
                min(
                    0.20,
                    score
                ),
                3
            ),

            "C2": 0.02,
        }

    result.update({

        "text":
            text,

        "raw_text":
            text,

        "normalized_text":
            normalized,

        "classification": {

            "label":
                evidence[
                    "label"
                ],

            "score":
                round(
                    score,
                    3
                ),

            "probabilities":
                probabilities,
        },

        "score":
            round(
                score,
                3
            ),

        "label":
            evidence[
                "label"
            ],

        "confidence":
            round(
                confidence,
                3
            ),

        "quality":
            round(
                quality,
                3
            ),

        "gambling_terms":
            evidence[
                "gambling_terms"
            ],

        "promotional_terms":
            evidence[
                "promotional_terms"
            ],

        "strong_promotional_phrases":
            evidence[
                "strong_promotional_phrases"
            ],

        "suspicious_combinations":
            evidence[
                "suspicious_combinations"
            ],

        "strong_gambling_combinations":
            evidence[
                "strong_gambling_combinations"
            ],

        "anti_gambling_phrases":
            evidence[
                "anti_gambling_phrases"
            ],

        "negative_context":
            evidence[
                "negative_context"
            ],

        "contact_evidence":
            evidence[
                "contact_evidence"
            ],

        "gambling_relevance":
            evidence[
                "gambling_relevance"
            ],

        "promotional_intent":
            evidence[
                "promotional_intent"
            ],

        "preprocessing":
            best[
                "variant"
            ],

        "status":
            "success",
    })

    return result


# ============================================================
# COMPATIBILITY HELPERS
# ============================================================

def get_text_score(
    result: Dict[str, Any]
) -> float:

    if not result:

        return 0.0

    return clamp(
        result.get(
            "score",
            0.0
        )
    )


def get_text_reliability(
    result: Dict[str, Any]
) -> float:

    if not result:

        return 0.0

    text = result.get(
        "text",
        ""
    )

    if not text:

        return 0.0

    return get_ocr_reliability(
        result
    )


def get_visual_score(
    result: Dict[str, Any]
) -> float:

    if not result:

        return 0.0

    return clamp(
        result.get(
            "visual_score",
            result.get(
                "score",
                0.0
            )
        )
    )


def get_visual_reliability(
    result: Dict[str, Any]
) -> float:

    if not result:

        return 0.0

    if result.get(
        "status"
    ) != "success":

        return 0.0

    return 1.0


def get_payment_score(
    result: Dict[str, Any]
) -> float:

    if not result:

        return 0.0

    if result.get(
        "detected",
        False
    ):

        return clamp(
            result.get(
                "risk",
                0.5
            )
        )

    return 0.0


def get_payment_reliability(
    result: Dict[str, Any]
) -> float:

    if not result:

        return 0.0

    if result.get(
        "detected",
        False
    ):

        return 1.0

    return 0.0


def get_entity_score(
    result: Dict[str, Any]
) -> float:

    if not result:

        return 0.0

    count = result.get(
        "entity_count",
        0
    )

    try:

        count = int(
            count
        )

    except Exception:

        count = 0

    return clamp(
        count / 5.0
    )


def get_entity_reliability(
    result: Dict[str, Any]
) -> float:

    if not result:

        return 0.0

    count = result.get(
        "entity_count",
        0
    )

    try:

        count = int(
            count
        )

    except Exception:

        count = 0

    if count <= 0:

        return 0.2

    return clamp(
        0.2
        +
        min(
            count * 0.15,
            0.8
        )
    )


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

OCR_AVAILABLE = (
    cv2 is not None
    and
    pytesseract is not None
)


__all__ = [

    "run_ocr",

    "get_ocr_score",

    "get_ocr_reliability",

    "get_text_score",

    "get_text_reliability",

    "get_visual_score",

    "get_visual_reliability",

    "get_payment_score",

    "get_payment_reliability",

    "get_entity_score",

    "get_entity_reliability",

    "classify_ocr_text",

    "normalize_text",

    "OCR_AVAILABLE",
]