from typing import Dict, Any, List

# Layer 3: Indian Government Document Knowledge Base
DOCUMENT_KNOWLEDGE_BASE = {
    "Income Certificate": {
        "processing_time_days": "7-15 Days",
        "difficulty": "Medium",
        "official_application_link": "https://edistrict.gov.in (Varies by State)",
        "application_method": "Online via e-District portal or physically at local MeeSeva/CSC center.",
        "required_documents": ["Aadhaar Card", "Ration Card", "Self-Declaration Form", "Salary Slip/ITR"],
        "issuing_authority": "State Revenue Department (Tehsildar/Mandal Revenue Officer)"
    },
    "Caste Certificate": {
        "processing_time_days": "15-30 Days",
        "difficulty": "Medium",
        "official_application_link": "https://edistrict.gov.in (Varies by State)",
        "application_method": "Online via e-District portal or physically at local MeeSeva/CSC center.",
        "required_documents": ["Aadhaar Card", "Proof of Caste (Ancestral)", "Address Proof"],
        "issuing_authority": "State Revenue Department"
    },
    "DPIIT Recognition": {
        "processing_time_days": "14-30 Days",
        "difficulty": "High",
        "official_application_link": "https://www.startupindia.gov.in/",
        "application_method": "Fully online through the National Single Window System (NSWS).",
        "required_documents": ["Certificate of Incorporation", "PAN Card", "Pitch Deck/Business Plan"],
        "issuing_authority": "Ministry of Commerce and Industry (DPIIT)"
    },
    "UDYAM Registration": {
        "processing_time_days": "Instant (OTP Based)",
        "difficulty": "Low",
        "official_application_link": "https://udyamregistration.gov.in/",
        "application_method": "Fully online and paperless via official MSME portal.",
        "required_documents": ["Aadhaar Card", "PAN Card", "Bank Account Details"],
        "issuing_authority": "Ministry of Micro, Small and Medium Enterprises"
    },
    "Disability Certificate (UDID)": {
        "processing_time_days": "30-60 Days",
        "difficulty": "High",
        "official_application_link": "https://www.swavlambancard.gov.in/",
        "application_method": "Online application followed by physical assessment at designated Medical Board.",
        "required_documents": ["Passport Photo", "Aadhaar Card", "Previous Medical Reports"],
        "issuing_authority": "Department of Empowerment of Persons with Disabilities"
    },
    "Land Passbook": {
        "processing_time_days": "30-90 Days",
        "difficulty": "High",
        "official_application_link": "State Revenue Portal (e.g., Dharani for TS, Bhoomi for KA)",
        "application_method": "Online mutation request or physically via Patwari/Village Revenue Officer.",
        "required_documents": ["Sale Deed", "Aadhaar Card", "Pahani/Adangal extracts"],
        "issuing_authority": "State Revenue Department"
    }
}

# =================================================================
# LAYER 1 — MISSED OPPORTUNITY DETECTION ENGINE
# =================================================================
def detect_missed_opportunity(opp: Dict[str, Any], readiness: Dict[str, Any], current_days_remaining: int) -> Dict[str, Any]:
    """
    Detects if an opportunity is mathematically missed.
    Returns None if not missed.
    """
    if current_days_remaining >= 0:
        return None # Not dead yet
        
    title = opp.get("title", "Unknown Opportunity")
    val = float(opp.get("benefit_value", 0.0))
    module = opp.get("module", "General")
    
    is_eligible = opp.get("eligible", False)
    r_score = float(readiness.get("overall_readiness", 0.0))
    applied = opp.get("applied", False)
    
    # Missing logic based on rules
    if is_eligible and not applied:
        m_type = "Awareness Miss" if r_score >= 90.0 else "Full Miss"
        conf = 95
    elif not is_eligible and len(opp.get("blocking_items", [])) > 0:
        m_type = "Preparation Miss"
        conf = 85
    else:
        return None # Just ineligible
        
    return {
        "opportunity_name": title,
        "module": module,
        "benefit_value": val,
        "missed_type": m_type,
        "confidence": conf,
        "regret_hook": self.generate_regret_hook(title, val, opp.get("blocking_items", []), r_score) if not is_eligible else None
    }

    def generate_regret_hook(self, title: str, value: float, missing_docs: List[str], readiness_score: float) -> str:
        """
        Creates the 'Regret Hook' - an explicit missed value notification.
        """
        doc_str = missing_docs[0] if missing_docs else "a required document"
        val_str = f"₹{value:,.0f}" if value > 0 else "a major opportunity"
        
        return f"You missed {val_str} from {title} because your profile was {readiness_score}% ready but lacked your {doc_str}."

# =================================================================
# LAYER 2 — ROOT CAUSE ANALYSIS ENGINE
# =================================================================
def analyze_root_cause(opp: Dict[str, Any], readiness: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determines exactly why the opportunity was missed using Cause Trees.
    """
    missing_docs = readiness.get("document_readiness", {}).get("missing_documents", [])
    unanswered_q = readiness.get("profile_readiness", {}).get("missing_critical_fields", [])
    
    root_cause = "Unknown"
    category = "Unknown"
    blocking_item = "None"
    
    if len(missing_docs) > 0:
        root_cause = "Document Gap"
        category = "Documentation"
        blocking_item = missing_docs[0] # The primary blocker
    elif len(unanswered_q) > 0:
        root_cause = "Profile Gap"
        category = "Profile Setup"
        blocking_item = unanswered_q[0]
    elif opp.get("eligible", False) and not opp.get("applied", False):
        root_cause = "Action Gap"
        category = "Application Process"
        blocking_item = "Late Application / Procrastination"
        
    return {
        "root_cause": root_cause,
        "root_cause_category": category,
        "blocking_item": blocking_item,
        "impact_value": float(opp.get("benefit_value", 0.0))
    }

# =================================================================
# LAYER 3 — RECOVERY & PREVENTION ENGINE
# =================================================================
def generate_recovery_plan(missed_opp: Dict[str, Any], root_cause: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates the exact Document Action Plan using the real Indian Government Knowledge Base.
    """
    blocking_item = root_cause.get("blocking_item", "")
    val = missed_opp.get("benefit_value", 0.0)
    title = missed_opp.get("opportunity_name", "")
    
    # Assume protection for next 3 cycles if they fix it now
    future_val = val * 3 
    
    plan = {
        "message": f"You missed ₹{int(val):,} because {blocking_item} was unavailable. Fixing this now protects future cycles.",
        "estimated_future_value_unlocked": future_val,
        "document_action_plan": {}
    }
    
    # If the blocker is a known document, inject the real-world recovery info
    for known_doc, doc_data in DOCUMENT_KNOWLEDGE_BASE.items():
        if known_doc.lower() in blocking_item.lower() or blocking_item.lower() in known_doc.lower():
            plan["document_action_plan"] = {
                "document_name": known_doc,
                "importance": "critical",
                "opportunities_affected": [title],
                "processing_time_days": doc_data["processing_time_days"],
                "difficulty": doc_data["difficulty"],
                "official_application_link": doc_data["official_application_link"],
                "application_method": doc_data["application_method"],
                "required_documents": doc_data["required_documents"],
                "issuing_authority": doc_data["issuing_authority"]
            }
            break
            
    # Prevention plan
    plan["future_protection_plan"] = {
        "preventive_action": f"Apply for {blocking_item} immediately.",
        "estimated_value_protected": future_val
    }
    
    return plan

# =================================================================
# MASTER ORCHESTRATOR
# =================================================================
def process_missed_opportunity(opp: Dict[str, Any], readiness: Dict[str, Any], days_rem: int) -> Dict[str, Any]:
    missed_data = detect_missed_opportunity(opp, readiness, days_rem)
    if not missed_data:
        return None
        
    root_cause = analyze_root_cause(opp, readiness)
    recovery = generate_recovery_plan(missed_data, root_cause)
    
    return {
        "missed_opportunity": missed_data,
        "root_cause_analysis": root_cause,
        "recovery_plan": {
            "message": recovery["message"],
            "estimated_future_value_unlocked": recovery["estimated_future_value_unlocked"]
        },
        "document_action_plan": recovery.get("document_action_plan", {}),
        "future_protection_plan": recovery.get("future_protection_plan", {})
    }
