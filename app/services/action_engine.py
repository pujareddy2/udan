from typing import Dict, Any, List

def calculate_impact_score(action: Dict[str, Any], max_unlock_value: float) -> float:
    """
    Calculates the Impact Score (0-100) using the exact formula from the architecture.
    Impact_Score = (Unlock_Value_Normalized * 0.40) + (Opps_Unlocked * 0.30) + (Readiness_Increase * 0.15) + (Confidence_Increase * 0.15) + Deadline_Bonus
    """
    unlock_val = float(action.get('estimated_unlock_value', 0.0))
    opps = float(action.get('opportunities_unlocked', 0.0))
    readiness_inc = float(action.get('readiness_gain', 0.0))
    confidence_inc = float(action.get('confidence_gain', 0.0))
    deadline_risk = action.get('deadline_risk', 'Low')
    
    # Normalize Unlock Value (0-100)
    val_norm = (unlock_val / max_unlock_value * 100.0) if max_unlock_value > 0 else 0.0
    
    # Scale opps assuming 10 opps is 100 points
    opps_norm = min((opps / 10.0) * 100.0, 100.0)
    
    score = (val_norm * 0.40) + (opps_norm * 0.30) + (readiness_inc * 0.15) + (confidence_inc * 0.15)
    
    # Deadline Bonus
    if deadline_risk in ['High', 'High Risk', 'Critical Risk']:
        score += 20.0
    elif deadline_risk in ['Medium', 'Medium Risk']:
        score += 10.0
        
    return round(min(100.0, score), 2)

def generate_action_intelligence(actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generates the Recommended Next Steps arrays sorted by impact.
    """
    if not actions:
        return {"top_action": None, "top_5_actions": [], "top_10_actions": []}
        
    max_val = max([float(a.get('estimated_unlock_value', 0.0)) for a in actions] + [0.1])
    
    processed = []
    for a in actions:
        # Clone dict
        act = dict(a)
        act['impact_score'] = calculate_impact_score(act, max_val)
        processed.append(act)
        
    # Sort by impact_score descending
    processed.sort(key=lambda x: x['impact_score'], reverse=True)
    
    return {
        "top_action": processed[0] if len(processed) > 0 else None,
        "top_5_actions": processed[:5],
        "top_10_actions": processed[:10]
    }
