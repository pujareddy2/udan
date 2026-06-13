import re
from typing import Dict, Any, List

def check_scam(text: str) -> Dict[str, Any]:
    """
    Analyzes job postings for common scam heuristics without calling an LLM.

    >>> check_scam("Urgent hiring! Please pay Rs. 5000 registration fee.")
    {'is_scam': True, 'flags': ['Money/fee/payment requested', 'Urgency language used']}

    >>> check_scam("Send your CVV and OTP to get 100% guaranteed selection.")
    {'is_scam': True, 'flags': ['Financial/account details requested', 'Guaranteed government job claim']}

    >>> check_scam("Apply for sarkari government job at http://fake-jobs.com")
    {'is_scam': True, 'flags': ['non-official domain for government job']}

    >>> check_scam("We are hiring software engineers. Send your resume to careers@company.com")
    {'is_scam': False, 'flags': []}
    """
    
    text_lower = text.lower()
    flags: List[str] = []
    
    # 1. Money/fee/payment
    money_keywords = ["fee", "fees", "payment", "registration charge", "security deposit"]
    # Match words like "pay", "rs", "₹", "inr" followed by a number, or keywords
    if any(keyword in text_lower for keyword in money_keywords) or re.search(r'\b(pay|rs\.?|₹|inr)\b\s*\d+', text_lower):
        flags.append("Money/fee/payment requested")
        
    # 2. Financial details
    financial_keywords = ["bank", "upi", "otp", "card details", "cvv", "account number"]
    if any(re.search(rf'\b{re.escape(keyword)}\b', text_lower) for keyword in financial_keywords):
        flags.append("Financial/account details requested")
        
    # 3. Fake government domains
    gov_keywords = ["government job", "sarkari", "govt"]
    if any(keyword in text_lower for keyword in gov_keywords):
        # Find all domains/websites
        domains = re.findall(r'\b[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?\b', text_lower)
        if domains:
            has_fake_url = False
            for dom in domains:
                if not (dom.endswith(".gov.in") or dom.endswith(".nic.in")):
                    has_fake_url = True
                    break
            if has_fake_url:
                flags.append("non-official domain for government job")
                
    # 4. Guaranteed selection
    guarantee_keywords = ["guaranteed job", "100% selection", "100% placement", "direct selection", "guaranteed government"]
    if any(keyword in text_lower for keyword in guarantee_keywords):
        flags.append("Guaranteed government job claim")
        
    # 5. Urgency
    urgency_keywords = ["limited seats", "apply immediately", "urgent hiring", "apply within", "urgently"]
    if any(keyword in text_lower for keyword in urgency_keywords):
        flags.append("Urgency language used")
        
    return {
        "is_scam": len(flags) > 0,
        "flags": flags
    }

if __name__ == "__main__":
    import doctest
    doctest.testmod()
