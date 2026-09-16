import re


def detect_payment(text):

    text = text.lower()


    evidence = []


    # QRIS
    if "qris" in text:
        evidence.append("qris")


    # rekening
    rekening = re.findall(
        r"\b\d{10,16}\b",
        text
    )

    if rekening:
        evidence.append(
            "bank_account"
        )


    # phone
    phone = re.findall(
        r"(08\d{8,12})",
        text
    )

    if phone:
        evidence.append(
            "phone_number"
        )


    # URL
    url = re.findall(
        r"(https?://\S+|www\.\S+)",
        text
    )

    if url:
        evidence.append(
            "url"
        )


    return {

        "detected":
            len(evidence) > 0,


        "evidence":
            evidence,


        "risk":
            min(
                len(evidence)/4,
                1
            )
    }