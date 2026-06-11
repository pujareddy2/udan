from typing import Dict, Any, List
from app.services.eligibility import get_field, safe_float, safe_list

def analyze_future_risk(missing_items: List[str], active_opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates the 'blast radius' of missing documents/profile fields against upcoming opportunities.
    """
    risk_factors = {}
    total_val_at_risk = 0.0
    total_opps_at_risk = 0
    
    for item in missing_items:
        risk_factors[item] = {
            "action": f"Acquire or Update {item}",
            "importance": "Critical",
            "value_protected": 0.0,
            "future_opportunities_protected": []
        }
        
    for opp in active_opportunities:
        title = get_field(opp, 'title', '')
        val = safe_float(get_field(opp, 'benefit_amount', 0.0))
        
        # In a real system, we cross-reference opp['required_documents'] and opp['required_fields']
        # Here we simulate the intersection check
        req_docs = safe_list(get_field(opp, 'required_documents', []))
        
        for item in missing_items:
            # If the missing item is strictly required by this future opportunity
            if item in req_docs or any(item.lower() in d.lower() for d in req_docs):
                risk_factors[item]["value_protected"] += val
                risk_factors[item]["future_opportunities_protected"].append(title)
                total_val_at_risk += val
                total_opps_at_risk += 1

    # Filter out empty risks
    active_risks = [rf for item, rf in risk_factors.items() if len(rf["future_opportunities_protected"]) > 0]
    
    # Sort by value protected
    active_risks.sort(key=lambda x: x["value_protected"], reverse=True)
    
    risk_level = "Low"
    if total_val_at_risk > 100000:
        risk_level = "Critical"
    elif total_val_at_risk > 50000:
        risk_level = "High"
    elif total_val_at_risk > 10000:
        risk_level = "Medium"

    return {
        "future_risk_level": risk_level,
        "opportunities_at_risk": total_opps_at_risk,
        "value_at_risk": total_val_at_risk,
        "risk_factors": active_risks
    }
