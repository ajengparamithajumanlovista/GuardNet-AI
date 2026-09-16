import re


# ============================================================
# GUARDNET-AI
# PAYMENT INTELLIGENCE
# ============================================================
#
# Payment Intelligence mendeteksi:
#
# 1. QRIS / payment QR context
# 2. Bank account
# 3. E-Wallet
# 4. Phone number
#
# Prinsip penting:
#
# - Nomor telepon TIDAK otomatis dianggap rekening bank.
# - Kata "QRIS" pada caption TIDAK otomatis berarti QRIS
#   benar-benar terdeteksi pada gambar.
# - Payment evidence digunakan sebagai supporting evidence.
#
# ============================================================


# ============================================================
# BANK ACCOUNT
# ============================================================

BANK_ACCOUNT_PATTERN = re.compile(
    r"(?i)"
    r"(?:"
    r"rekening"
    r"|"
    r"no\.?\s*rek"
    r"|"
    r"nomor\s+rekening"
    r"|"
    r"rekening\s+bank"
    r"|"
    r"bank"
    r")"
    r"\s*[:\-]?\s*"
    r"(\d{8,20})"
)


# ============================================================
# E-WALLET
# ============================================================

EWALLET_PATTERN = re.compile(
    r"(?i)"
    r"(?:"
    r"dana"
    r"|"
    r"ovo"
    r"|"
    r"gopay"
    r"|"
    r"shopeepay"
    r"|"
    r"linkaja"
    r")"
    r"\s*"
    r"[:\-]?"
    r"\s*"
    r"(\+?62|0)"
    r"[\s.\-]?"
    r"(\d{8,13})"
)


# ============================================================
# QRIS / PAYMENT KEYWORDS
# ============================================================

QRIS_KEYWORDS = [
    "qris",
    "qr.is",
    "merchant",
    "nmid",
    "scan qr",
    "scan qris",
]


PAYMENT_KEYWORDS = [
    "deposit",
    "pembayaran",
    "payment",
    "transfer",
    "bayar",
    "top up",
]


# ============================================================
# UNIQUE
# ============================================================

def unique(items):

    result = []
    seen = set()

    for item in items:

        if not item:
            continue

        key = str(item).lower()

        if key not in seen:

            seen.add(key)
            result.append(item)

    return result


# ============================================================
# NORMALIZE BANK ACCOUNT
# ============================================================

def normalize_bank_account(identifier):

    if not identifier:
        return None

    digits = re.sub(
        r"\D",
        "",
        str(identifier)
    )

    if not (
        8 <= len(digits) <= 20
    ):
        return None

    return digits


# ============================================================
# MASK BANK ACCOUNT
# ============================================================

def mask_bank_account(identifier):

    if not identifier:
        return None

    digits = re.sub(
        r"\D",
        "",
        str(identifier)
    )

    if len(digits) <= 4:

        return "*" * len(digits)

    return (
        "*" * (len(digits) - 4)
        + digits[-4:]
    )


# ============================================================
# NORMALIZE E-WALLET
# ============================================================

def normalize_ewallet(prefix, number):

    if not prefix or not number:
        return None

    digits = re.sub(
        r"\D",
        "",
        str(prefix) + str(number)
    )

    if digits.startswith("0"):

        digits = "62" + digits[1:]

    elif digits.startswith("8"):

        digits = "62" + digits

    elif not digits.startswith("62"):

        return None

    return "+" + digits


# ============================================================
# MASK IDENTIFIER
# ============================================================

def mask_identifier(identifier):

    if not identifier:
        return None

    value = str(identifier)

    if len(value) <= 4:

        return "*" * len(value)

    return (
        "*" * (len(value) - 4)
        + value[-4:]
    )


# ============================================================
# DETECT QRIS CONTEXT
# ============================================================

def detect_qris_context(text):

    if not text:
        return False

    lowered = str(text).lower()

    for keyword in QRIS_KEYWORDS:

        if keyword in lowered:
            return True

    return False


# ============================================================
# DETECT PAYMENT CONTEXT
# ============================================================

def detect_payment_context(text):

    if not text:
        return False

    lowered = str(text).lower()

    for keyword in PAYMENT_KEYWORDS:

        if keyword in lowered:
            return True

    return False


# ============================================================
# DETECT BANK ACCOUNT
# ============================================================

def detect_bank_accounts(text):

    if not text:
        return []

    matches = BANK_ACCOUNT_PATTERN.findall(
        text
    )

    normalized = []

    for match in matches:

        account = normalize_bank_account(
            match
        )

        if account:

            normalized.append(
                account
            )

    return unique(
        normalized
    )


# ============================================================
# DETECT E-WALLET
# ============================================================

def detect_ewallets(text):

    if not text:
        return []

    matches = EWALLET_PATTERN.findall(
        text
    )

    results = []

    for provider_match in matches:

        prefix = provider_match[0]
        number = provider_match[1]

        identifier = normalize_ewallet(
            prefix,
            number
        )

        if identifier:

            results.append(
                identifier
            )

    return unique(
        results
    )


# ============================================================
# DETECT PHONE NUMBERS
# ============================================================

PHONE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\+62|62|0)"
    r"(?:[\s.\-]?\d){8,13}"
    r"(?!\d)"
)


def detect_phone_numbers(text):

    if not text:
        return []

    matches = PHONE_PATTERN.findall(
        text
    )

    results = []

    for match in matches:

        digits = re.sub(
            r"\D",
            "",
            match
        )

        if digits.startswith("0"):

            digits = "62" + digits[1:]

        elif digits.startswith("8"):

            digits = "62" + digits

        if (
            digits.startswith("62")
            and 10 <= len(digits) <= 15
        ):

            results.append(
                "+" + digits
            )

    return unique(
        results
    )


# ============================================================
# ANALYZE PAYMENT INTELLIGENCE
# ============================================================

def analyze_payment_intelligence(
    text,
    qris_result=None
):

    if not text:

        text = ""

    if qris_result is None:

        qris_result = {}


    # ========================================================
    # QRIS
    # ========================================================

    qris_context = detect_qris_context(
        text
    )

    payment_context = detect_payment_context(
        text
    )

    # TRUE hanya jika QRIS detector benar-benar
    # memberikan hasil detected=True.
    #
    # Jadi kata "QRIS" saja tidak dianggap sebagai
    # QRIS visual yang terdeteksi.

    qris_detected = bool(
        qris_result.get(
            "detected",
            False
        )
    )


    qris_data = {

        "detected":
            qris_detected,

        "context_detected":
            qris_context,

        "merchant_name":
            qris_result.get(
                "merchant_name"
            ),

        "merchant_city":
            qris_result.get(
                "merchant_city"
            ),

        "mcc":
            qris_result.get(
                "mcc"
            ),

        "amount":
            qris_result.get(
                "amount"
            )
    }


    # ========================================================
    # BANK ACCOUNT
    # ========================================================

    bank_accounts = detect_bank_accounts(
        text
    )

    bank_items = []

    for account in bank_accounts:

        bank_items.append({

            "identifier":
                mask_bank_account(
                    account
                ),

            "normalized":
                account

        })


    # ========================================================
    # E-WALLET
    # ========================================================

    ewallets = detect_ewallets(
        text
    )

    ewallet_items = []

    for identifier in ewallets:

        ewallet_items.append({

            "identifier":
                mask_identifier(
                    identifier
                ),

            "normalized":
                identifier

        })


    # ========================================================
    # PHONE NUMBER
    # ========================================================

    phone_numbers = detect_phone_numbers(
        text
    )

    phone_items = []

    for phone in phone_numbers:

        phone_items.append({

            "identifier":
                mask_identifier(
                    phone
                ),

            "normalized":
                phone

        })


    # ========================================================
    # PAYMENT INDICATORS
    # ========================================================

    indicators = []

    if qris_detected:

        indicators.append(
            "QRIS"
        )

    elif qris_context:

        indicators.append(
            "QRIS_CONTEXT"
        )


    if bank_items:

        indicators.append(
            "BANK_ACCOUNT"
        )


    if ewallet_items:

        indicators.append(
            "E_WALLET"
        )


    if phone_items:

        indicators.append(
            "PHONE_NUMBER"
        )


    # ========================================================
    # PAYMENT RISK
    # ========================================================

    risk = 0.0

    if qris_detected:

        risk += 0.35

    elif qris_context:

        risk += 0.10


    if bank_items:

        risk += 0.30


    if ewallet_items:

        risk += 0.25


    if phone_items:

        risk += 0.10


    if payment_context:

        risk += 0.05


    risk = min(
        risk,
        1.0
    )


    # ========================================================
    # DETECTED
    # ========================================================

    detected = bool(
        indicators
    )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "detected":
            detected,

        "evidence":
            indicators,

        "risk":
            round(
                risk,
                3
            ),

        "qris":
            qris_data,

        "bank_account":
            bank_items,

        "e_wallet":
            ewallet_items,

        "phone_number":
            phone_items,

        "payment_context":
            payment_context,

        "payment_indicator_count":
            len(indicators),

        "status":
            "success"
    }