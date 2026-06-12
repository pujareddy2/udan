from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

# ==========================================
# 1. OUTPUT SCHEMAS
# ==========================================
class ValueSummary(BaseModel):
    eligible_value: float
    potential_value: float
    protected_value: float
    missed_value: float
    recovery_value: float
    total_opportunities: int

class ValueForecast(BaseModel):
    days_30: float
    days_90: float
    days_180: float

class TopPriority(BaseModel):
    name: str
    value: float
    reason: str
    rank_score: float

class DocumentImpact(BaseModel):
    document: str
    blocked_value: float

class UserValueDashboard(BaseModel):
    summary: ValueSummary
    forecast: ValueForecast
    top_priorities: List[TopPriority]
    document_impacts: List[DocumentImpact]

# ==========================================
# 2. VALUE ENGINE
# ==========================================
class ValueEngine:
    """
    STAGE 14: The Value Engine
    Translates Opportunities into Financial Velocity.
    """

    def generate_value_summary(
        self, 
        eligible_opps: List[Dict[str, Any]], 
        potential_opps: List[Dict[str, Any]], 
        missed_opps: List[Dict[str, Any]], 
        protected_opps: List[Dict[str, Any]],
        missing_docs: List[str]
    ) -> UserValueDashboard:
        
        # 1. Core State Calculators
        eligible_value = sum(opp.get("financial_value", 0.0) for opp in eligible_opps)
        potential_value = sum(opp.get("financial_value", 0.0) for opp in potential_opps)
        protected_value = sum(opp.get("financial_value", 0.0) for opp in protected_opps)
        missed_value = sum(opp.get("financial_value", 0.0) for opp in missed_opps)
        
        # Assume Recovery Value is 50% of Potential Value realistically achieved
        recovery_value = potential_value * 0.5 
        
        total_opps = len(eligible_opps) + len(potential_opps) + len(protected_opps) + len(missed_opps)

        # 2. Document Impact Engine
        doc_impacts = self._calculate_document_impacts(missing_docs, potential_opps)

        # 3. Value Prioritization Engine
        top_priorities = self._calculate_priorities(eligible_opps + potential_opps)

        # 4. Forecast Engine
        forecast = self._calculate_forecast(eligible_value, recovery_value)

        return UserValueDashboard(
            summary=ValueSummary(
                eligible_value=eligible_value,
                potential_value=potential_value,
                protected_value=protected_value,
                missed_value=missed_value,
                recovery_value=recovery_value,
                total_opportunities=total_opps
            ),
            forecast=forecast,
            top_priorities=top_priorities,
            document_impacts=doc_impacts
        )

    # --- SUB ENGINES ---

    def _calculate_document_impacts(self, missing_docs: List[str], potential_opps: List[Dict[str, Any]]) -> List[DocumentImpact]:
        """Calculates exactly how much value is trapped behind each missing document."""
        impacts = []
        for doc in missing_docs:
            blocked_val = 0.0
            for opp in potential_opps:
                if doc.lower() in [d.lower() for d in opp.get("required_documents", [])]:
                    blocked_val += opp.get("financial_value", 0.0)
            
            if blocked_val > 0:
                impacts.append(DocumentImpact(document=doc, blocked_value=blocked_val))
                
        # Sort by biggest blocker
        impacts.sort(key=lambda x: x.blocked_value, reverse=True)
        return impacts

    def _calculate_priorities(self, opps: List[Dict[str, Any]]) -> List[TopPriority]:
        """
        Rank Score = (Financial Value * Probability * Readiness) / Difficulty
        """
        priorities = []
        for opp in opps:
            value = opp.get("financial_value", 0.0)
            if value <= 0:
                continue
                
            probability = 0.8 # Mock: probability of success
            readiness = opp.get("readiness_score", 50.0) / 100.0
            difficulty = 2.0 # Mock: 1 to 5 scale
            
            rank = (value * probability * readiness) / difficulty
            
            reason = ""
            if readiness > 0.8:
                reason = "High readiness, apply immediately."
            else:
                reason = "High value, complete missing documents."
                
            priorities.append(TopPriority(
                name=opp.get("title", "Unknown Opportunity"),
                value=value,
                reason=reason,
                rank_score=round(rank, 2)
            ))
            
        priorities.sort(key=lambda x: x.rank_score, reverse=True)
        return priorities[:5] # Return top 5

    def _calculate_forecast(self, current_eligible: float, recovery_target: float) -> ValueForecast:
        """Predicts the financial trajectory over time."""
        # 30 Days: Assume user captures 30% of recovery value
        d30 = current_eligible + (recovery_target * 0.30)
        # 90 Days: Assume user captures 70% of recovery value
        d90 = current_eligible + (recovery_target * 0.70)
        # 180 Days: Assume full recovery + organic platform growth
        d180 = current_eligible + recovery_target + (current_eligible * 0.10)
        
        return ValueForecast(
            days_30=round(d30, 2),
            days_90=round(d90, 2),
            days_180=round(d180, 2)
        )
