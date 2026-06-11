from typing import Dict, Any, List
from app.services.eligibility import safe_list, safe_float
from app.services.document_engine import calculate_readiness_score

def calculate_document_impact(document_name: str, eligible_opportunities: List[Dict[str, Any]], current_missing_docs: List[str], current_expired_docs: List[str]) -> Dict[str, Any]:
    """
    Calculates the exact cascading failure impact of a single piece of missing paperwork.
    """
    affected_opps = []
    affected_modules = set()
    unlock_value = 0.0
    
    # 1. Calculate Opportunity & Value Impact
    for opp in eligible_opportunities:
        reqs = [r.lower() for r in safe_list(opp.get("required_documents", []))]
        
        # Check if this document is requested by the opportunity
        if document_name.lower() in reqs or any(document_name.lower() in r or r in document_name.lower() for r in reqs):
            affected_opps.append(opp.get("title", "Unknown Scheme"))
            mod = opp.get("module", "General")
            if mod:
                affected_modules.add(mod)
            unlock_value += safe_float(opp.get("benefit_value", opp.get("benefit_amount", 0.0)))
            
    # 2. Calculate Readiness Gain (If user uploads this document)
    current_readiness = calculate_readiness_score(current_missing_docs, current_expired_docs)
    
    # Simulate readiness if this document was removed from the missing/expired lists
    simulated_missing = [d for d in current_missing_docs if document_name.lower() not in d.lower()]
    simulated_expired = [d for d in current_expired_docs if document_name.lower() not in d.lower()]
    
    simulated_readiness = calculate_readiness_score(simulated_missing, simulated_expired)
    readiness_gain = simulated_readiness - current_readiness
    
    # 3. Determine Dependency Priority Matrix
    priority = "LOW"
    if unlock_value >= 50000 or len(affected_opps) >= 3:
        priority = "CRITICAL"
    elif unlock_value >= 10000 or len(affected_opps) >= 2:
        priority = "HIGH"
    elif len(affected_opps) == 1:
        priority = "MEDIUM"

    return {
        "document_name": document_name,
        "calculated_priority": priority,
        "affected_opportunities": affected_opps,
        "affected_modules": list(affected_modules),
        "unlock_value": unlock_value,
        "value_at_risk": unlock_value, # Semantically identical in this context
        "readiness_impact": f"+{readiness_gain} Points",
        "confidence_impact": "+15%" # UX metric
    }
