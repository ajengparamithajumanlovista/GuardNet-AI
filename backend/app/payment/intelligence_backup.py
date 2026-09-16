import re


# ============================================================
# GUARDNET-AI
# PAYMENT INTELLIGENCE
# ============================================================
#
# Fungsi:
#
# 1. Deteksi QRIS berdasarkan:
#    - QRIS detector
#    - QRIS keyword/context
#
# 2. Deteksi rekening bank
#    - HANYA jika ada konteks rekening/bank
#
# 3. Deteksi e-wallet
#
# 4. Deteksi nomor telepon/contact
#
# PENTING:
#
# Nomor telepon TIDAK dianggap sebagai rekening bank.
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
        r"no\.?\s*rekening"
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
        r"go\s*pay"
        r"|"
        r"shopeepay"
        r"|"
        r"linkaja"
    r")"
    r"\s*"
    r"[:\-]?\s*"
    r"(\+?62|0)"
    r"[\s.\-]?"
    r"(\d{8,13})"
)


# ============================================================
# PHONE NUMBER
# ============================================================

PHONE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:"
        r"\+62"
        r"|"
        r"62"
        r"|"
        r"0"
    r")"
    r"[\s.\-]?"
    r"(?:\d[\s.\-]?){8,13}"
    r"(?!\d)"
)


# ============================================================
# QRIS KEYWORDS
# ============================================================

QRIS_KEYWORDS = [

    "qris",

    "qr.is",

    "scan qr",

    "scan qris",

    "nmid",

    "merchant",

    "pembayaran",

    "payment"

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

        key = str(
            item
        ).lower()

        if key not in seen:

            seen.add(
                key
            )

            result.append(
                item
            )

    return result


# ============================================================
# NORMALIZE BANK ACCOUNT
# ============================================================

def normalize_bank_account(
    identifier
):

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

def mask_bank_account(
    identifier
):

    if not identifier:
        return None

    digits = re.sub(
        r"\D",
        "",
        str(identifier)
    )

    if len(digits) <= 4:

        return "*" * len(
            digits
        )

    return (
        "*"
        * (
            len(digits) - 4
        )
        +
        digits[-4:]
    )


# ============================================================
# NORMALIZE PHONE
# ============================================================

def normalize_phone(
    identifier
):

    if not identifier:
        return None

    digits = re.sub(
        r"\D",
        "",
        str(identifier)
    )

    # 081234567890
    if digits.startswith("0"):

        digits = (
            "62"
            +
            digits[1:]
        )

    # 81234567890
    elif digits.startswith("8"):

        digits = (
            "62"
            +
            digits
        )

    # +6281234567890 / 6281234567890
    elif digits.startswith("62"):

        pass

    else:

        return None

    if not (
        10 <= len(digits) <= 15
    ):
        return None

    return "+" + digits


# ============================================================
# NORMALIZE E-WALLET
# ============================================================

def normalize_ewallet(
    prefix,
    number
):

    digits = re.sub(
        r"\D",
        "",
        str(prefix)
        +
        str(number)
    )

    if digits.startswith("0"):

        digits = (
            "62"
            +
            digits[1:]
        )

    elif digits.startswith("8"):

        digits = (
            "62"
            +
            digits
        )

    elif digits.startswith("62"):

        pass

    else:

        return None

    if not (
        10 <= len(digits) <= 15
    ):
        return None

    return "+" + digits


# ============================================================
# MASK IDENTIFIER
# ============================================================

def mask_identifier(
    identifier
):

    if not identifier:
        return None

    value = str(
        identifier
    )

    if len(value) <= 4:

        return (
            "*"
            *
            len(value)
        )

    return (
        "*"
        *
        (
            len(value) - 4
        )
        +
        value[-4:]
    )


# ============================================================
# DETECT QRIS CONTEXT
# ============================================================

def detect_qris_context(
    text
):

    if not text:
        return False

    lowered = str(
        text
    ).lower()

    for keyword in QRIS_KEYWORDS:

        if keyword in lowered:

            return True

    return False


# ============================================================
# DETECT BANK ACCOUNT
# ============================================================

def detect_bank_accounts(
    text
):

    if not text:
        return []

    matches = (
        BANK_ACCOUNT_PATTERN.findall(
            str(text)
        )
    )

    normalized = []

    for match in matches:

        account = (
            normalize_bank_account(
                match
            )
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

def detect_ewallets(
    text
):

    if not text:
        return []

    matches = (
        EWALLET_PATTERN.findall(
            str(text)
        )
    )

    results = []

    for provider_match in matches:

        if not provider_match:
            continue

        prefix = (
            provider_match[0]
        )

        number = (
            provider_match[1]
        )

        identifier = (
            normalize_ewallet(
                prefix,
                number
            )
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

def detect_phone_numbers(
    text
):

    if not text:
        return []

    matches = (
        PHONE_PATTERN.findall(
            str(text)
        )
    )

    results = []

    for match in matches:

        identifier = (
            normalize_phone(
                match
            )
        )

        if identifier:

            results.append(
                identifier
            )

    return unique(
        results
    )


# ============================================================
# COMPLETE PAYMENT INTELLIGENCE
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

    qris_context = (
        detect_qris_context(
            text
        )
    )

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

    bank_accounts = (
        detect_bank_accounts(
            text
        )
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

    ewallets = (
        detect_ewallets(
            text
        )
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
    # PHONE
    # ========================================================

    phone_numbers = (
        detect_phone_numbers(
            text
        )
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


    # --------------------------------------------------------
    # QRIS
    # --------------------------------------------------------

    if qris_detected:

        indicators.append(
            "QRIS"
        )

    elif qris_context:

        indicators.append(
            "QRIS_TEXT"
        )


    # --------------------------------------------------------
    # BANK
    # --------------------------------------------------------

    if bank_items:

        indicators.append(
            "BANK_ACCOUNT"
        )


    # --------------------------------------------------------
    # E-WALLET
    # --------------------------------------------------------

    if ewallet_items:

        indicators.append(
            "E_WALLET"
        )


    # --------------------------------------------------------
    # PHONE
    # --------------------------------------------------------

    if phone_items:

        indicators.append(
            "PHONE_NUMBER"
        )


    # ========================================================
    # PAYMENT DETECTED
    # ========================================================

    payment_detected = bool(
        indicators
    )


    # ========================================================
    # PAYMENT RISK
    # ========================================================

    risk = 0.0


    # QRIS benar-benar terdeteksi
    if qris_detected:

        risk += 0.40


    # Hanya kata QRIS ditemukan di caption/OCR
    elif qris_context:

        risk += 0.20


    # Rekening bank
    if bank_items:

        risk += 0.35


    # E-wallet
    if ewallet_items:

        risk += 0.30


    # Nomor telepon
    if phone_items:

        risk += 0.15


    risk = min(
        risk,
        1.0
    )


    # ========================================================
    # RESULT
    # ========================================================

    return {

        "detected":
            payment_detected,

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

        "payment_indicators":
            indicators,

        "payment_indicator_count":
            len(indicators),

        "status":
            "success"

    }