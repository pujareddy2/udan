import re
from typing import Dict, Any, List

def check_scam(text: str) -> Dict[str, Any]:
    """
    Analyzes job postings for common scam heuristics without calling an LLM.

    >>> check_scam("Urgent hiring! Please pay Rs. 5000 registration fee.")
    {'is_scam': True, 'flags': ['Money/fee/payment', 'Urgency']}

    >>> check_scam("Send your CVV and OTP to get 100% guaranteed selection.")
    {'is_scam': True, 'flags': ['Financial details', 'Guaranteed selection']}

    >>> check_scam("Apply for sarkari government job at http://fake-jobs.com")
    {'is_scam': True, 'flags': ['Fake government domain']}

    >>> check_scam("We are hiring software engineers. Send your resume to careers@company.com")
    {'is_scam': False, 'flags': []}
    """
    
    text_lower = text.lower()
    flags: List[str] = []
    
    # 1. Money/fee/payment
    money_keywords = ["fee", "fees", "payment", "registration charge", "security deposit"]
    if any(keyword in text_lower for keyword in money_keywords) or re.search(r'(rs\.|₹)\s*\d+', text_lower):
        flags.append("Money/fee/payment")
        
    # 2. Financial details
    financial_keywords = ["bank", "upi", "otp", "card details", "cvv", "account number"]
    # We add boundaries to 'otp' and 'cvv' to avoid matching inside other words like 'notpool' etc.
    if any(re.search(rf'\b{re.escape(keyword)}\b', text_lower) for keyword in financial_keywords):
        flags.append("Financial details")
        
    # 3. Fake government domains
    gov_keywords = ["government job", "sarkari", "govt"]
    if any(keyword in text_lower for keyword in gov_keywords):
        # Find all URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text_lower)
        if urls:
            has_fake_url = False
            for url in urls:
                # Strip trailing paths/queries to check the base domain
                domain = url.split('/')[2] if '/' in url else url
                if not (domain.endswith(".gov.in") or domain.endswith(".nic.in")):
                    has_fake_url = True
                    break
            if has_fake_url:
                flags.append("Fake government domain")
                
    # 4. Guaranteed selection
    guarantee_keywords = ["guaranteed job", "100% selection", "100% placement", "direct selection"]
    if any(keyword in text_lower for keyword in guarantee_keywords):
        flags.append("Guaranteed selection")
        
    # 5. Urgency
    urgency_keywords = ["limited seats", "apply immediately", "urgent hiring", "apply within"]
    if any(keyword in text_lower for keyword in urgency_keywords):
        flags.append("Urgency")
        
    return {
        "is_scam": len(flags) > 0,
        "flags": flags
    }

if __name__ == "__main__":
    import doctest
    doctest.testmod()
