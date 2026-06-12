from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

# ==========================================
# 1. OUTPUT SCHEMAS
# ==========================================
class NotificationMetrics(BaseModel):
    value: float
    probability: float

class NotificationAction(BaseModel):
    text: str
    link: str

class ActionableNotification(BaseModel):
    id: str
    type: str
    priority: str
    title: str
    message: str
    metrics: NotificationMetrics
    action: NotificationAction
    created_at: str

class NotificationDigestContent(BaseModel):
    active: bool
    content: Optional[str] = None

class NotificationDashboardPayload(BaseModel):
    summary: Dict[str, int]
    notifications: List[ActionableNotification]
    digest: NotificationDigestContent

# ==========================================
# 2. NOTIFICATION ENGINE
# ==========================================
class IntelligentNotificationEngine:
    """
    STAGE 18: The Intelligent Notification Engine
    Transforms raw backend events into personalized, action-oriented Financial Alerts.
    """

    def generate_notification(
        self, 
        event_type: str, 
        opportunity: Dict[str, Any], 
        days_to_deadline: Optional[int],
        user_behavior: Dict[str, Any]
    ) -> Optional[ActionableNotification]:
        """
        Takes an event and returns a fully formatted Notification, 
        unless it is caught by the Anti-Spam throttle.
        """
        
        opp_name = opportunity.get("title", "Unknown Opportunity")
        value = opportunity.get("financial_value", 0.0)
        prob = opportunity.get("approval_probability", 50.0)
        missing_docs = opportunity.get("missing_documents", [])

        # 1. Priority Routing Matrix
        priority = self._assign_priority(event_type, days_to_deadline, value, missing_docs)

        # 2. Anti-Spam Engine
        if not self._check_anti_spam(priority, user_behavior):
            return None # Sent to Digest queue instead

        # 3. Content Generators
        title, message = self._generate_content(event_type, opp_name, value, days_to_deadline, missing_docs)
        action_text, action_link = self._generate_action(event_type, missing_docs)

        return ActionableNotification(
            id=f"notif_{datetime.utcnow().timestamp()}",
            type=event_type,
            priority=priority,
            title=title,
            message=message,
            metrics=NotificationMetrics(value=value, probability=prob),
            action=NotificationAction(text=action_text, link=action_link),
            created_at=datetime.utcnow().isoformat()
        )

    # --- SUB ENGINES ---

    def _assign_priority(self, event_type: str, days_to_deadline: Optional[int], value: float, missing_docs: List[str]) -> str:
        """Engine 11: Priority Routing Matrix"""
        
        # P0 Rules
        if days_to_deadline is not None and days_to_deadline <= 3:
            return "P0"
        if event_type == "APPLICATION_REJECTED":
            return "P0"
            
        # P1 Rules
        if days_to_deadline is not None and days_to_deadline <= 7:
            return "P1"
        if event_type == "NEW_MATCH" and value >= 50000:
            return "P1"
        if event_type == "DOCUMENT_MISSING" and len(missing_docs) > 0:
            return "P1"
            
        # P2 Rules
        if event_type == "READINESS_CHANGE":
            return "P2"
        if days_to_deadline is not None and days_to_deadline <= 15:
            return "P2"
            
        # P3 Rules
        return "P3"

    def _check_anti_spam(self, priority: str, behavior: Dict[str, Any]) -> bool:
        """Engine 12: Anti-Spam Engine
        Prevents user fatigue by blocking alerts if daily limits are reached.
        """
        p0_count = behavior.get("daily_p0_count", 0)
        p1_count = behavior.get("daily_p1_count", 0)
        
        if priority == "P0" and p0_count >= 2:
            return False # Queue for digest
            
        if priority == "P1" and p1_count >= 3:
            return False # Queue for digest
            
        if priority == "P3":
            # Highly limit P3 noise
            if p1_count > 0 or p0_count > 0:
                return False
                
        return True

    def _generate_content(self, event_type: str, opp_name: str, value: float, days: Optional[int], missing_docs: List[str]) -> tuple[str, str]:
        """Engine 14: Actionable Message Generator"""
        
        val_str = f"₹{value:,.0f}"
        
        if event_type == "DEADLINE_ALERT" and days is not None:
            return f"Deadline Approaching: {opp_name}", f"You have {days} Days left to apply for {opp_name}. Do not miss this {val_str} benefit."
            
        if event_type == "VALUE_UNLOCK":
            return f"Value Unlocked!", f"Uploading your document just unlocked {val_str} in potential value across new opportunities."
            
        if event_type == "DOCUMENT_MISSING" and missing_docs:
            return f"Document Missing", f"Your missing {missing_docs[0]} is blocking {val_str}. Let's fix this now."
            
        if event_type == "FUTURE_RISK":
            return f"Future Risk Warning", f"Warning: You may miss {val_str} next month if your {missing_docs[0]} is not uploaded."
            
        if event_type == "NEW_MATCH":
            return f"New Match: {opp_name}", f"You are now eligible for {opp_name}. Potential Benefit: {val_str}."

        return f"Update: {opp_name}", "There has been an update to your opportunity profile."

    def _generate_action(self, event_type: str, missing_docs: List[str]) -> tuple[str, str]:
        if "DOCUMENT" in event_type or "RISK" in event_type:
            doc = missing_docs[0] if missing_docs else "Document"
            return f"Upload {doc}", "/wallet/documents/upload"
            
        return "Apply Now", "/wallet/apply"
