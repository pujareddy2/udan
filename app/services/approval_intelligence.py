from typing import Dict, Any, List
from pydantic import BaseModel

class SuccessSimulator(BaseModel):
    current_prob: float
    potential_prob: float

class ApprovalPredictionResult(BaseModel):
    approval_probability: float
    level: str
    missing_items: List[str]
    improvement_actions: List[str]
    success_simulator: SuccessSimulator

class ApprovalIntelligenceEngine:
    """
    STAGE 14B: Approval Intelligence Engine
    Calculates the exact probability of an application being approved.
    """

    def calculate_approval_probability(self, opp_data: Dict[str, Any], user_profile: Dict[str, Any]) -> ApprovalPredictionResult:
        
        # 1. Gather Factors
        eligibility_score = opp_data.get("eligibility_score", 0.0) # 30%
        readiness_score = opp_data.get("readiness_score", 0.0) # 25%
        doc_health = self._calculate_document_health(user_profile.get("documents", [])) # 20%
        profile_completeness = user_profile.get("completeness", 0.0) # 10%
        verification_status = 100.0 if user_profile.get("is_verified") else 0.0 # 10%
        competition_score = opp_data.get("competition_index", 50.0) # 5% (lower competition = higher prob)

        # 2. Base Formula
        base_prob = self._run_formula(
            eligibility_score, 
            readiness_score, 
            doc_health, 
            profile_completeness, 
            verification_status, 
            competition_score
        )

        # 3. Simulator (What if missing docs are uploaded?)
        missing_docs = opp_data.get("missing_documents", [])
        potential_prob = base_prob
        if missing_docs:
            # Simulate 100% doc health and 100% readiness
            potential_prob = self._run_formula(
                eligibility_score, 
                100.0, # Simulated Readiness
                100.0, # Simulated Doc Health
                profile_completeness, 
                verification_status, 
                competition_score
            )

        # 4. Level Assignment
        level = self._assign_level(base_prob)
        
        # 5. Improvement Actions
        actions = []
        if missing_docs:
            actions.append(f"Upload {missing_docs[0]} for a +{int(potential_prob - base_prob)}% boost")
        if not user_profile.get("is_verified"):
            actions.append("Complete Aadhar verification for a +10% boost")

        return ApprovalPredictionResult(
            approval_probability=round(base_prob, 1),
            level=level,
            missing_items=missing_docs,
            improvement_actions=actions,
            success_simulator=SuccessSimulator(
                current_prob=round(base_prob, 1),
                potential_prob=round(potential_prob, 1)
            )
        )

    def _run_formula(self, elig: float, readi: float, docs: float, prof: float, verif: float, comp: float) -> float:
        comp_factor = 100 - comp # If competition is 80 (high), factor is 20 (low prob gain)
        score = (elig * 0.30) + (readi * 0.25) + (docs * 0.20) + (prof * 0.10) + (verif * 0.10) + (comp_factor * 0.05)
        return min(max(score, 0.0), 100.0)

    def _calculate_document_health(self, documents: List[Dict[str, Any]]) -> float:
        if not documents: return 0.0
        valid_docs = [d for d in documents if not d.get("is_expired")]
        return (len(valid_docs) / len(documents)) * 100.0

    def _assign_level(self, score: float) -> str:
        if score >= 90: return "Very High"
        if score >= 75: return "High"
        if score >= 60: return "Medium"
        if score >= 40: return "Low"
        return "Very Low"
