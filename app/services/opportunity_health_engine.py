from typing import Dict, Any, Tuple
from pydantic import BaseModel

class HealthScoreResult(BaseModel):
    health_score: float
    status: str
    next_action: str
    potential_value: float

class OpportunityHealthEngine:
    """
    STAGE 14C: Opportunity Health Engine
    Determines if the user should apply now, prepare, or ignore.
    """

    def calculate_health(self, opp_data: Dict[str, Any], approval_prob: float, trust_score: float) -> HealthScoreResult:
        
        # 1. Gather Factors
        value = opp_data.get("financial_value", 0.0)
        # Normalize value for the 0-100 formula (e.g. 1 Lakh = 100)
        norm_value = min((value / 100000.0) * 100.0, 100.0) # 25%
        
        readiness = opp_data.get("readiness_score", 0.0) # 20%
        
        days_to_deadline = opp_data.get("days_to_deadline", 30)
        urgency = self._calculate_urgency(days_to_deadline) # 15%
        
        comp_index = opp_data.get("competition_index", 50.0)
        comp_factor = 100 - comp_index # 5%
        
        # 2. Formula
        health = (norm_value * 0.25) + (approval_prob * 0.25) + (readiness * 0.20) + (urgency * 0.15) + (trust_score * 0.10) + (comp_factor * 0.05)
        health = min(max(health, 0.0), 100.0)
        
        # 3. Status
        status = self._assign_status(health)
        
        # 4. Action Generator
        action = self._generate_action(status, opp_data.get("missing_documents", []), days_to_deadline)

        return HealthScoreResult(
            health_score=round(health, 1),
            status=status,
            next_action=action,
            potential_value=value
        )

    def _calculate_urgency(self, days: int) -> float:
        if days <= 3: return 100.0
        if days <= 7: return 80.0
        if days <= 15: return 50.0
        if days <= 30: return 20.0
        return 0.0

    def _assign_status(self, score: float) -> str:
        if score >= 90: return "Apply Immediately"
        if score >= 75: return "High Priority"
        if score >= 60: return "Prepare First"
        if score >= 40: return "Low Priority"
        return "Not Recommended"

    def _generate_action(self, status: str, missing_docs: list, days: int) -> str:
        if status == "Apply Immediately" and not missing_docs:
            return "Submit Application"
            
        if missing_docs:
            if days <= 3:
                return f"URGENT: Upload {missing_docs[0]}"
            return f"Upload {missing_docs[0]}"
            
        return "Review Details"
