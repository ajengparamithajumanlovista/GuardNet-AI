from app.fusion.engine import fusion_score


# ============================================================
# TEST GUARDNET-AI MULTIMODAL FUSION
# ============================================================


# ============================================================
# TEXT CLASSIFICATION
# ============================================================

text = {

    "label":
        "C2",

    "score":
        0.85,

    "probabilities": {

        "C0":
            0.045,

        "C1":
            0.105,

        "C2":
            0.85

    },

    "status":
        "success",

    "evidence": {

        "gambling_terms": [

            "slot",
            "gacor"

        ],

        "promotional_terms": [

            "daftar",
            "bonus"

        ]

    }

}


# ============================================================
# OCR
# ============================================================

ocr = {

    "text":
        "SLOTGACOR 2026\nDEPOSITOQRIS\nBONUS MEMBER BARU\nDAFTAR SEKARANG",

    "confidence":
        0.886,

    "quality":
        0.92,

    "gambling_terms": [

        "slot",
        "gacor"

    ],

    "promotional_terms": [

        "daftar",
        "bonus",
        "deposit"

    ],

    "status":
        "success"

}


# ============================================================
# VISUAL
# ============================================================

visual = {

    "visual_score":
        0.173,

    "width":
        1000,

    "height":
        500,

    "contrast":
        9.338,

    "evidence": [

        "bright_visual"

    ],

    "status":
        "success"

}


# ============================================================
# PAYMENT
# ============================================================

payment = {

    "detected":
        True,

    "evidence": [

        "qris"

    ],

    "status":
        "success"

}


# ============================================================
# ENTITY / DIGITAL INTELLIGENCE
# ============================================================

entities = {

    "account": [

        "@contohslot"

    ],

    "phone": [

        "081234567890"

    ],

    "url": [

        "https://contoh.com"

    ],

    "domain": [

        "contoh.com"

    ],

    "payment_indicator": [

        "qris"

    ],

    "threat_indicator": [

        "slot",
        "gacor"

    ]

}


# ============================================================
# RUN FUSION
# ============================================================

result = fusion_score(

    text=text,

    payment=payment,

    entities=entities,

    visual=visual,

    ocr=ocr

)


# ============================================================
# DISPLAY RESULT
# ============================================================

print()
print("==============================================")
print(" GUARDNET-AI MULTIMODAL FUSION TEST")
print("==============================================")

print()

print("Classification:")
print(
    result.get(
        "classification"
    )
)

print()

print("Risk Score:")
print(
    result.get(
        "risk_score"
    )
)

print()

print("Confidence:")
print(
    result.get(
        "confidence"
    )
)

print()

print("Active Modalities:")
print(
    result.get(
        "active_modalities"
    )
)

print()

print("Reliability:")
print(
    result.get(
        "reliability"
    )
)

print()

print("Adaptive Weights:")
print(
    result.get(
        "adaptive_weights"
    )
)

print()

print("Evidence:")
print(
    result.get(
        "evidence"
    )
)

print()

print("Status:")
print(
    result.get(
        "status"
    )
)

print()
print("==============================================")