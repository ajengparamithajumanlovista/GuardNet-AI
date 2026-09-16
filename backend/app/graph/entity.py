import re


def build_entities(text):

    text_lower = text.lower()


    # ==========================
    # Instagram Account
    # ==========================

    accounts = re.findall(
        r'@[A-Za-z0-9_.]+',
        text
    )


    # ==========================
    # Phone / WhatsApp
    # ==========================

    phones = re.findall(
        r'(?:\+62|62|0)[0-9]{8,13}',
        text
    )


    # ==========================
    # URL
    # ==========================

    urls = re.findall(
        r'https?://[^\s]+|www\.[^\s]+',
        text
    )


    # ==========================
    # Domain
    # ==========================

    domains = re.findall(
        r'\b[A-Za-z0-9-]+\.(?:com|net|id|xyz|site|vip|top|io)\b',
        text
    )


    # ==========================
    # Bank Account Detection
    # ==========================

    bank_numbers = re.findall(
        r'\b\d{10,16}\b',
        text
    )


    # ==========================
    # Payment Indicators
    # ==========================

    payment_keywords = [

        "qris",
        "qr",
        "deposit",
        "transfer",
        "rekening",
        "bank",
        "ewallet",
        "dana",
        "ovo",
        "gopay",
        "shopeepay"

    ]


    payment_indicator = []


    for word in payment_keywords:

        if word in text_lower:

            payment_indicator.append(word)



    # ==========================
    # Gambling Indicators
    # ==========================

    threat_keywords = [

        "slot",
        "gacor",
        "jackpot",
        "bonus",
        "daftar",
        "menang",
        "judi",
        "deposit"

    ]


    threat_indicator = []


    for word in threat_keywords:

        if word in text_lower:

            threat_indicator.append(word)



    # ==========================
    # Graph Nodes
    # ==========================

    nodes = []


    nodes.append({

        "type":
            "post",

        "value":
            "instagram_post"

    })



    for account in accounts:

        nodes.append({

            "type":
                "account",

            "value":
                account

        })


    for phone in phones:

        nodes.append({

            "type":
                "phone",

            "value":
                phone

        })


    for url in urls:

        nodes.append({

            "type":
                "url",

            "value":
                url

        })


    for domain in domains:

        nodes.append({

            "type":
                "domain",

            "value":
                domain

        })


    for pay in payment_indicator:

        nodes.append({

            "type":
                "payment",

            "value":
                pay

        })



    # ==========================
    # Graph Relationship
    # ==========================

    graph_links = []


    for entity in accounts:

        graph_links.append({

            "source":
                "instagram_post",

            "target":
                entity,

            "relation":
                "posted_by"

        })



    for phone in phones:

        graph_links.append({

            "source":
                "instagram_post",

            "target":
                phone,

            "relation":
                "contact_number"

        })



    for url in urls:

        graph_links.append({

            "source":
                "instagram_post",

            "target":
                url,

            "relation":
                "external_link"

        })



    for domain in domains:

        graph_links.append({

            "source":
                "instagram_post",

            "target":
                domain,

            "relation":
                "domain_reference"

        })



    for payment in payment_indicator:

        graph_links.append({

            "source":
                "instagram_post",

            "target":
                payment,

            "relation":
                "payment_indicator"

        })



    return {


        "account":
            list(set(accounts)),


        "phone":
            list(set(phones)),


        "url":
            list(set(urls)),


        "domain":
            list(set(domains)),


        "bank_account":
            list(set(bank_numbers)),


        "payment_indicator":
            list(set(payment_indicator)),


        "threat_indicator":
            list(set(threat_indicator)),


        "nodes":
            nodes,


        "graph_links":
            graph_links,


        "entity_count":
            len(nodes)

    }