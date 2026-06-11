from typing import Dict, Any, List

def format_inr(value: float) -> str:
    if value >= 100000:
        return f"₹{value/100000:.1f} Lakh"
    return f"₹{int(value):,}"

# =================================================================
# LAYER 7 — NEW SCHEME MONITORING ENGINE (BATCH)
# =================================================================
def evaluate_new_scheme_batch(scheme: Dict[str, Any], user_evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates a single new scheme against a batch of pre-calculated user profiles.
    user_evaluations should contain dictionaries with 'is_eligible' and 'readiness_score'.
    Returns the impact analysis payload.
    """
    scheme_name = scheme.get("title", "Unknown Scheme")
    scheme_val = float(scheme.get("benefit_amount", 0.0))
    
    total_eval = len(user_evaluations)
    eligible = 0
    high_ready = 0
    
    for user_data in user_evaluations:
        if user_data.get("is_eligible", False):
            eligible += 1
            if float(user_data.get("readiness_score", 0.0)) >= 80.0:
                high_ready += 1
                
    total_val = eligible * scheme_val
    
    return {
        "scheme_name": scheme_name,
        "users_evaluated": total_eval,
        "eligible_users": eligible,
        "high_readiness_users": high_ready,
        "total_potential_value": total_val
    }

# =================================================================
# LAYER 1 — NEW OPPORTUNITY NOTIFICATION ENGINE (INDIVIDUAL)
# =================================================================
def generate_new_opportunity_notification(opp: Dict[str, Any], readiness: Dict[str, Any]) -> Dict[str, Any]:
    is_eligible = opp.get("eligible", False)
    val = float(opp.get("benefit_value", 0.0))
    r_score = float(readiness.get("overall_readiness", 0.0))
    
    if not is_eligible:
        return None
    if r_score < 60.0 and val < 5000:
        return None
        
    val_str = format_inr(val)
    title = opp.get("title", "New Opportunity Available")
    module = opp.get("module", "general")
    
    msg = f"A new {val_str} opportunity has been added. Based on your profile, you are a strong match."
    action = "Apply Now"
    if r_score < 80:
        msg = f"A new {val_str} opportunity has been added. You are missing a few requirements, but it's highly valuable."
        action = "Complete Profile"

    return {
        "notification_type": "new_scheme", # Aligned with Layer 7
        "scheme_name": title,
        "message": msg,
        "module": module,
        "benefit_value": val,
        "readiness": r_score,
        "confidence": 95 if r_score >= 80 else 75,
        "why_recommended": "You meet all criteria and have strong document readiness.",
        "required_actions": [action],
        "official_link": opp.get("official_link", "")
    }

# =================================================================
# LAYER 2 — ELIGIBILITY CHANGE NOTIFICATION ENGINE
# =================================================================
def generate_eligibility_change_notification(unlocked_opps: List[Dict[str, Any]], old_r_score: float, new_r_score: float) -> Dict[str, Any]:
    if len(unlocked_opps) == 0:
        return None
        
    total_val = sum(float(o.get('benefit_value', 0.0)) for o in unlocked_opps)
    titles = [o.get('title', 'Scheme') for o in unlocked_opps]
    
    val_str = format_inr(total_val)
    count = len(titles)
    r_increase = max(0.0, new_r_score - old_r_score)
    
    msg = f"Your recent profile update just unlocked {count} new opportunities worth {val_str}."
    
    return {
        "notification_type": "eligibility_change",
        "title": "Profile Update Successful!",
        "message": msg,
        "new_opportunities_unlocked": titles,
        "benefit_value_unlocked": total_val,
        "readiness_increase": f"+{int(r_increase)}%",
        "confidence_increase": "+15%"
    }

# =================================================================
# LAYER 3 — DEADLINE INTELLIGENCE NOTIFICATION ENGINE
# =================================================================
def generate_deadline_alert(opp: Dict[str, Any], readiness: Dict[str, Any], days_remaining: int) -> Dict[str, Any]:
    if days_remaining < 0 or days_remaining > 45:
        return None
        
    title = opp.get("title", "Opportunity")
    val = float(opp.get("benefit_value", 0.0))
    val_str = format_inr(val)
    r_score = float(readiness.get("overall_readiness", 0.0))
    
    missing_docs = readiness.get("document_readiness", {}).get("missing_documents", [])
    primary_blocker = missing_docs[0] if len(missing_docs) > 0 else "Profile Details"
    
    stage = ""
    msg = ""
    actions = []
    
    if days_remaining <= 1:
        stage = "LAST_DAY" if days_remaining == 0 else "1_DAY"
        msg = f"Final 24 Hours: Your {val_str} benefit is at risk. Apply immediately before the portal closes."
        actions = ["Apply Now"]
    elif days_remaining <= 3:
        stage = "3_DAYS"
        msg = f"Critical: The {title} portal closes in {days_remaining} days. Your readiness is {r_score}%. Complete the final steps now."
        if len(missing_docs) > 0:
            actions = [f"Upload {primary_blocker}"]
    elif days_remaining <= 7:
        stage = "7_DAYS"
        msg = f"Warning: You are 7 days away from losing {val_str}. "
        if len(missing_docs) > 0:
            msg += f"You must acquire your {primary_blocker}."
            actions = [f"Apply for {primary_blocker}"]
    elif days_remaining <= 15:
        stage = "15_DAYS"
        msg = f"Preparation Alert: {title} closes in 15 days. "
        if len(missing_docs) > 0:
            msg += f"You are missing your {primary_blocker}. Apply for it today."
            actions = [f"Apply for {primary_blocker}"]
    elif days_remaining <= 30:
        stage = "30_DAYS"
        msg = f"Reminder: 30 days left for the {val_str} {title}."
    elif days_remaining <= 45:
        stage = "45_DAYS"
        msg = f"Awareness: {title} closes next month. Prepare your documents."
        
    if not stage:
        return None
        
    return {
        "notification_type": "deadline_alert",
        "deadline_stage": stage,
        "days_remaining": days_remaining,
        "value_at_risk": val,
        "missing_items": missing_docs,
        "recommended_actions": actions,
        "official_links": [opp.get("official_link", "")],
        "message": msg
    }

# =================================================================
# LAYER 4 — DOCUMENT & CERTIFICATE INTELLIGENCE NOTIFICATION ENGINE
# =================================================================
def generate_document_intelligence_notification(doc_name: str, event_type: str, opps_blocked: int, potential_val: float, doc_kb_data: Dict[str, Any] = {}) -> Dict[str, Any]:
    val_str = format_inr(potential_val)
    msg = ""
    
    if event_type == "MISSING":
        msg = f"You are missing your {doc_name}. It is required for {opps_blocked} opportunities worth a potential unlock of {val_str}. Apply now."
    elif event_type == "EXPIRING_SOON":
        msg = f"Warning: Your {doc_name} expires in 30 days. Renew now. Failure to renew puts {opps_blocked} upcoming opportunities at risk."
    elif event_type == "UPLOADED":
        msg = f"Document Verified! Uploading your {doc_name} just unlocked {opps_blocked} new opportunities worth {val_str}."
    elif event_type == "VERIFICATION_PENDING":
        msg = f"Your {doc_name} has been uploaded. Verification is pending and expected to complete in 2 days."
        
    return {
        "notification_type": "document_alert",
        "document_name": doc_name,
        "event": event_type,
        "message": msg,
        "financial_context": {
            "opportunities_blocked": opps_blocked,
            "potential_value": potential_val
        },
        "action_guidance": doc_kb_data
    }

# =================================================================
# LAYER 5 — APPLICATION PROGRESS & TRACKING NOTIFICATION ENGINE
# =================================================================
def generate_application_tracking_notification(doc_name: str, state: str, days_pending: int = 0) -> Dict[str, Any]:
    msg = ""
    action = "None"
    
    if state == "STARTED":
        msg = f"{doc_name} Application Started."
    elif state == "PENDING":
        msg = f"Your {doc_name} application has been pending for {days_pending} days. Please update the status if you have received it."
        action = "UPDATE_STATUS"
    elif state == "APPROVED":
        msg = f"{doc_name} Approved! Upload the document now to unlock your opportunities."
        action = "UPLOAD_DOCUMENT"
        
    return {
        "notification_type": "application_tracking",
        "document_name": doc_name,
        "current_state": state,
        "message": msg,
        "required_user_action": action
    }

# =================================================================
# LAYER 6 — MISSED OPPORTUNITY & RECOVERY NOTIFICATION ENGINE
# =================================================================
def generate_recovery_notification(missed_opp_name: str, missed_val: float, root_cause: str, future_val_protected: float, alt_opps: List[str]) -> Dict[str, Any]:
    missed_val_str = format_inr(missed_val)
    future_val_str = format_inr(future_val_protected)
    
    total_pool = missed_val + future_val_protected
    recovery_score = int((future_val_protected / total_pool) * 100) if total_pool > 0 else 0
    
    msg = f"You missed {missed_val_str} on {missed_opp_name}. But by completing one action now, you can still protect {future_val_str}."
    
    return {
        "notification_type": "recovery_alert",
        "missed_opportunity": missed_opp_name,
        "root_cause": root_cause,
        "message": msg,
        "recovery_metrics": {
            "missed_value": missed_val,
            "future_value_protected": future_val_protected,
            "recovery_score": recovery_score
        },
        "action_required": f"Resolve: {root_cause}",
        "alternative_opportunities": alt_opps
    }

# =================================================================
# WALLET NOTIFICATIONS (Legacy Wrapper)
# =================================================================
def generate_smart_notifications(wallet_data: Dict[str, Any], action_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    notifications = []
    top_action = action_data.get('top_action')
    if top_action:
        val_str = format_inr(top_action.get('estimated_unlock_value', 0))
        action_name = top_action.get('action', 'Completing this step')
        if "Upload" in action_name or "Certificate" in action_name:
            msg = f"You are one document away from unlocking {val_str} in benefits."
        elif "Answer" in action_name or "Question" in action_name:
            msg = f"Answering one question can unlock {val_str} worth of opportunities."
        else:
            msg = f"{action_name} can unlock {val_str} worth of opportunities."
        notifications.append({"type": "UNLOCK_POTENTIAL", "priority": "HIGH", "message": msg, "action_link": "/actions/top"})
        
    return notifications
