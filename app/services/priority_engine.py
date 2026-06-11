from typing import Dict, Any, List

def orchestrate_notification(notification: Dict[str, Any], user_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Master Traffic Controller: Calculates priority score, checks suppression, and routes delivery.
    """
    if not notification:
        return None
        
    ntype = notification.get("notification_type", "")
    
    # Defaults
    benefit_val = 0.0
    deadline_mult = 0.0
    readiness = 0.0
    
    priority_tier = "LOW"
    delivery_mode = "DIGEST"
    suppressed = False
    reason = "Passed to Digest"
    
    # Extract values based on type
    if ntype == "deadline_alert":
        benefit_val = float(notification.get("value_at_risk", 0))
        days = int(notification.get("days_remaining", 99))
        if days <= 3:
            deadline_mult = 1.0
        elif days <= 7:
            deadline_mult = 0.6
        elif days <= 15:
            deadline_mult = 0.3
            
    elif ntype in ["new_opportunity", "new_scheme"]:
        benefit_val = float(notification.get("benefit_value", 0))
        readiness = float(notification.get("readiness_score", notification.get("readiness", 0)))
        
    elif ntype == "recovery_alert":
        benefit_val = float(notification.get("recovery_metrics", {}).get("future_value_protected", 0))
        deadline_mult = 0.8 # Treat recovery as highly urgent
        
    elif ntype == "eligibility_change":
        benefit_val = float(notification.get("benefit_value_unlocked", 0))
        
    elif ntype == "document_alert":
        if notification.get("event") == "EXPIRING_SOON":
            deadline_mult = 1.0
        benefit_val = float(notification.get("financial_context", {}).get("potential_value", 0))
        
    # Mathematical Priority Score
    # Value is scaled (assuming 100k is a massive win)
    val_score = min((benefit_val / 100000) * 100, 100)
    
    score = (val_score * 0.4) + (deadline_mult * 100 * 0.4) + (readiness * 0.2)
    
    # Tier Routing
    if deadline_mult == 1.0 or score >= 80:
        priority_tier = "CRITICAL"
        delivery_mode = "IMMEDIATE"
        reason = "Critical urgency or extremely high value."
    elif score >= 50 or ntype == "recovery_alert":
        priority_tier = "HIGH"
        delivery_mode = "IMMEDIATE"
        reason = "High ROI action required."
    elif score >= 20 or ntype == "eligibility_change":
        priority_tier = "MEDIUM"
        delivery_mode = "DIGEST"
        reason = "Informational win, deferred to digest."
    else:
        priority_tier = "LOW"
        delivery_mode = "SILENT_LOG"
        reason = "Low priority, background update."
        
    # Basic Suppression Logic Checks
    # In a real DB, we would check if a high priority notification was sent in the last 2 hours.
    recent_high_pushes = sum(1 for h in user_history if h.get("priority_tier") in ["CRITICAL", "HIGH"] and h.get("delivered_hours_ago", 99) < 24)
    
    if priority_tier == "HIGH" and recent_high_pushes >= 2:
        suppressed = True
        delivery_mode = "DIGEST"
        reason = "Cool-down period enforced (Max 2 High-priority pushes per 24hrs)."
        
    # Never suppress critical deadlines
    if priority_tier == "CRITICAL":
        suppressed = False
        delivery_mode = "IMMEDIATE"

    return {
        "original_payload": notification,
        "routing": {
            "priority_tier": priority_tier,
            "priority_score": score,
            "delivery_mode": delivery_mode,
            "suppressed": suppressed,
            "reason": reason
        }
    }
