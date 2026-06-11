from typing import Dict, Any, List
from app.services.eligibility import safe_list, safe_float
from app.services.document_engine import get_document_priority, analyze_document_inventory

def calculate_advanced_document_readiness(user_docs: List[Dict[str, Any]], eligible_opps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Layer 6: Document Readiness Engine
    Calculates granular readiness mathematically with strict critical penalties.
    """
    inventory = analyze_document_inventory(user_docs, eligible_opps)
    
    req_docs = inventory["required_documents"]
    avail_docs = inventory["available_documents"]
    missing_docs = inventory["missing_documents"]
    expired_docs = inventory["expired_documents"]
    
    total_required = len(req_docs)
    
    if total_required == 0:
        base_score = 100
    else:
        # Base fractional score
        base_score = int((len(avail_docs) / total_required) * 100)
        
    critical_missing = []
    
    # Apply Strict Mathematical Penalties
    penalty = 0
    for doc in missing_docs:
        priority = get_document_priority(doc)
        if priority == "CRITICAL":
            critical_missing.append(doc)
            penalty += 20
        elif priority == "HIGH":
            penalty += 10
            
    for doc in expired_docs:
        priority = get_document_priority(doc)
        if priority == "CRITICAL":
            critical_missing.append(doc)
            penalty += 25 # Expired is penalized slightly heavier to urge renewal
        elif priority == "HIGH":
            penalty += 15
        else:
            penalty += 5
            
    final_score = max(0, base_score - penalty)
    
    # Unlock Analysis Module
    unlock_analysis = []
    all_invalid = list(set(missing_docs + expired_docs))
    
    for doc in all_invalid:
        unlocked = []
        unlock_val = 0.0
        
        for opp in eligible_opps:
            reqs = [r.lower() for r in safe_list(opp.get("required_documents", []))]
            if doc.lower() in reqs or any(doc.lower() in r or r in doc.lower() for r in reqs):
                unlocked.append(opp.get("title", "Unknown Scheme"))
                unlock_val += safe_float(opp.get("benefit_value", 0.0))
                
        # Simulate readiness gain
        simulated_missing = [d for d in missing_docs if d != doc]
        simulated_expired = [d for d in expired_docs if d != doc]
        
        simulated_base = 100 if total_required == 0 else int(((len(avail_docs) + 1) / total_required) * 100)
        simulated_penalty = penalty
        
        prior = get_document_priority(doc)
        if prior == "CRITICAL":
            simulated_penalty -= 25 if doc in expired_docs else 20
        elif prior == "HIGH":
            simulated_penalty -= 15 if doc in expired_docs else 10
        elif doc in expired_docs:
            simulated_penalty -= 5
            
        simulated_score = max(0, simulated_base - simulated_penalty)
        gain = simulated_score - final_score
        
        if len(unlocked) > 0:
            unlock_analysis.append({
                "document_name": doc,
                "opportunities_unlocked": unlocked,
                "unlock_value": unlock_val,
                "readiness_gain": f"+{gain}%"
            })
            
    return {
        "document_readiness_score": final_score,
        "required_documents": req_docs,
        "available_documents": avail_docs,
        "missing_documents": missing_docs,
        "expired_documents": expired_docs,
        "critical_missing_documents": critical_missing,
        "unlock_analysis": unlock_analysis
    }
