from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

# ==========================================
# 1. OUTPUT SCHEMAS
# ==========================================
class CoachingSummary(BaseModel):
    why_it_matters: str
    motivation_message: str

class CoachingMetrics(BaseModel):
    approval_probability: float
    application_difficulty: str
    risk_level: str
    urgency_level: str

class TimeInvestment(BaseModel):
    estimated_time: str
    approval_timeline: str

class DocumentStatus(BaseModel):
    documents_ready: int
    documents_missing: int
    missing_names: List[str]

class ActionPlan(BaseModel):
    next_best_action: str
    success_roadmap: List[str]

class ApplicationCoachingPlan(BaseModel):
    opportunity_name: str
    coaching_summary: CoachingSummary
    metrics: CoachingMetrics
    time_investment: TimeInvestment
    document_status: DocumentStatus
    action_plan: ActionPlan

# ==========================================
# 2. APPLICATION COACH AGENT
# ==========================================
class ApplicationCoachAgent:
    """
    STAGE 15: Application Coach
    Replaces "Apply Here" with deeply personalized, data-backed guidance.
    """

    def generate_coaching_plan(
        self, 
        opportunity: Dict[str, Any], 
        user_profile: Dict[str, Any], 
        user_module: str,
        eligibility_score: float, 
        readiness_score: float,
        available_docs: List[str],
        missing_docs: List[str],
        days_to_deadline: Optional[int] = None
    ) -> ApplicationCoachingPlan:
        
        opp_name = opportunity.get("title", "Unknown Opportunity")
        opp_value = opportunity.get("financial_value", 0.0)
        
        # 1. Mathematical Engines
        probability = self._calculate_approval_probability(eligibility_score, readiness_score)
        difficulty = self._calculate_difficulty(len(missing_docs), opp_value)
        risk, urgency = self._calculate_risk_and_urgency(missing_docs, days_to_deadline)
        time_inv, approval_timeline = self._estimate_time(len(missing_docs), difficulty)

        # 2. Document Readiness
        doc_status = DocumentStatus(
            documents_ready=len(available_docs),
            documents_missing=len(missing_docs),
            missing_names=missing_docs
        )

        # 3. Action Plan Engine
        roadmap = self._generate_success_roadmap(missing_docs, opp_name)
        next_action = self._determine_next_best_action(missing_docs, opp_name)

        # 4. Gemini Generative Engines (Mocked for deterministic execution)
        why_matters = self._gemini_why_it_matters(user_module, opp_name, opp_value)
        motivation = self._gemini_motivation_engine(probability, len(missing_docs), opp_value)

        return ApplicationCoachingPlan(
            opportunity_name=opp_name,
            coaching_summary=CoachingSummary(
                why_it_matters=why_matters,
                motivation_message=motivation
            ),
            metrics=CoachingMetrics(
                approval_probability=probability,
                application_difficulty=difficulty,
                risk_level=risk,
                urgency_level=urgency
            ),
            time_investment=TimeInvestment(
                estimated_time=time_inv,
                approval_timeline=approval_timeline
            ),
            document_status=doc_status,
            action_plan=ActionPlan(
                next_best_action=next_action,
                success_roadmap=roadmap
            )
        )

    # --- MATHEMATICAL ENGINES ---

    def _calculate_approval_probability(self, elig: float, readi: float) -> float:
        """Engine 2: Approval Probability.
        Assumes profile strength is baked into readiness/eligibility for this iteration.
        """
        prob = (elig * 0.50) + (readi * 0.50)
        return min(round(prob, 2), 99.0) # Cap at 99%

    def _calculate_difficulty(self, missing_count: int, value: float) -> str:
        """Engine 3: Application Difficulty"""
        if missing_count >= 5 or value > 500000:
            return "Hard"
        elif missing_count >= 2:
            return "Medium"
        return "Easy"

    def _calculate_risk_and_urgency(self, missing_docs: List[str], days_to_deadline: Optional[int]) -> tuple[str, str]:
        """Engines 9 & 10: Risk and Urgency Analysis"""
        risk = "Low"
        urgency = "Low"
        
        if days_to_deadline is not None:
            if days_to_deadline <= 3:
                urgency = "Critical"
                risk = "High" if missing_docs else "Medium"
            elif days_to_deadline <= 14:
                urgency = "High"
                risk = "Medium" if missing_docs else "Low"
                
        if len(missing_docs) >= 4:
            risk = "High"
            
        return risk, urgency

    def _estimate_time(self, missing_count: int, difficulty: str) -> tuple[str, str]:
        """Engine 6: Time Investment Engine"""
        prep_time = 15 + (missing_count * 10)
        est_time = f"{prep_time} Minutes"
        
        if difficulty == "Hard":
            app_time = "30-45 Days"
        elif difficulty == "Medium":
            app_time = "15-20 Days"
        else:
            app_time = "7-10 Days"
            
        return est_time, app_time

    # --- ACTION ENGINES ---

    def _generate_success_roadmap(self, missing_docs: List[str], opp_name: str) -> List[str]:
        """Engine 7: Success Roadmap"""
        steps = []
        step_idx = 1
        
        if missing_docs:
            steps.append(f"Step {step_idx}: Obtain missing documents ({', '.join(missing_docs)}).")
            step_idx += 1
            
        steps.append(f"Step {step_idx}: Review Eligibility constraints for {opp_name}.")
        step_idx += 1
        steps.append(f"Step {step_idx}: Submit Application on official portal.")
        step_idx += 1
        steps.append(f"Step {step_idx}: Track status in Udaan Wallet.")
        
        return steps

    def _determine_next_best_action(self, missing_docs: List[str], opp_name: str) -> str:
        """Engine 8: Next Best Action"""
        if missing_docs:
            return f"Upload your {missing_docs[0]}. It is the primary blocker for this application."
        return f"You are fully ready! Click Apply Now for {opp_name}."

    # --- GENERATIVE ENGINES (MOCKED FOR DETERMINISTIC RUN) ---

    def _gemini_why_it_matters(self, module: str, opp_name: str, value: float) -> str:
        """Engine 1: Why it matters (Simulated Gemini output)"""
        val_str = f"worth ₹{value:,.0f}" if value > 0 else "of high strategic value"
        if module.lower() == "student":
            return f"This {opp_name} can reduce your education expenses by providing support {val_str}."
        elif module.lower() == "farmer":
            return f"This {opp_name} provides direct support {val_str} to assist with your agricultural costs."
        elif module.lower() == "startup":
            return f"This {opp_name} provides funding and mentorship {val_str} to scale your business."
        return f"This opportunity provides {val_str} to support your goals."

    def _gemini_motivation_engine(self, prob: float, missing: int, value: float) -> str:
        """Engine 16: Motivation Engine (Simulated Gemini output)"""
        if missing == 0:
            return "You are 100% ready! You are an exceptionally strong candidate for this."
        elif missing == 1:
            return f"You are so close! You are only one document away from unlocking this opportunity."
        else:
            return f"Let's get to work. Fixing these {missing} documents will dramatically increase your {prob}% approval odds."
