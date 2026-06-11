from typing import Dict, Any, List
from app.services.eligibility import safe_list, safe_float

# The core knowledge graph mapping document names to priority tiers
DOCUMENT_PRIORITY_MAP = {
    "Aadhaar": "CRITICAL",
    "Aadhaar Card": "CRITICAL",
    "PAN": "CRITICAL",
    "PAN Card": "CRITICAL",
    "Income Certificate": "CRITICAL",
    "Caste Certificate": "CRITICAL",
    "Land Passbook": "HIGH",
    "UDYAM": "HIGH",
    "UDYAM Certificate": "HIGH",
    "DPIIT Certificate": "HIGH",
    "Bank Passbook": "HIGH",
    "GST Certificate": "HIGH",
    "Skill Certificate": "MEDIUM",
    "Bonafide Certificate": "MEDIUM",
    "Disability Certificate": "MEDIUM"
}

def get_document_priority(doc_name: str) -> str:
    for key, priority in DOCUMENT_PRIORITY_MAP.items():
        if key.lower() in doc_name.lower():
            return priority
    return "LOW"

def calculate_readiness_score(missing_docs: List[str], expired_docs: List[str]) -> int:
    score = 100
    all_invalid = set(missing_docs + expired_docs)
    
    for doc in all_invalid:
        priority = get_document_priority(doc)
        if priority == "CRITICAL":
            score -= 30
        elif priority == "HIGH":
            score -= 15
        elif priority == "MEDIUM":
            score -= 5
        else:
            score -= 2
            
    return max(0, score)

def analyze_document_inventory(user_docs: List[Dict[str, Any]], eligible_opps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Layer 1: Centralized tracking of every document a user owns, requires, is missing, or has expired.
    user_docs: e.g. [{"document_name": "Aadhaar", "status": "Verified", "is_expired": False}]
    eligible_opps: List of opportunities the user passes the rules engine for.
    """
    required_set = set()
    for opp in eligible_opps:
        reqs = safe_list(opp.get("required_documents", []))
        for r in reqs:
            required_set.add(r.strip())
            
    available_set = set()
    expired_set = set()
    
    for doc in user_docs:
        name = doc.get("document_name", "").strip()
        status = doc.get("status", "Pending")
        is_expired = doc.get("is_expired", False)
        
        if status == "Verified" and not is_expired:
            available_set.add(name)
            # Normalization check (e.g., Aadhaar vs Aadhaar Card)
            # This is a simple implementation, a production engine would use an NLP/Synonym matcher
            for req in required_set:
                if name.lower() in req.lower() or req.lower() in name.lower():
                    available_set.add(req)
        elif is_expired:
            expired_set.add(name)
            for req in required_set:
                if name.lower() in req.lower() or req.lower() in name.lower():
                    expired_set.add(req)
                    
    missing_set = required_set - available_set
    
    # Calculate mathematically weighted score
    readiness_score = calculate_readiness_score(list(missing_set), list(expired_set))
    
    return {
        "required_documents": list(required_set),
        "available_documents": list(available_set),
        "missing_documents": list(missing_set),
        "expired_documents": list(expired_set),
        "document_readiness_score": readiness_score
    }

def analyze_document_impact(missing_docs: List[str], expired_docs: List[str], eligible_opps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Layer 2: Document Knowledge Engine
    Calculates the exact financial 'blast radius' of missing/expired documents.
    """
    impact_analysis = []
    all_invalid = list(set(missing_docs + expired_docs))
    
    for doc in all_invalid:
        priority = get_document_priority(doc)
        
        affected_opps = []
        value_at_risk = 0.0
        
        for opp in eligible_opps:
            reqs = [r.lower() for r in safe_list(opp.get("required_documents", []))]
            if doc.lower() in reqs or any(doc.lower() in r or r in doc.lower() for r in reqs):
                affected_opps.append(opp.get("title", "Unknown Opportunity"))
                value_at_risk += safe_float(opp.get("benefit_value", opp.get("benefit_amount", 0.0)))
                
        # Calculate localized readiness impact
        base_score = calculate_readiness_score([], [])
        score_without = calculate_readiness_score([doc], [])
        impact_drop = base_score - score_without
        
        if len(affected_opps) > 0:
            impact_analysis.append({
                "document_name": doc,
                "status": "Expired" if doc in expired_docs else "Missing",
                "priority_level": priority,
                "opportunities_affected": affected_opps,
                "opportunities_count": len(affected_opps),
                "value_at_risk": value_at_risk,
                "readiness_impact": f"-{impact_drop} points"
            })
            
    # Sort by value at risk descending
    impact_analysis.sort(key=lambda x: x["value_at_risk"], reverse=True)
    return impact_analysis
