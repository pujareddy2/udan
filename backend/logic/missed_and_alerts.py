from typing import Dict, Any, List, Callable
from datetime import datetime, timedelta

def missed(profile: Dict[str, Any], opportunities: List[Dict[str, Any]], check_eligibility: Callable) -> List[Dict[str, Any]]:
    """
    Finds opportunities that are no longer active but for which the user was eligible.
    Creates a 'regret hook' by analyzing what could have been.
    """
    missed_opps = []
    
    for opp in opportunities:
        is_active = opp.get("is_active")
        # Handle actual boolean or string variants from CSVs
        if is_active is False or str(is_active).lower() == "false":
            try:
                eligibility_result = check_eligibility(profile, opp)
                if eligibility_result and eligibility_result.get("verdict") == "eligible":
                    # Make a copy to avoid modifying the original data store object
                    opp_copy = opp.copy()
                    opp_copy["_eligibility"] = eligibility_result
                    missed_opps.append(opp_copy)
            except Exception as e:
                print(f"Eligibility check failed for opp '{opp.get('title')}': {e}")
                pass
                
    return missed_opps

def alerts(profile: Dict[str, Any], opportunities: List[Dict[str, Any]], within_days: int = 30) -> List[Dict[str, Any]]:
    """
    Finds active opportunities closing within a specific number of days.
    """
    alert_list = []
    today = datetime.now().date()
    target_date = today + timedelta(days=within_days)
    
    for opp in opportunities:
        is_active = opp.get("is_active")
        if is_active is False or str(is_active).lower() == "false":
            continue
            
        close_date_str = opp.get("close_date")
        if not close_date_str or str(close_date_str).strip() == "":
            continue # Skip open-ended / rolling opportunities
            
        try:
            close_date = datetime.strptime(str(close_date_str).strip(), "%Y-%m-%d").date()
        except ValueError:
            continue # Invalid or empty date format
            
        # Already expired (handled by missed engine if eligible)
        if close_date < today:
            continue 
            
        if today <= close_date <= target_date:
            days_left = (close_date - today).days
            
            if days_left == 0:
                msg_time = "TODAY"
            elif days_left == 1:
                msg_time = "TOMORROW"
            else:
                msg_time = f"in {days_left} days"
                
            message = f"Opportunity is closing {msg_time}. Don't miss it — apply now!"
            
            alert_list.append({
                "title": opp.get("title", "Unknown Opportunity"),
                "close_date": close_date_str,
                "days_left": days_left,
                "message": message
            })
            
    # Sort alerts soonest first
    alert_list.sort(key=lambda x: x["days_left"])
    return alert_list
