from app.graph.correlation import compare_cases
from app.graph.correlation import analyze_cross_content


# ============================================================
# CASE A
# ============================================================

case_a = {

    "case_id":
        "CASE-A",

    "payment": {

        "evidence": [
            "qris"
        ]

    },

    "qris": {

        "detected":
            False

    },

    "digital_intelligence": {

        "account": [],

        "domain": [],

        "url": [],

        "contact": []

    }

}


# ============================================================
# CASE B
# ============================================================

case_b = {

    "case_id":
        "CASE-B",

    "payment": {

        "evidence": [
            "qris"
        ]

    },

    "qris": {

        "detected":
            False

    },

    "digital_intelligence": {

        "account": [],

        "domain": [],

        "url": [],

        "contact": []

    }

}


# ============================================================
# CASE C
# ============================================================

case_c = {

    "case_id":
        "CASE-C",

    "payment": {

        "evidence": [
            "qris"
        ]

    },

    "digital_intelligence": {

        "account": [
            "@slotcontoh"
        ],

        "domain": [
            "slotcontoh.com"
        ],

        "url": [],

        "contact": []

    }

}


# ============================================================
# TEST 1
# QRIS ONLY
# ============================================================

result_1 = compare_cases(
    case_a,
    case_b
)


print()
print("==============================================")
print(" TEST 1 - QRIS ONLY")
print("==============================================")

print(
    "Correlation Level:",
    result_1.get(
        "correlation_level"
    )
)

print(
    "Shared Indicators:",
    result_1.get(
        "shared_indicators"
    )
)

print(
    "Shared Indicator Count:",
    result_1.get(
        "shared_indicator_count"
    )
)

print(
    "Strong Indicator Count:",
    result_1.get(
        "strong_indicator_count"
    )
)


# ============================================================
# TEST 2
# ACCOUNT + DOMAIN + QRIS
# ============================================================

case_d = {

    "case_id":
        "CASE-D",

    "payment": {

        "evidence": [
            "qris"
        ]

    },

    "digital_intelligence": {

        "account": [
            "@slotcontoh"
        ],

        "domain": [
            "slotcontoh.com"
        ],

        "url": [],

        "contact": []

    }

}


result_2 = compare_cases(
    case_c,
    case_d
)


print()
print("==============================================")
print(" TEST 2 - ACCOUNT + DOMAIN + QRIS")
print("==============================================")

print(
    "Correlation Level:",
    result_2.get(
        "correlation_level"
    )
)

print(
    "Shared Indicators:",
    result_2.get(
        "shared_indicators"
    )
)

print(
    "Shared Indicator Count:",
    result_2.get(
        "shared_indicator_count"
    )
)

print(
    "Strong Indicator Count:",
    result_2.get(
        "strong_indicator_count"
    )
)


# ============================================================
# TEST 3
# CROSS CONTENT
# ============================================================

result_3 = analyze_cross_content(

    case_c,

    [
        case_a,
        case_b,
        case_d
    ]

)


print()
print("==============================================")
print(" TEST 3 - CROSS CONTENT")
print("==============================================")

print(
    "Related Case Count:",
    result_3.get(
        "related_case_count"
    )
)

print(
    "Shared Indicators:",
    result_3.get(
        "shared_indicators"
    )
)

print(
    "Correlation Level:",
    result_3.get(
        "correlation_level"
    )
)

print(
    "Recurrence:",
    result_3.get(
        "recurrence"
    )
)


# ============================================================
# FINAL
# ============================================================

print()
print("==============================================")
print(" CORRELATION TEST SELESAI")
print("==============================================")
print()