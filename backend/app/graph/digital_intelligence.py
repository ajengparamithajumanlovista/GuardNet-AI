import re
from urllib.parse import urlparse


# =========================================================
# GUARDNET-AI
# DIGITAL INTELLIGENCE
# =========================================================
#
# Extract:
# - Instagram Account
# - URL
# - Domain
# - Contact / Phone / WhatsApp
#
# Contact dipisahkan dari Payment Intelligence.
#
# Nomor telepon TIDAK dianggap sebagai rekening bank.
# =========================================================


# =========================================================
# REGEX
# =========================================================

INSTAGRAM_PATTERN = re.compile(
    r"(?<![\w.])@([a-zA-Z0-9._]{2,30})"
)


URL_PATTERN = re.compile(
    r"(?i)\b(?:https?://|www\.)[^\s<>\"]+"
)


DOMAIN_PATTERN = re.compile(
    r"(?i)\b"
    r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z]{2,63}"
    r"\b"
)


PHONE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\+62|62|0)"
    r"(?:[\s.-]?\d){8,14}"
    r"(?!\d)"
)


# =========================================================
# UNIQUE
# =========================================================

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


# =========================================================
# NORMALIZE INSTAGRAM ACCOUNT
# =========================================================

def normalize_account(account: str):

    account = account.strip()

    if account.startswith("@"):

        username = account[1:]

    else:

        username = account

    username = username.lower()

    return "@" + username


# =========================================================
# NORMALIZE PHONE
# =========================================================

def normalize_phone(phone: str):

    """
    Normalize Indonesian phone number.

    Examples:

    081234567890
        -> +6281234567890

    6281234567890
        -> +6281234567890

    +6281234567890
        -> +6281234567890

    0812-3456-7890
        -> +6281234567890
    """

    # Keep only digits
    digits = re.sub(
        r"\D",
        "",
        phone
    )


    # -----------------------------------------
    # Indonesian local format
    # -----------------------------------------

    if digits.startswith("0"):

        digits = "62" + digits[1:]


    # -----------------------------------------
    # International format without +
    # -----------------------------------------

    elif digits.startswith("62"):

        pass


    # -----------------------------------------
    # 8xxxxxxxxx format
    # -----------------------------------------

    elif digits.startswith("8"):

        digits = "62" + digits


    else:

        return None


    # -----------------------------------------
    # Validate reasonable Indonesian length
    # -----------------------------------------

    if not digits.startswith("62"):

        return None


    # Indonesia country code + local number
    #
    # 62 + 9-13 digit local number
    #

    local_number = digits[2:]


    if not (9 <= len(local_number) <= 13):

        return None


    return "+" + digits


# =========================================================
# NORMALIZE DOMAIN
# =========================================================

def normalize_domain(domain: str):

    domain = domain.strip().lower()

    domain = re.sub(
        r"^https?://",
        "",
        domain
    )

    domain = re.sub(
        r"^www\.",
        "",
        domain
    )

    domain = domain.split("/")[0]

    domain = domain.split("?")[0]

    domain = domain.split("#")[0]

    return domain


# =========================================================
# NORMALIZE URL
# =========================================================

def normalize_url(url: str):

    url = url.strip()

    url = url.rstrip(
        ".,;)"
    )


    if not re.match(
        r"^https?://",
        url,
        re.IGNORECASE
    ):

        url = "https://" + url


    return url


# =========================================================
# EXTRACT ACCOUNT
# =========================================================

def extract_accounts(text: str):

    if not text:

        return []


    matches = INSTAGRAM_PATTERN.findall(
        text
    )


    accounts = []


    for match in matches:

        account = normalize_account(
            match
        )

        if account:

            accounts.append(
                account
            )


    return unique(
        accounts
    )


# =========================================================
# EXTRACT URL
# =========================================================

def extract_urls(text: str):

    if not text:

        return []


    matches = URL_PATTERN.findall(
        text
    )


    urls = []


    for match in matches:

        url = normalize_url(
            match
        )

        if url:

            urls.append(
                url
            )


    return unique(
        urls
    )


# =========================================================
# EXTRACT DOMAIN
# =========================================================

def extract_domains(text: str):

    if not text:

        return []


    domains = []


    # -----------------------------------------
    # Extract from URLs
    # -----------------------------------------

    urls = extract_urls(
        text
    )


    for url in urls:

        try:

            parsed = urlparse(
                url
            )

            hostname = parsed.hostname


            if hostname:

                domain = normalize_domain(
                    hostname
                )

                if domain:

                    domains.append(
                        domain
                    )

        except Exception:

            pass


    # -----------------------------------------
    # Direct domains
    # -----------------------------------------

    direct_domains = DOMAIN_PATTERN.findall(
        text
    )


    for domain in direct_domains:

        normalized = normalize_domain(
            domain
        )


        if normalized:

            domains.append(
                normalized
            )


    return unique(
        domains
    )


# =========================================================
# EXTRACT CONTACT
# =========================================================

def extract_contacts(text: str):

    if not text:

        return []


    matches = PHONE_PATTERN.findall(
        text
    )


    contacts = []


    for match in matches:

        phone = normalize_phone(
            match
        )


        if phone:

            contacts.append(
                phone
            )


    return unique(
        contacts
    )


# =========================================================
# DIGITAL INTELLIGENCE
# =========================================================

def analyze_digital_intelligence(
    text: str
):

    if not text:

        return {

            "account": [],

            "url": [],

            "domain": [],

            "contact": [],

            "entity_count": 0,

            "status":
                "no_text"

        }


    accounts = extract_accounts(
        text
    )


    urls = extract_urls(
        text
    )


    domains = extract_domains(
        text
    )


    contacts = extract_contacts(
        text
    )


    entity_count = (

        len(accounts)

        +

        len(urls)

        +

        len(domains)

        +

        len(contacts)

    )


    return {

        "account":
            accounts,

        "url":
            urls,

        "domain":
            domains,

        "contact":
            contacts,

        "entity_count":
            entity_count,

        "status":
            "success"

    }


# =========================================================
# GRAPH LINKS
# =========================================================

def build_digital_links(
    source: str,
    intelligence: dict
):

    links = []


    # -----------------------------------------
    # Account
    # -----------------------------------------

    for account in intelligence.get(
        "account",
        []
    ):

        links.append({

            "source":
                source,

            "target":
                account,

            "relation":
                "has_account"

        })


    # -----------------------------------------
    # Domain
    # -----------------------------------------

    for domain in intelligence.get(
        "domain",
        []
    ):

        links.append({

            "source":
                source,

            "target":
                domain,

            "relation":
                "contains_domain"

        })


    # -----------------------------------------
    # URL
    # -----------------------------------------

    for url in intelligence.get(
        "url",
        []
    ):

        links.append({

            "source":
                source,

            "target":
                url,

            "relation":
                "contains_url"

        })


    # -----------------------------------------
    # Contact
    # -----------------------------------------

    for contact in intelligence.get(
        "contact",
        []
    ):

        links.append({

            "source":
                source,

            "target":
                contact,

            "relation":
                "contains_contact"

        })


    return links


# =========================================================
# COMPLETE DIGITAL INTELLIGENCE
# =========================================================

def build_digital_intelligence(
    text: str,
    source: str = "instagram_post"
):

    intelligence = (
        analyze_digital_intelligence(
            text
        )
    )


    links = build_digital_links(

        source,

        intelligence

    )


    intelligence[
        "graph_links"
    ] = links


    return intelligence