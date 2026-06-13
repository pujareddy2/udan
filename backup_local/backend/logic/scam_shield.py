import re


def check_scam(text: str) -> dict:
    """
    Analyzes job postings/messages using rule-based heuristics to flag potential scams.
    Returns:
        dict: {"is_scam": bool, "flags": list[str]}

    Examples:
        >>> check_scam("Pay Rs 5000 to confirm your government job, limited seats!")
        {"is_scam": True, "flags": ["Money/fee/payment requested", "Urgency language used"]}

        >>> check_scam("SSC CGL 2026 notification released, apply on ssc.gov.in")
        {"is_scam": False, "flags": []}
    """
    flags = []
    if not text:
        return {"is_scam": False, "flags": flags}

    text_lower = text.lower()

    # 1. Money / fee / payment / "registration charges"
    money_keywords = [
        "money", "fee", "fees", "payment", "registration charges",
        "registration charge", "security deposit", "charges", "pay"
    ]
    has_money = (
        any(kw in text_lower for kw in money_keywords)
        or re.search(r'(?:rs\.?|rupees|₹)\s*\d+', text_lower)
    )
    if has_money:
        flags.append("Money/fee/payment requested")

    # 2. Bank / UPI / OTP / card / account details
    financial_keywords = [
        "bank", "upi", "otp", "card", "account details",
        "account number", "cvv", "credit", "debit", "pin"
    ]
    has_financial = any(kw in text_lower for kw in financial_keywords)
    if has_financial:
        flags.append("Financial/account details requested")

    # 3. Claims a government job but links to a non-.gov.in / non-.nic.in domain
    govt_keywords = [
        "government job", "govt job", "govt. job", "govt", "government", "sarkari"
    ]
    is_govt_claim = any(kw in text_lower for kw in govt_keywords)
    if is_govt_claim:
        candidates = re.findall(r'\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', text)
        non_official = []
        for cand in candidates:
            cand_clean = cand.strip(".,;:!?()").lower()
            # Skip version numbers or numeric IPs
            if re.match(r'^\d+(\.\d+)+$', cand_clean):
                continue
            if not (cand_clean.endswith(".gov.in") or cand_clean.endswith(".nic.in")):
                non_official.append(cand_clean)
        if non_official:
            flags.append(
                f"Claims a government job but links to non-official domain(s): {', '.join(non_official)}"
            )

    # 4. "Guaranteed government job" / "100% selection" type language
    guarantee_keywords = [
        "guaranteed government job", "guaranteed job", "100% selection",
        "100% placement", "direct selection", "direct hiring", "assured selection"
    ]
    has_guarantee = any(kw in text_lower for kw in guarantee_keywords)
    if has_guarantee:
        flags.append("Guaranteed selection language used")

    # 5. Urgency ("apply within X hours", "limited seats today")
    urgency_keywords = [
        "limited seats", "limited seat", "apply within",
        "closing today", "urgent hiring", "apply immediately"
    ]
    has_urgency = (
        any(kw in text_lower for kw in urgency_keywords)
        or re.search(r'apply within \w+', text_lower)
    )
    if has_urgency:
        flags.append("Urgency language used")

    return {
        "is_scam": len(flags) > 0,
        "flags": flags
    }
