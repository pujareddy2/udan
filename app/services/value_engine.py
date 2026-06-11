from typing import Dict, Any, List

from app.services.eligibility import get_field, safe_float, safe_list

# =================================================================
# LAYER 1 — BENEFIT VALUE ENGINE
# =================================================================
def calculate_benefit_value(opp: Any) -> Dict[str, Any]:
    """
    Calculates the exact multi-dimensional value of an opportunity.
    """
    val = safe_float(get_field(opp, 'benefit_amount', 0.0))
    b_type = str(get_field(opp, 'benefit_type', 'cash')).lower()
    
    financial = 0.0
    indirect = 0.0
    non_fin = []
    
    financial_types = ['cash', 'subsidy', 'grant', 'pension', 'scholarship', 'reimbursement', 'loan']
    indirect_types = ['training', 'insurance', 'incubation', 'certification']
    non_fin_types = ['mentorship', 'recognition', 'support']
    
    if any(t in b_type for t in financial_types) or val > 0:
        financial = val
    elif any(t in b_type for t in indirect_types):
        indirect = val
    elif any(t in b_type for t in non_fin_types):
        non_fin.append(b_type.capitalize())
        
    exp = f"You are eligible for ₹{int(val):,} in {b_type} benefits." if val > 0 else f"You are eligible for {b_type} benefits."
        
    return {
        "benefit_value": val,
        "benefit_type": b_type.title(),
        "financial_value": financial,
        "indirect_value": indirect,
        "non_financial_value": non_fin,
        "explanation": exp
    }

# =================================================================
# LAYER 2 — SAVINGS ENGINE
# =================================================================
def calculate_savings(opp: Any) -> Dict[str, Any]:
    """
    Calculates exact out-of-pocket money saved by claiming the opportunity.
    """
    market_cost = safe_float(get_field(opp, 'average_market_cost', 0.0))
    benefit_val = safe_float(get_field(opp, 'benefit_amount', 0.0))
    is_recurring = get_field(opp, 'is_recurring', False)
    
    # If explicitly passed as string 'True'/'1'
    if isinstance(is_recurring, str) and is_recurring.lower() in ['true', '1', 'yes']:
        is_recurring = True
        
    if market_cost > 0:
        reduced = max(0.0, market_cost - benefit_val)
        savings = market_cost - reduced
    else:
        # Implicit savings (the benefit itself acts as the savings)
        reduced = 0.0
        savings = benefit_val
        market_cost = benefit_val

    annual = savings if is_recurring else 0.0
    # Assuming standard 5-year outlook for recurring scheme lifetime savings if not explicitly defined
    lifetime = annual * 5 if is_recurring else savings 
    
    exp = f"By claiming this, your out-of-pocket cost drops to ₹{int(reduced):,}, saving you ₹{int(savings):,}."
    
    return {
        "current_cost": market_cost,
        "reduced_cost": reduced,
        "savings_value": savings,
        "recurring_savings": savings if is_recurring else 0.0,
        "annual_savings": annual,
        "lifetime_savings": lifetime,
        "explanation": exp
    }

# =================================================================
# LAYER 3 — MISSED OPPORTUNITY ENGINE
# =================================================================
def calculate_missed_opportunity(profile: Any, opp: Any) -> Dict[str, Any]:
    """
    Calculates the financial loss incurred by not applying earlier.
    """
    opp_name = get_field(opp, 'title', 'Unknown Scheme')
    benefit_val = safe_float(get_field(opp, 'benefit_amount', 0.0))
    
    user_age = safe_float(get_field(profile, 'age', 0))
    min_age = safe_float(get_field(opp, 'min_age', 0))
    
    launch_year = safe_float(get_field(opp, 'launch_year', 2020))
    current_year = 2026
    
    is_recurring = get_field(opp, 'is_recurring', False)
    if isinstance(is_recurring, str) and is_recurring.lower() in ['true', '1', 'yes']:
        is_recurring = True
        
    years_missed = 0
    if min_age > 0 and user_age > min_age:
        # They became eligible when they hit min_age. 
        # Capped by when the scheme actually launched.
        years_eligible_by_age = user_age - min_age
        years_since_launch = current_year - launch_year
        years_missed = min(years_eligible_by_age, years_since_launch)
        
    # We only assume missed value for recurring schemes, or 1-time schemes if they never claimed it.
    # For now, default to recurring loss.
    missed_val = (years_missed * benefit_val) if is_recurring else 0.0
    
    reason = f"Did not apply since becoming eligible {int(years_missed)} years ago." if missed_val > 0 else ""
    
    return {
        "opportunity_name": opp_name,
        "eligible_since": str(int(current_year - years_missed)) if years_missed > 0 else str(current_year),
        "benefit_value": benefit_val,
        "missed_value": missed_val,
        "reason_missed": reason,
        "future_loss_risk": benefit_val
    }

def aggregate_missed_values(missed_opps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregates all missed values across multiple opportunities.
    """
    hist = sum(o['missed_value'] for o in missed_opps)
    future = sum(o['future_loss_risk'] for o in missed_opps)
    
    return {
        "historical_missed_value": hist,
        "current_missed_value": future, # Treating future risk as current liability
        "future_risk_value": future,
        "total_missed_value": hist + future
    }

# =================================================================
# ACTION INTELLIGENCE & UNLOCK ENGINE (Previous Layers)
# =================================================================
def calculate_unlock_value(item_name: str, item_type: str, opps_unlocked: int, estimated_val: float) -> Dict[str, Any]:
    return {
        "item": item_name,
        "type": item_type,
        "opportunities_unlocked": opps_unlocked,
        "estimated_unlock_value": estimated_val
    }

def generate_action_plan(actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    processed_actions = []
    
    for act in actions:
        dl_risk = act.get('deadline_risk', 'Low Risk')
        dl_mult = 5
        if dl_risk == 'High Risk': dl_mult = 50
        elif dl_risk == 'Medium Risk': dl_mult = 20
        elif dl_risk == 'Critical Risk': dl_mult = 0
        
        effort = act.get('effort', 'Medium')
        effort_mult = 1.0
        if effort == 'Low': effort_mult = 1.5
        elif effort == 'High': effort_mult = 0.5
        
        unlock_val = act.get('unlock_value', 0.0)
        opps = act.get('opps_unlocked', 0)
        readiness_imp = act.get('readiness_improvement', 0.0)
        
        score = (unlock_val / 1000) * 0.40
        score += (opps * 10) * 0.30
        score += dl_mult * 0.20
        score += readiness_imp * 0.10
        score = score * effort_mult
        
        priority = "Low"
        if score > 50: priority = "High"
        elif score > 20: priority = "Medium"
        if dl_risk == 'Critical Risk': priority = "Unfeasible"
        
        processed_actions.append({
            "action": act["action"],
            "priority": priority,
            "numeric_score": round(score, 2),
            "impact": f"Unlocks {opps} schemes",
            "estimated_unlock_value": unlock_val,
            "effort": effort,
            "official_link": act.get("official_link", "")
        })
        
    processed_actions.sort(key=lambda x: x["numeric_score"], reverse=True)
    return processed_actions
