# ============================================================
# GUARDNET-AI
# CROSS-CONTENT CORRELATION ENGINE
# ============================================================
#
# Purpose:
# Compare digital indicators between cases.
#
# Important:
# Shared generic payment indicators such as "qris" are weak
# evidence and must NOT automatically create HIGH recurrence.
#
# Stronger correlation:
#   account + domain
#   domain + contact
#   account + contact
#   multiple independent indicators
#
# This engine indicates SHARED DIGITAL INDICATORS only.
# It does not establish ownership, identity, or legal relation.
# ============================================================


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_value(value):

    if value is None:
        return ""

    value = str(value).strip().lower()

    return value


def normalize_list(values):

    if not values:
        return []

    result = []

    for value in values:

        normalized = normalize_value(value)

        if normalized:
            result.append(normalized)

    return list(
        dict.fromkeys(result)
    )


# ============================================================
# DIGITAL INDICATORS
# ============================================================

def get_digital_indicators(case):

    digital = case.get(
        "digital_intelligence",
        {}
    )

    # Support both "contact" and "phone"
    contact_values = (
        digital.get(
            "contact",
            []
        )
        or
        digital.get(
            "phone",
            []
        )
    )

    return {

        "account":
            set(
                normalize_list(
                    digital.get(
                        "account",
                        []
                    )
                )
            ),

        "domain":
            set(
                normalize_list(
                    digital.get(
                        "domain",
                        []
                    )
                )
            ),

        "url":
            set(
                normalize_list(
                    digital.get(
                        "url",
                        []
                    )
                )
            ),

        "contact":
            set(
                normalize_list(
                    contact_values
                )
            )
    }


# ============================================================
# PAYMENT INDICATORS
# ============================================================

def get_payment_indicators(case):

    payment = case.get(
        "payment",
        {}
    )

    qris = case.get(
        "qris",
        {}
    )

    result = set()

    # --------------------------------------------------------
    # Payment evidence
    # --------------------------------------------------------

    evidence = payment.get(
        "evidence",
        []
    )

    for item in evidence:

        normalized = normalize_value(item)

        if normalized:
            result.add(normalized)

    # --------------------------------------------------------
    # Payment intelligence
    # --------------------------------------------------------

    payment_intelligence = case.get(
        "payment_intelligence",
        {}
    )

    for item in payment_intelligence.get(
        "payment_indicators",
        []
    ):

        normalized = normalize_value(item)

        if normalized:
            result.add(normalized)

    # --------------------------------------------------------
    # QRIS
    # --------------------------------------------------------

    if qris.get(
        "detected",
        False
    ):

        result.add(
            "qris"
        )

    return result


# ============================================================
# PAYMENT INDICATOR STRENGTH
# ============================================================

GENERIC_PAYMENT_INDICATORS = {

    "qris",
    "qr",
    "deposit",
    "transfer",
    "bank",
    "ewallet"

}


def payment_strength(shared_payment):

    if not shared_payment:
        return 0

    strong = (
        set(shared_payment)
        -
        GENERIC_PAYMENT_INDICATORS
    )

    # Only generic payment indicators
    if not strong:
        return 0

    # Strong payment identifier
    return len(strong)


# ============================================================
# COMPARE TWO CASES
# ============================================================

def compare_cases(
    current_case,
    previous_case
):

    current_digital = (
        get_digital_indicators(
            current_case
        )
    )

    previous_digital = (
        get_digital_indicators(
            previous_case
        )
    )

    shared = {}

    # --------------------------------------------------------
    # Account
    # --------------------------------------------------------

    shared["account"] = sorted(

        current_digital["account"]
        &
        previous_digital["account"]

    )

    # --------------------------------------------------------
    # Domain
    # --------------------------------------------------------

    shared["domain"] = sorted(

        current_digital["domain"]
        &
        previous_digital["domain"]

    )

    # --------------------------------------------------------
    # URL
    # --------------------------------------------------------

    shared["url"] = sorted(

        current_digital["url"]
        &
        previous_digital["url"]

    )

    # --------------------------------------------------------
    # Contact
    # --------------------------------------------------------

    shared["contact"] = sorted(

        current_digital["contact"]
        &
        previous_digital["contact"]

    )

    # --------------------------------------------------------
    # Payment
    # --------------------------------------------------------

    current_payment = (
        get_payment_indicators(
            current_case
        )
    )

    previous_payment = (
        get_payment_indicators(
            previous_case
        )
    )

    shared["payment"] = sorted(

        current_payment
        &
        previous_payment

    )

    # ========================================================
    # INDICATOR COUNT
    # ========================================================

    total_shared = sum(

        len(values)

        for values in shared.values()

    )

    # ========================================================
    # STRONG INDICATOR COUNT
    # ========================================================

    strong_indicator_count = (

        len(shared["account"])

        +

        len(shared["domain"])

        +

        len(shared["url"])

        +

        len(shared["contact"])

        +

        payment_strength(
            shared["payment"]
        )

    )

    # ========================================================
    # CORRELATION LEVEL
    # ========================================================

    strong_identity_count = (

        len(shared["account"])

        +

        len(shared["domain"])

        +

        len(shared["url"])

        +

        len(shared["contact"])

    )

    if strong_identity_count >= 2:

        level = "HIGH"

    elif strong_identity_count == 1:

        level = "MEDIUM"

    elif (
        payment_strength(
            shared["payment"]
        ) >= 1
    ):

        level = "MEDIUM"

    elif (
        "qris" in shared["payment"]
        or
        "qr" in shared["payment"]
    ):

        level = "LOW"

    else:

        level = "NONE"

    return {

        "case_id":
            previous_case.get(
                "case_id"
            ),

        "shared_indicators":
            shared,

        "shared_indicator_count":
            total_shared,

        "strong_indicator_count":
            strong_indicator_count,

        "correlation_level":
            level

    }


# ============================================================
# FIND RELATED CASES
# ============================================================

def find_related_cases(
    current_case,
    previous_cases
):

    correlations = []

    for previous_case in previous_cases:

        result = compare_cases(

            current_case,

            previous_case

        )

        # Only retain meaningful correlation.
        #
        # A generic QRIS-only match is intentionally ignored.

        level = result.get(
            "correlation_level",
            "NONE"
        )

        if level in [
            "MEDIUM",
            "HIGH"
        ]:

            correlations.append(
                result
            )

    return correlations


# ============================================================
# RECURRENCE SCORE
# ============================================================

def calculate_recurrence(
    correlations
):

    count = len(
        correlations
    )

    if count == 0:

        return {

            "count":
                0,

            "score":
                0.0,

            "level":
                "NONE"

        }

    # --------------------------------------------------------
    # Count strong correlations only
    # --------------------------------------------------------

    high_count = sum(

        1

        for correlation
        in correlations

        if correlation.get(
            "correlation_level"
        ) == "HIGH"

    )

    medium_count = sum(

        1

        for correlation
        in correlations

        if correlation.get(
            "correlation_level"
        ) == "MEDIUM"

    )

    # --------------------------------------------------------
    # HIGH recurrence
    # Requires multiple strong relationships.
    # --------------------------------------------------------

    if high_count >= 3:

        return {

            "count":
                count,

            "score":
                1.0,

            "level":
                "HIGH"

        }

    # --------------------------------------------------------
    # MEDIUM recurrence
    # --------------------------------------------------------

    if (
        high_count >= 1
        or
        medium_count >= 2
    ):

        return {

            "count":
                count,

            "score":
                0.6,

            "level":
                "MEDIUM"

        }

    # --------------------------------------------------------
    # LOW recurrence
    # --------------------------------------------------------

    return {

        "count":
            count,

        "score":
            0.3,

        "level":
            "LOW"

    }


# ============================================================
# COMPLETE CROSS-CONTENT ANALYSIS
# ============================================================

def analyze_cross_content(
    current_case,
    previous_cases
):

    correlations = find_related_cases(

        current_case,

        previous_cases

    )

    recurrence = calculate_recurrence(

        correlations

    )

    # ========================================================
    # UNIQUE SHARED INDICATORS
    # ========================================================

    aggregate = {

        "account":
            set(),

        "domain":
            set(),

        "url":
            set(),

        "contact":
            set(),

        "payment":
            set()

    }

    for correlation in correlations:

        shared = correlation.get(
            "shared_indicators",
            {}
        )

        for key in aggregate:

            for value in shared.get(
                key,
                []
            ):

                aggregate[key].add(
                    value
                )

    aggregate = {

        key:
            sorted(values)

        for key, values
        in aggregate.items()

    }

    # ========================================================
    # COUNTS
    # ========================================================

    total_shared = sum(

        len(values)

        for values
        in aggregate.values()

    )

    strong_shared = (

        len(
            aggregate["account"]
        )

        +

        len(
            aggregate["domain"]
        )

        +

        len(
            aggregate["url"]
        )

        +

        len(
            aggregate["contact"]
        )

    )

    # ========================================================
    # OVERALL CORRELATION
    # ========================================================

    if strong_shared >= 2:

        correlation_level = "HIGH"

    elif strong_shared == 1:

        correlation_level = "MEDIUM"

    elif (
        "qris"
        in aggregate["payment"]
        and
        total_shared == 1
    ):

        correlation_level = "LOW"

    elif total_shared >= 1:

        correlation_level = "LOW"

    else:

        correlation_level = "NONE"

    # ========================================================
    # RETURN
    # ========================================================

    return {

        "related_cases":
            correlations,

        "related_case_count":
            len(
                correlations
            ),

        "shared_indicators":
            aggregate,

        "shared_indicator_count":
            total_shared,

        "strong_shared_indicator_count":
            strong_shared,

        "correlation_level":
            correlation_level,

        "recurrence":
            recurrence,

        "status":
            "success"

    }