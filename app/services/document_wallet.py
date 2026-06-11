from typing import Dict, Any, List
from app.services.document_readiness import calculate_advanced_document_readiness
from app.services.document_expiry import calculate_expiry_intelligence
from app.services.document_engine import get_document_priority

def generate_document_wallet_dashboard(user_docs: List[Dict[str, Any]], eligible_opps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Layer 8: Document Wallet Engine
    Aggregates all document intelligence into a Swiggy-style frontend dashboard state.
    """
    # 1. Pull Base Analytics
    readiness_data = calculate_advanced_document_readiness(user_docs, eligible_opps)
    expiry_data = calculate_expiry_intelligence(user_docs, eligible_opps)
    
    # 2. Build Categories
    verified_docs = readiness_data["available_documents"]
    missing_docs = readiness_data["missing_documents"]
    
    under_review_docs = []
    for d in user_docs:
        if d.get("status") == "Pending":
            under_review_docs.append(d.get("document_name"))
            
    # Remove under_review docs from the 'missing' pile so UI doesn't yell at user
    missing_docs = [m for m in missing_docs if m not in under_review_docs]
    
    # 3. Action Required Array (Sorted by unlock value)
    action_required = []
    for m in missing_docs:
        priority = get_document_priority(m)
        unlock_val = 0.0
        for unlock in readiness_data.get("unlock_analysis", []):
            if unlock["document_name"] == m:
                unlock_val = unlock["unlock_value"]
                break
                
        action_required.append({
            "document_name": m,
            "priority": priority,
            "unlock_value": unlock_val
        })
        
    action_required.sort(key=lambda x: x["unlock_value"], reverse=True)
    
    # 4. Urgent Array (Expiring Soon/Expired)
    urgent_required = []
    for exp in expiry_data:
        urgent_required.append({
            "document_name": exp["document_name"],
            "status": exp["status"],
            "days_to_expiry": exp["days_to_expiry"],
            "value_at_risk": exp["value_at_risk"]
        })
        
    # Determine Master Status
    wallet_status = "HEALTHY"
    if len(urgent_required) > 0 or len(action_required) > 0:
        wallet_status = "NEEDS_ATTENTION"
        
    # If a critical doc is missing or expired, it's critical
    if any(a["priority"] == "CRITICAL" for a in action_required) or any(u["days_to_expiry"] <= 7 for u in urgent_required):
        wallet_status = "CRITICAL_ACTION_REQUIRED"
        
    return {
        "wallet_status": wallet_status,
        "total_documents_required": len(readiness_data["required_documents"]),
        "total_documents_verified": len(verified_docs),
        "categories": {
            "verified": verified_docs,
            "action_required": action_required,
            "urgent": urgent_required,
            "under_review": under_review_docs
        }
    }
