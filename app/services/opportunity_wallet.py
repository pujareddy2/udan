from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

# ==========================================
# 1. OUTPUT SCHEMAS
# ==========================================
class WalletSummary(BaseModel):
    total_opportunities: int
    ready_value: float
    blocked_value: float
    missed_value: float
    recovered_value: float

class WalletOpportunity(BaseModel):
    id: str
    name: str
    value: float
    deadline: Optional[str]
    priority_score: float
    next_best_action: str
    blocker: Optional[str] = None
    recovery_time: Optional[str] = None

class WalletBuckets(BaseModel):
    ready: List[WalletOpportunity]
    blocked: List[WalletOpportunity]
    needs_clarification: List[WalletOpportunity]
    applied: List[WalletOpportunity]
    under_review: List[WalletOpportunity]
    missed: List[WalletOpportunity]
    recovered: List[WalletOpportunity]

class MasterWalletDashboard(BaseModel):
    wallet_summary: WalletSummary
    insights: List[str]
    buckets: WalletBuckets

# ==========================================
# 2. OPPORTUNITY WALLET ENGINE
# ==========================================
class OpportunityWalletEngine:
    """
    STAGE 16: The Opportunity Wallet Engine
    The Master Dashboard synthesizer.
    """

    def generate_master_wallet(
        self, 
        user_opportunities: List[Dict[str, Any]]
    ) -> MasterWalletDashboard:
        
        buckets = {
            "ready": [],
            "blocked": [],
            "needs_clarification": [],
            "applied": [],
            "under_review": [],
            "missed": [],
            "recovered": []
        }
        
        summary_totals = {
            "ready": 0.0,
            "blocked": 0.0,
            "missed": 0.0,
            "recovered": 0.0
        }
        
        blocked_docs = set()

        # 1. Classification & Aggregation
        for opp in user_opportunities:
            bucket_name = self._classify_bucket(opp)
            
            value = opp.get("financial_value", 0.0)
            if bucket_name in summary_totals:
                summary_totals[bucket_name] += value
                
            wallet_opp = self._format_opportunity(opp, bucket_name)
            buckets[bucket_name].append(wallet_opp)
            
            if bucket_name == "blocked" and wallet_opp.blocker:
                blocked_docs.add(wallet_opp.blocker)

        # 2. Sort Buckets by Priority
        for key in buckets:
            buckets[key].sort(key=lambda x: x.priority_score, reverse=True)

        # 3. Insights Engine
        insights = self._generate_insights(
            len(buckets["ready"]), 
            summary_totals["ready"], 
            len(blocked_docs), 
            summary_totals["blocked"]
        )

        return MasterWalletDashboard(
            wallet_summary=WalletSummary(
                total_opportunities=len(user_opportunities),
                ready_value=summary_totals["ready"],
                blocked_value=summary_totals["blocked"],
                missed_value=summary_totals["missed"],
                recovered_value=summary_totals["recovered"]
            ),
            insights=insights,
            buckets=WalletBuckets(**buckets)
        )

    # --- SUB ENGINES ---

    def _classify_bucket(self, opp: Dict[str, Any]) -> str:
        """Engine 1: Wallet Classification Engine
        Deterministically forces every opp into exactly one bucket.
        """
        # Assume these fields come attached from previous stages
        eligibility = opp.get("eligibility_status", "Needs Clarification")
        readiness = opp.get("readiness_score", 0.0)
        is_applied = opp.get("is_applied", False)
        is_under_review = opp.get("is_under_review", False)
        is_missed = opp.get("is_missed", False)
        is_recovered = opp.get("is_recovered", False)

        if is_missed: return "missed"
        if is_recovered: return "recovered"
        if is_under_review: return "under_review"
        if is_applied: return "applied"
        
        if eligibility == "Needs Clarification":
            return "needs_clarification"
            
        if eligibility == "Eligible":
            if readiness >= 80.0:
                return "ready"
            else:
                return "blocked"
                
        # Default fallback
        return "needs_clarification"

    def _format_opportunity(self, opp: Dict[str, Any], bucket: str) -> WalletOpportunity:
        """Formats the raw dictionary into the Wallet schema, injecting actions."""
        action = "Click Apply Now"
        blocker = None
        recovery_time = None
        
        if bucket == "blocked":
            blocker = opp.get("missing_document", "Missing Requirements")
            action = f"Upload {blocker}"
            recovery_time = opp.get("recovery_time", "7 Days")
        elif bucket == "needs_clarification":
            action = "Answer Clarification Questions"
            
        return WalletOpportunity(
            id=opp.get("id", "UNKNOWN"),
            name=opp.get("title", "Unknown Opportunity"),
            value=opp.get("financial_value", 0.0),
            deadline=opp.get("deadline", "None"),
            priority_score=opp.get("priority_score", 50.0),
            next_best_action=action,
            blocker=blocker,
            recovery_time=recovery_time
        )

    def _generate_insights(self, ready_count: int, ready_value: float, blocked_doc_count: int, blocked_value: float) -> List[str]:
        """Engine 13: Wallet Insights Engine
        Translates raw numbers into gamified UI messages.
        """
        insights = []
        
        if ready_count > 0:
            insights.append(f"You have {ready_count} opportunities worth ₹{ready_value:,.0f} ready to apply right now.")
            
        if blocked_doc_count > 0:
            doc_str = "document is" if blocked_doc_count == 1 else "documents are"
            insights.append(f"{blocked_doc_count} missing {doc_str} blocking ₹{blocked_value:,.0f} in potential value.")
            
        if not insights:
            insights.append("Your wallet is up to date. Keep your profile updated for new matches!")
            
        return insights
