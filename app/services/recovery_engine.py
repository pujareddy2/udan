from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

# ==========================================
# 1. OUTPUT SCHEMAS
# ==========================================
class RootCauseAnalysis(BaseModel):
    primary_cause: str
    details: str

class FinancialImpact(BaseModel):
    value_lost: float
    future_opportunities_protected: int
    future_value_protected: float

class RecoveryActionPlan(BaseModel):
    do_first: str
    success_probability: float
    roadmap: List[str]

class SimilarOpportunity(BaseModel):
    name: str
    deadline: str

class RecoveryStrategyPlan(BaseModel):
    opportunity_name: str
    root_cause_analysis: RootCauseAnalysis
    financial_impact: FinancialImpact
    emotional_impact: str
    recovery_action_plan: RecoveryActionPlan
    similar_opportunities: List[SimilarOpportunity]

# ==========================================
# 2. RECOVERY ENGINE
# ==========================================
class RecoveryEngine:
    """
    STAGE 17: The Recovery Engine
    Transforms a Missed Opportunity into a Future Protection Plan.
    """

    def generate_recovery_strategy(
        self, 
        opportunity: Dict[str, Any],
        user_missed_count: int,
        missing_docs: List[str],
        future_blocked_opps: List[Dict[str, Any]],
        similar_opps_pool: List[Dict[str, Any]]
    ) -> RecoveryStrategyPlan:
        
        opp_name = opportunity.get("title", "Unknown Opportunity")
        value_lost = opportunity.get("financial_value", 0.0)

        # 1. Root Cause Engine
        cause, details = self._determine_root_cause(opportunity, missing_docs)

        # 2. Future Protection Engine (The core psychological hook)
        future_opps_protected = len(future_blocked_opps)
        future_value_protected = sum(o.get("financial_value", 0.0) for o in future_blocked_opps)

        # 3. Emotional Translation Engine
        emotional_msg = self._generate_emotional_impact(
            value_lost, future_value_protected, cause
        )

        # 4. Roadmap Engine
        do_first, roadmap = self._generate_roadmap(cause, missing_docs, opp_name)
        
        # 5. Behavior Analytics Engine
        success_prob = self._calculate_recovery_probability(user_missed_count, len(missing_docs))

        # 6. Similar Opportunity Engine
        similar = self._find_similar_opportunities(similar_opps_pool, opportunity.get("category", ""))

        return RecoveryStrategyPlan(
            opportunity_name=opp_name,
            root_cause_analysis=RootCauseAnalysis(
                primary_cause=cause,
                details=details
            ),
            financial_impact=FinancialImpact(
                value_lost=value_lost,
                future_opportunities_protected=future_opps_protected,
                future_value_protected=future_value_protected
            ),
            emotional_impact=emotional_msg,
            recovery_action_plan=RecoveryActionPlan(
                do_first=do_first,
                success_probability=success_prob,
                roadmap=roadmap
            ),
            similar_opportunities=similar
        )

    # --- SUB ENGINES ---

    def _determine_root_cause(self, opp: Dict[str, Any], missing_docs: List[str]) -> tuple[str, str]:
        """Engine 1: Root Cause Analysis"""
        if missing_docs:
            return "Missing Document", f"{missing_docs[0]} was not uploaded."
        
        # If it was missed but docs were there, it's likely a deadline miss or lack of awareness
        if opp.get("is_missed"):
            return "Missed Deadline", "The application deadline passed before submission."
            
        return "Incomplete Profile", "Required eligibility parameters were not provided."

    def _generate_emotional_impact(self, value_lost: float, future_value: float, cause: str) -> str:
        """Engine 16: Emotional Impact Engine"""
        cause_text = "one document was unavailable" if cause == "Missing Document" else "a deadline passed"
        
        if future_value > 0:
            return f"You missed ₹{value_lost:,.0f} because {cause_text}. Completing this requirement now will protect ₹{future_value:,.0f} in future opportunities."
        return f"You missed ₹{value_lost:,.0f} because {cause_text}. Let's fix this so it never happens again."

    def _generate_roadmap(self, cause: str, missing_docs: List[str], opp_name: str) -> tuple[str, List[str]]:
        """Engine 10: Recovery Roadmap Engine"""
        if cause == "Missing Document" and missing_docs:
            doc = missing_docs[0]
            return f"Apply for {doc}", [
                f"Step 1: Apply for {doc} via the official portal.",
                f"Step 2: Upload {doc} to Udaan Wallet.",
                "Step 3: Apply for alternative opportunities immediately."
            ]
        elif cause == "Missed Deadline":
            return "Set Calendar Alerts", [
                "Step 1: Enable Udaan push notifications.",
                "Step 2: Review upcoming deadlines in Wallet.",
                "Step 3: Apply to Similar Opportunities listed below."
            ]
        
        return "Complete Profile", [
            "Step 1: Answer pending clarification questions.",
            "Step 2: Review Eligibility updates."
        ]

    def _calculate_recovery_probability(self, user_missed_count: int, missing_doc_count: int) -> float:
        """Engine 17: Recovery Success Probability (based on Behavior Analytics)"""
        prob = 95.0
        
        # Chronic delays lower the probability of recovery
        if user_missed_count > 3:
            prob -= 20.0
        elif user_missed_count > 1:
            prob -= 10.0
            
        # Harder requirements lower probability
        if missing_doc_count > 2:
            prob -= 15.0
            
        return max(prob, 10.0)

    def _find_similar_opportunities(self, pool: List[Dict[str, Any]], category: str) -> List[SimilarOpportunity]:
        """Engine 12: Similar Opportunity Engine"""
        similar = []
        for opp in pool:
            if opp.get("category") == category and not opp.get("is_missed"):
                similar.append(SimilarOpportunity(
                    name=opp.get("title", "Alternative Opportunity"),
                    deadline=opp.get("deadline", "Upcoming")
                ))
                if len(similar) >= 2: # Max 2 alternatives
                    break
        return similar
