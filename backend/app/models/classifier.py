# ============================================================
# GUARDNET-AI
# CONTEXT-AWARE TEXT CLASSIFIER
# Research Publication Edition
# ============================================================

import re


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):

    if text is None:
        return ""

    text = str(text).lower()

    replacements = {
        "0": "o",
        "1": "i",
        "3": "e",
        "4": "a",
        "5": "s",
        "7": "t",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    typo_replacements = {
        "scater": "scatter",
        "scattar": "scatter",
        "gacorr": "gacor",
        "gaccor": "gacor",
        "judi0nline": "judi online",
    }

    for old, new in typo_replacements.items():
        text = text.replace(old, new)

    text = re.sub(
        r"[^\w\s@./:+-]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# ============================================================
# KEYWORD GROUPS
# ============================================================

GAMBLING_TERMS = [

    "slot",
    "slots",
    "gacor",
    "jackpot",
    "maxwin",
    "max win",

    "judi",
    "judi online",
    "perjudian",

    "casino",
    "kasino",

    "bet",
    "betting",
    "taruhan",

    "scatter",
    "free spin",
    "freespin",

    "spin",
    "turnover",

    "deposit",
    "withdraw",
    "withdrawal",

    "qris",

]


PROMOTIONAL_TERMS = [

    "bonus",
    "promo",
    "promosi",

    "member",
    "member baru",
    "new member",

    "daftar",
    "daftar sekarang",
    "register",

    "klik",
    "klik link",
    "link",
    "link alternatif",
    "link di bio",

    "admin",

    "hadiah",
    "hadiah besar",

    "menang",
    "menang besar",
    "gampang menang",
    "mudah menang",
    "kemenangan",

    "spill",
    "spill link",

    "coba",
    "mau coba",

]


# ============================================================
# STRONG GAMBLING / PROMOTIONAL PHRASES
# ============================================================

STRONG_PROMOTIONAL_PHRASES = [

    "slot gacor",
    "slot gacor hari ini",

    "jackpot besar",
    "bonus besar",

    "bonus new member",
    "bonus member baru",

    "daftar sekarang",
    "deposit sekarang",

    "deposit qris",
    "qris untuk",

    "klik link",
    "link di bio",

    "main slot",
    "main judi",

    "judi online sekarang",

    "gampang menang",
    "mudah menang",

    "menang besar",

    "gampang scatter",
    "gampang scater",

    "scatter bosku",

    "free spin",

]


# ============================================================
# GAMBLING CONTEXT COMBINATIONS
# ============================================================

SUSPICIOUS_COMBINATIONS = [

    (
        "situs",
        "menang"
    ),

    (
        "situs",
        "coba"
    ),

    (
        "situs",
        "link"
    ),

    (
        "situs",
        "spill"
    ),

    (
        "menang",
        "link"
    ),

    (
        "menang",
        "coba"
    ),

    (
        "menang",
        "spill"
    ),

    (
        "link",
        "coba"
    ),

]


STRONG_COMBINATIONS = [

    (
        "slot",
        "gacor"
    ),

    (
        "slot",
        "bonus"
    ),

    (
        "slot",
        "daftar"
    ),

    (
        "slot",
        "deposit"
    ),

    (
        "judi",
        "online"
    ),

    (
        "judi",
        "daftar"
    ),

    (
        "judi",
        "deposit"
    ),

    (
        "gacor",
        "bonus"
    ),

    (
        "scatter",
        "bonus"
    ),

    (
        "scatter",
        "deposit"
    ),

]


# ============================================================
# ANTI GAMBLING / INFORMATIONAL CONTEXT
# ============================================================

ANTI_GAMBLING_PHRASES = [

    "bahaya judi",
    "bahaya judi online",

    "hindari judi",
    "hindari judi online",

    "jangan percaya judi",
    "jangan percaya situs judi",

    "dilarang judi",
    "dilarang perjudian",

    "memberantas judi",
    "memberantas judi online",

    "pemberantasan judi",

    "penindakan judi",
    "penindakan terhadap judi",

    "polisi mengimbau",
    "pemerintah",

    "edukasi bahaya",

    "kerugian finansial",
    "kecanduan judi",

    "dampak judi",

]


NEGATIVE_CONTEXT = [

    "bahaya",
    "hindari",
    "jangan",
    "dilarang",
    "memberantas",
    "pemberantasan",
    "penindakan",
    "imbauan",
    "edukasi",
    "kerugian",
    "kecanduan",

]


# ============================================================
# CONTACT / ACTION EVIDENCE
# ============================================================

CONTACT_PATTERNS = [

    r"https?://",
    r"www\.",
    r"@\w+",
    r"\b08\d{8,13}\b",
    r"\+62\d{8,13}",

]


# ============================================================
# FIND TERMS
# ============================================================

def find_terms(text, terms):

    found = []

    for term in terms:

        if term in text:
            found.append(term)

    return list(
        dict.fromkeys(found)
    )


# ============================================================
# CONTACT DETECTION
# ============================================================

def detect_contact_evidence(text):

    evidence = []

    for pattern in CONTACT_PATTERNS:

        if re.search(
            pattern,
            text
        ):

            evidence.append(pattern)

    return evidence


# ============================================================
# COMBINATION DETECTION
# ============================================================

def detect_combinations(
    text,
    combinations
):

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
# PROBABILITY NORMALIZATION
# ============================================================

def normalize_probabilities(
    probabilities
):

    cleaned = {}

    for label in [
        "C0",
        "C1",
        "C2"
    ]:

        value = probabilities.get(
            label,
            0.0
        )

        try:
            value = float(value)
        except (
            TypeError,
            ValueError
        ):
            value = 0.0

        cleaned[label] = max(
            0.0,
            value
        )

    total = sum(
        cleaned.values()
    )

    if total <= 0:

        return {
            "C0": 1.0,
            "C1": 0.0,
            "C2": 0.0,
        }

    normalized = {

        label:
            value / total

        for label, value
        in cleaned.items()

    }

    # Round first.
    rounded = {

        label:
            round(
                value,
                3
            )

        for label, value
        in normalized.items()

    }

    # Correct rounding drift so total is exactly 1.000.
    difference = round(
        1.0
        -
        sum(
            rounded.values()
        ),
        3
    )

    if difference != 0:

        largest_label = max(
            rounded,
            key=rounded.get
        )

        rounded[
            largest_label
        ] = round(
            rounded[
                largest_label
            ]
            +
            difference,
            3
        )

    return rounded


# ============================================================
# CLASSIFIER
# ============================================================

def classify_text(text):

    normalized = normalize_text(
        text
    )

    # ========================================================
    # EVIDENCE
    # ========================================================

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
        STRONG_PROMOTIONAL_PHRASES
    )

    anti_gambling_phrases = find_terms(
        normalized,
        ANTI_GAMBLING_PHRASES
    )

    negative_context = find_terms(
        normalized,
        NEGATIVE_CONTEXT
    )

    contact_evidence = detect_contact_evidence(
        normalized
    )

    suspicious_combinations = detect_combinations(
        normalized,
        SUSPICIOUS_COMBINATIONS
    )

    strong_combinations = detect_combinations(
        normalized,
        STRONG_COMBINATIONS
    )

    # ========================================================
    # COUNTS
    # ========================================================

    gambling_count = len(
        gambling_terms
    )

    promotional_count = len(
        promotional_terms
    )

    strong_count = len(
        strong_promotional_phrases
    )

    anti_count = len(
        anti_gambling_phrases
    )

    suspicious_count = len(
        suspicious_combinations
    )

    strong_combination_count = len(
        strong_combinations
    )

    # ========================================================
    # ANTI-GAMBLING SCORE
    # ========================================================

    anti_score = 0.0

    if anti_count >= 1:
        anti_score += 0.35

    if anti_count >= 2:
        anti_score += 0.20

    if len(
        negative_context
    ) >= 2:
        anti_score += 0.15

    anti_score = min(
        anti_score,
        0.70
    )

    # ========================================================
    # GAMBLING RELEVANCE
    # ========================================================

    gambling_relevance = 0.0

    if gambling_count >= 1:
        gambling_relevance += 0.30

    if gambling_count >= 2:
        gambling_relevance += 0.20

    if gambling_count >= 3:
        gambling_relevance += 0.15

    if strong_combination_count >= 1:
        gambling_relevance += 0.15

    gambling_relevance = min(
        gambling_relevance,
        0.90
    )

    # ========================================================
    # PROMOTIONAL INTENT
    # ========================================================

    promotional_intent = 0.0

    if promotional_count >= 1:
        promotional_intent += 0.20

    if promotional_count >= 2:
        promotional_intent += 0.15

    if strong_count >= 1:
        promotional_intent += 0.25

    if strong_count >= 2:
        promotional_intent += 0.20

    if suspicious_count >= 1:
        promotional_intent += 0.10

    promotional_intent = min(
        promotional_intent,
        0.90
    )

    # ========================================================
    # CONTEXT FLAGS
    # ========================================================

    strong_gambling_context = (

        gambling_count >= 1
        and
        promotional_count >= 1

    )

    very_strong_context = (

        gambling_count >= 2

        and

        (
            promotional_count >= 2
            or
            strong_count >= 1
        )

    )

    suspicious_context = (

        suspicious_count >= 1
        and
        (
            promotional_count >= 1
            or
            contact_evidence
        )

    )

    # ========================================================
    # INITIAL SCORE
    # ========================================================

    score = 0.10

    # --------------------------------------------------------
    # Informational / anti-gambling
    # --------------------------------------------------------

    if anti_count >= 1:

        score = 0.10

        if gambling_count >= 1:
            score = 0.20

        if anti_count >= 2:
            score = 0.10

    # --------------------------------------------------------
    # Strong gambling context
    # --------------------------------------------------------

    if strong_gambling_context:

        score = max(
            score,
            0.70
        )

    if very_strong_context:

        score = max(
            score,
            0.85
        )

    # --------------------------------------------------------
    # Pure gambling indicators
    # --------------------------------------------------------

    if gambling_count >= 2:

        score = max(
            score,
            0.70
        )

    if gambling_count >= 3:

        score = max(
            score,
            0.80
        )

    # --------------------------------------------------------
    # Strong phrases
    # --------------------------------------------------------

    if strong_count >= 1:

        score = max(
            score,
            0.65
        )

    # --------------------------------------------------------
    # Suspicious context
    #
    # Example:
    # "situs baru katanya gampang menang"
    # + "spill link"
    # + "aku mau coba"
    #
    # This is NOT automatically C2.
    # It becomes C1 because context is suspicious
    # but gambling evidence is not explicit enough.
    # --------------------------------------------------------

    if suspicious_context:

        score = max(
            score,
            0.45
        )

    # --------------------------------------------------------
    # Strong suspicious combination
    # --------------------------------------------------------

    if (
        suspicious_count >= 2
        and
        promotional_count >= 1
    ):

        score = max(
            score,
            0.55
        )

    # --------------------------------------------------------
    # Payment-related gambling
    # --------------------------------------------------------

    payment_terms = [

        "deposit",
        "withdraw",
        "qris"

    ]

    payment_found = find_terms(
        normalized,
        payment_terms
    )

    if payment_found and (
        gambling_count >= 1
        or
        promotional_count >= 1
    ):

        score = max(
            score,
            0.75
        )

    # ========================================================
    # ANTI-GAMBLING OVERRIDE
    # ========================================================

    if (
        anti_count >= 1
        and
        not strong_gambling_context
        and
        not very_strong_context
    ):

        score = min(
            score,
            0.25
        )

    # ========================================================
    # LABEL
    # ========================================================

    if score >= 0.75:

        label = "C2"

    elif score >= 0.40:

        label = "C1"

    else:

        label = "C0"

    # ========================================================
    # REASONS
    # ========================================================

    reasons = []

    if gambling_count >= 1:
        reasons.append(
            "gambling_context"
        )

    if gambling_count >= 2:
        reasons.append(
            "multiple_gambling_terms"
        )

    if promotional_count >= 1:
        reasons.append(
            "promotional_language"
        )

    if promotional_count >= 2:
        reasons.append(
            "multiple_promotional_terms"
        )

    if strong_count >= 1:
        reasons.append(
            "strong_promotional_phrase"
        )

    if strong_count >= 2:
        reasons.append(
            "multiple_strong_promotional_phrases"
        )

    if suspicious_count >= 1:
        reasons.append(
            "suspicious_context_combination"
        )

    if strong_combination_count >= 1:
        reasons.append(
            "strong_gambling_combination"
        )

    if payment_found:
        reasons.append(
            "payment_context"
        )

    if anti_count >= 1:
        reasons.append(
            "anti_gambling_context"
        )

    if contact_evidence:
        reasons.append(
            "contact_evidence"
        )

    # ========================================================
    # PROBABILITY MODEL
    # ========================================================

    if label == "C2":

        probabilities = {

            "C0": max(
                0.01,
                (1.0 - score) * 0.20
            ),

            "C1": max(
                0.01,
                (1.0 - score) * 0.30
            ),

            "C2": score,

        }

    elif label == "C1":

        probabilities = {

            "C0": max(
                0.05,
                1.0 - score
            ),

            "C1": score,

            "C2": max(
                0.01,
                score * 0.15
            ),

        }

    else:

        probabilities = {

            "C0": max(
                0.80,
                1.0 - score
            ),

            "C1": max(
                0.01,
                score * 0.50
            ),

            "C2": 0.02,

        }

    probabilities = normalize_probabilities(
        probabilities
    )

    # ========================================================
    # FINAL
    # ========================================================

    return {

        "label":
            label,

        "score":
            round(
                score,
                3
            ),

        "probabilities":
            probabilities,

        "evidence": {

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
                reasons

        },

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

        "status":
            "success"

    }