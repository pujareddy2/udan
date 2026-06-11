from typing import Dict, Any, List

def calculate_deadline_risk(days_remaining: int, missing_docs_processing_days: int) -> Dict[str, Any]:
    """
    Calculates deadline risk (Layer 5) based on days remaining vs document processing times.
    """
    if days_remaining < 0:
        return {
            "risk": "Critical Risk", 
            "feasibility": "Deadline passed. Unfeasible.",
            "ratio": 0.0
        }
        
    buffer_days = 2
    total_needed = missing_docs_processing_days + buffer_days
    
    if total_needed <= buffer_days:
        return {
            "risk": "Low Risk", 
            "feasibility": "No major documents pending. Ready to apply immediately.",
            "ratio": float('inf')
        }
        
    ratio = days_remaining / total_needed
    
    if ratio >= 2.0:
        risk = "Low Risk"
        feas = "Plenty of time to acquire documents."
    elif ratio >= 1.2:
        risk = "Medium Risk"
        feas = "Possible, but requires document application within 48 hours."
    elif ratio >= 1.0:
        risk = "High Risk"
        feas = "Extremely tight. Apply for documents immediately today."
    else:
        risk = "Critical Risk"
        feas = "Unfeasible. Deadline will pass before documents arrive. Do not waste resources applying for docs."
        
    return {
        "risk": risk,
        "feasibility": feas,
        "ratio": round(ratio, 2)
    }

def generate_deadline_analysis(opp_name: str, days_remaining: int, pending_docs: List[str], est_completion_days: int) -> Dict[str, Any]:
    """
    Generates the Deadline Opportunity Analysis structure.
    """
    risk_data = calculate_deadline_risk(days_remaining, est_completion_days)
    
    return {
        "opportunity_name": opp_name,
        "days_remaining": days_remaining,
        "documents_pending": pending_docs,
        "estimated_completion_days": est_completion_days,
        "deadline_risk": risk_data["risk"],
        "application_feasibility": risk_data["feasibility"]
    }
