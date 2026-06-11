from typing import Dict, Any, List
from datetime import datetime
from app.services.eligibility import safe_float, safe_list

def calculate_expiry_intelligence(user_docs: List[Dict[str, Any]], eligible_opps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Layer 7: Document Expiry Intelligence Engine
    Monitors document decay and calculates financial value at risk.
    """
    expiry_alerts = []
    current_time = datetime.utcnow()
    
    for doc in user_docs:
        name = doc.get("document_name", "Unknown Document")
        expiry_str = doc.get("expiry_date")
        
        if not expiry_str:
            continue
            
        try:
            # Simple ISO format parsing for demo purposes
            expiry_date = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
            delta = expiry_date.replace(tzinfo=None) - current_time
            days_to_expiry = delta.days
        except Exception:
            continue # Skip invalid dates
            
        status = "Valid"
        if days_to_expiry < 0:
            status = "Expired"
        elif days_to_expiry <= 7:
            status = "Critical"
        elif days_to_expiry <= 30:
            status = "Expiring Soon"
            
        if status == "Valid":
            continue # We only generate intelligence for at-risk documents
            
        # Calculate Value at Risk
        affected_opps = []
        val_at_risk = 0.0
        
        for opp in eligible_opps:
            reqs = [r.lower() for r in safe_list(opp.get("required_documents", []))]
            if name.lower() in reqs or any(name.lower() in r or r in name.lower() for r in reqs):
                affected_opps.append(opp.get("title", "Unknown Scheme"))
                val_at_risk += safe_float(opp.get("benefit_value", 0.0))
                
        expiry_alerts.append({
            "document_name": name,
            "status": status,
            "days_to_expiry": days_to_expiry,
            "renewal_link": "https://edistrict.gov.in", # Normally pulled from document_master
            "value_at_risk": val_at_risk,
            "affected_opportunities": affected_opps
        })
        
    # Sort by urgency
    expiry_alerts.sort(key=lambda x: x["days_to_expiry"])
    return expiry_alerts
