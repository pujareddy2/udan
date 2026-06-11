from typing import Dict, Any, List

def format_inr(value: float) -> str:
    if value >= 100000:
        return f"₹{value/100000:.1f} Lakh"
    return f"₹{int(value):,}"

def generate_digest(pending_notifications: List[Dict[str, Any]], digest_type: str = "WEEKLY") -> Dict[str, Any]:
    """
    Squashes multiple pending notifications into a single anti-spam summary payload.
    """
    if not pending_notifications:
        return None
        
    total_val_unlocked = 0.0
    total_val_at_risk = 0.0
    total_future_protected = 0.0
    new_schemes_count = 0
    missed_count = 0
    
    actions = set()
    
    for notif in pending_notifications:
        ntype = notif.get("notification_type", "")
        
        if ntype == "new_scheme" or ntype == "new_opportunity":
            new_schemes_count += 1
            total_val_unlocked += float(notif.get("benefit_value", 0))
            if "action_required" in notif and notif["action_required"] != "None":
                actions.add(notif["action_required"])
                
        elif ntype == "eligibility_change":
            total_val_unlocked += float(notif.get("benefit_value_unlocked", 0))
            
        elif ntype == "deadline_alert":
            total_val_at_risk += float(notif.get("value_at_risk", 0))
            if "recommended_actions" in notif:
                for action in notif["recommended_actions"]:
                    actions.add(action)
                    
        elif ntype == "recovery_alert":
            missed_count += 1
            rec_metrics = notif.get("recovery_metrics", {})
            total_future_protected += float(rec_metrics.get("future_value_protected", 0))
            if "action_required" in notif:
                actions.add(notif["action_required"])
                
        elif ntype == "document_alert":
            f_ctx = notif.get("financial_context", {})
            if notif.get("event") == "MISSING" or notif.get("event") == "EXPIRING_SOON":
                total_val_at_risk += float(f_ctx.get("potential_value", 0))
            elif notif.get("event") == "UPLOADED":
                total_val_unlocked += float(f_ctx.get("potential_value", 0))
    
    # Sort actions to pick top 3
    action_list = list(actions)[:3]
    
    summary = ""
    if digest_type == "DAILY":
        summary = f"You unlocked {new_schemes_count} new schemes today."
        if total_val_at_risk > 0:
            summary += " However, some deadlines require urgent attention."
    else:
        summary = f"You discovered {new_schemes_count} schemes and protected {format_inr(total_future_protected)} in future value this week."

    return {
        "digest_type": digest_type,
        "summary": summary,
        "metrics": {
            "new_opportunities_count": new_schemes_count,
            "missed_opportunities_count": missed_count,
            "available_value": total_val_unlocked,
            "value_at_risk": total_val_at_risk,
            "future_value_protected": total_future_protected
        },
        "recommended_actions": action_list
    }
