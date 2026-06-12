from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

# ==========================================
# 1. OUTPUT SCHEMAS
# ==========================================
class TimelineImpact(BaseModel):
    value_gained: float
    readiness_gain: float

class TimelineEventModel(BaseModel):
    id: str
    category: str
    sub_type: str
    importance: str
    story_text: str
    impact: TimelineImpact
    timestamp: str

class MilestoneModel(BaseModel):
    title: str
    date: str

class PredictionModel(BaseModel):
    expected_event: str
    expected_time: str

class JourneySummary(BaseModel):
    total_value_earned: float
    total_opportunities_found: int
    total_applications_submitted: int

class TimelineDashboardPayload(BaseModel):
    journey_summary: JourneySummary
    achievements: List[MilestoneModel]
    recent_events: List[TimelineEventModel]
    predictions: List[PredictionModel]

# ==========================================
# 2. TIMELINE ENGINE
# ==========================================
class TimelineEngine:
    """
    STAGE 19: The Timeline Engine
    Converts scattered backend states into a cohesive Financial Journey.
    """

    def process_event(
        self,
        user_id: int,
        category: str,
        sub_type: str,
        metadata: Dict[str, Any],
        current_analytics: Dict[str, Any]
    ) -> TimelineDashboardPayload:
        
        # 1. Importance Routing
        importance = self._determine_importance(category, sub_type)

        # 2. Impact Calculation
        value_gain = metadata.get("value", 0.0)
        readi_gain = metadata.get("readiness_diff", 0.0)
        
        # 3. Story Generation
        story = self._generate_story(category, sub_type, metadata, value_gain, readi_gain)
        
        # 4. Construct Event
        event = TimelineEventModel(
            id=f"evt_{datetime.utcnow().timestamp()}",
            category=category,
            sub_type=sub_type,
            importance=importance,
            story_text=story,
            impact=TimelineImpact(value_gained=value_gain, readiness_gain=readi_gain),
            timestamp=datetime.utcnow().isoformat()
        )

        # 5. Milestone Detection
        milestones = self._detect_milestones(category, current_analytics, value_gain)

        # 6. Predictive Engine
        predictions = self._generate_predictions(category, sub_type, metadata)

        # 7. Mock Analytics Update
        summary = JourneySummary(
            total_value_earned=current_analytics.get("total_value", 0.0) + value_gain,
            total_opportunities_found=current_analytics.get("total_opps", 0) + (1 if category == "DISCOVERY" else 0),
            total_applications_submitted=current_analytics.get("total_apps", 0) + (1 if sub_type == "SUBMITTED" else 0)
        )

        return TimelineDashboardPayload(
            journey_summary=summary,
            achievements=milestones,
            recent_events=[event], # In reality, we'd fetch historical events from DB
            predictions=predictions
        )

    # --- SUB ENGINES ---

    def _determine_importance(self, category: str, sub_type: str) -> str:
        """Engine 3: Importance Engine"""
        critical_types = ["APPROVED", "REJECTED", "MISSED"]
        if sub_type in critical_types:
            return "Critical"
            
        high_types = ["SUBMITTED", "UPLOADED", "COMPLETED"]
        if sub_type in high_types:
            return "High"
            
        return "Medium"

    def _generate_story(self, category: str, sub_type: str, metadata: Dict[str, Any], val: float, readi: float) -> str:
        """Engine 11: Story Generation Engine"""
        opp_name = metadata.get("opportunity_name", "an opportunity")
        doc_name = metadata.get("document_name", "a document")
        
        if category == "DOCUMENT" and sub_type == "UPLOADED":
            return f"You uploaded {doc_name} and unlocked ₹{val:,.0f} in potential value."
            
        if category == "APPLICATION" and sub_type == "SUBMITTED":
            return f"You successfully submitted your application for {opp_name}."
            
        if category == "APPROVAL" and sub_type == "APPROVED":
            return f"Congratulations! Your application for {opp_name} was approved, earning you ₹{val:,.0f}."
            
        if category == "RECOVERY" and sub_type == "COMPLETED":
            return f"You successfully completed a recovery action for {opp_name}, protecting future value."
            
        if category == "DISCOVERY" and sub_type == "FOUND":
            return f"A new high-value match was found: {opp_name} worth ₹{val:,.0f}."

        return f"Event tracked: {category} - {sub_type}"

    def _detect_milestones(self, category: str, analytics: Dict[str, Any], val_gain: float) -> List[MilestoneModel]:
        """Engine 7 & 8: Milestone and Achievement Engine"""
        milestones = []
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Check Value Threshold
        curr_val = analytics.get("total_value", 0.0)
        if curr_val < 100000 and (curr_val + val_gain) >= 100000:
            milestones.append(MilestoneModel(title="₹1 Lakh Value Unlocked!", date=date_str))
            
        # Check Application Threshold
        curr_apps = analytics.get("total_apps", 0)
        if curr_apps == 0 and category == "APPLICATION":
            milestones.append(MilestoneModel(title="First Application Submitted", date=date_str))
            
        return milestones

    def _generate_predictions(self, category: str, sub_type: str, metadata: Dict[str, Any]) -> List[PredictionModel]:
        """Engine 15: Predictive Timeline Engine"""
        preds = []
        opp_name = metadata.get("opportunity_name", "Opportunity")
        
        if category == "APPLICATION" and sub_type == "SUBMITTED":
            preds.append(PredictionModel(
                expected_event=f"{opp_name} Verification Result",
                expected_time="15 Days"
            ))
            
        if category == "DOCUMENT" and sub_type == "UPLOADED":
            preds.append(PredictionModel(
                expected_event=f"Readiness Score Recalculation",
                expected_time="Immediately"
            ))
            
        return preds
