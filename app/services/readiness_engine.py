from typing import Dict, Any, List, Optional
from pydantic import BaseModel

# ==========================================
# 1. OUTPUT SCHEMAS
# ==========================================
class ReadinessImpact(BaseModel):
    readiness_gain: float
    opportunities_unlocked: int
    potential_value_unlocked: float

class ReadinessRecommendation(BaseModel):
    missing_item: str
    action_required: str
    impact: ReadinessImpact

class UserReadinessResult(BaseModel):
    overall_readiness: float
    profile_readiness: float
    document_readiness: float
    skill_readiness: float
    business_readiness: float
    application_readiness: float
    verification_readiness: float
    recommendations: List[ReadinessRecommendation]
    unlockable_opportunities: int
    potential_value: float

# ==========================================
# 2. READINESS ENGINE
# ==========================================
class ReadinessEngine:
    """
    STAGE 11: The Opportunity Readiness Engine.
    Answers: "How prepared am I to apply right now?"
    """
    
    def calculate_readiness(
        self, 
        user_module: str, 
        user_profile: Dict[str, Any], 
        user_documents: List[str], 
        user_skills: List[str], 
        eligible_opportunities: List[Dict[str, Any]]
    ) -> UserReadinessResult:
        
        # 1. Extract Global Requirements
        all_required_docs = set()
        all_required_skills = set()
        total_potential_value = 0.0
        
        for opp in eligible_opportunities:
            all_required_docs.update(opp.get("required_documents", []))
            all_required_skills.update(opp.get("required_skills", []))
            total_potential_value += opp.get("financial_value", 0.0)

        # 2. Sub-Engines Calculate Raw Scores
        doc_score, missing_docs = self._calculate_document_readiness(user_documents, list(all_required_docs))
        skill_score, missing_skills = self._calculate_skill_readiness(user_skills, list(all_required_skills))
        
        # Mock other engines for now
        prof_score = 90.0 if user_profile else 0.0
        bus_score = 100.0 if user_profile.get("is_business_registered") else 0.0
        ver_score = 100.0 if user_profile.get("is_kyc_verified") else 50.0
        app_score = 80.0 # Assumes mostly online forms

        # 3. Apply Module Weighting
        overall = self._apply_module_weights(user_module.lower(), prof_score, doc_score, skill_score, bus_score, app_score, ver_score)
        
        # 4. Value Impact Engine
        recommendations = self._generate_value_impact_recommendations(
            missing_docs, 
            missing_skills, 
            eligible_opportunities
        )
        
        # 5. Summarize
        unlockable_opps = sum(1 for rec in recommendations if rec.impact.opportunities_unlocked > 0)
        
        return UserReadinessResult(
            overall_readiness=round(overall, 2),
            profile_readiness=prof_score,
            document_readiness=doc_score,
            skill_readiness=skill_score,
            business_readiness=bus_score,
            application_readiness=app_score,
            verification_readiness=ver_score,
            recommendations=recommendations,
            unlockable_opportunities=unlockable_opps,
            potential_value=total_potential_value
        )

    # --- SUB ENGINES ---

    def _calculate_document_readiness(self, user_docs: List[str], required_docs: List[str]) -> tuple[float, List[str]]:
        if not required_docs:
            return 100.0, []
            
        user_lower = [d.lower() for d in user_docs]
        missing = [d for d in required_docs if d.lower() not in user_lower]
        
        score = ((len(required_docs) - len(missing)) / len(required_docs)) * 100
        
        # Critical Penalties
        if "aadhaar" in [m.lower() for m in missing]:
            score = min(score, 70.0)
            
        return round(score, 2), missing

    def _calculate_skill_readiness(self, user_skills: List[str], required_skills: List[str]) -> tuple[float, List[str]]:
        if not required_skills:
            return 100.0, []
            
        user_lower = [s.lower() for s in user_skills]
        missing = [s for s in required_skills if s.lower() not in user_lower]
        
        score = ((len(required_skills) - len(missing)) / len(required_skills)) * 100
        return round(score, 2), missing

    # --- WEIGHTING ENGINE ---

    def _apply_module_weights(self, module: str, prof: float, doc: float, skill: float, bus: float, app: float, ver: float) -> float:
        if module == "student":
            return (prof * 0.20) + (doc * 0.35) + (skill * 0.20) + (app * 0.15) + (ver * 0.10)
        elif module == "farmer":
            return (prof * 0.20) + (doc * 0.40) + (app * 0.20) + (ver * 0.20)
        elif module == "job seeker":
            return (prof * 0.20) + (doc * 0.20) + (skill * 0.35) + (app * 0.25)
        elif module == "entrepreneur" or module == "women entrepreneur":
            return (bus * 0.40) + (doc * 0.30) + (app * 0.20) + (ver * 0.10)
        elif module == "startup":
            return (bus * 0.40) + (doc * 0.25) + (bus * 0.20) + (app * 0.15) # Startup has distinct business chunks
        elif module == "senior citizen":
            return (prof * 0.25) + (doc * 0.45) + (ver * 0.30)
            
        # Fallback average
        return (prof + doc + skill + bus + app + ver) / 6.0

    # --- VALUE IMPACT ENGINE ---

    def _generate_value_impact_recommendations(self, missing_docs: List[str], missing_skills: List[str], opportunities: List[Dict[str, Any]]) -> List[ReadinessRecommendation]:
        """Calculates exactly how much money and how many schemes are lost due to a single missing item."""
        recommendations = []
        
        # Analyze missing docs
        for doc in missing_docs:
            blocked_count = 0
            blocked_value = 0.0
            
            for opp in opportunities:
                if doc.lower() in [d.lower() for d in opp.get("required_documents", [])]:
                    blocked_count += 1
                    blocked_value += opp.get("financial_value", 0.0)
                    
            if blocked_count > 0:
                recommendations.append(ReadinessRecommendation(
                    missing_item=doc,
                    action_required=f"Upload {doc}",
                    impact=ReadinessImpact(
                        readiness_gain=15.0, # Mock static gain
                        opportunities_unlocked=blocked_count,
                        potential_value_unlocked=blocked_value
                    )
                ))
                
        # (Similar loop for missing skills can be added here)
        
        # Sort recommendations by highest value impact
        recommendations.sort(key=lambda x: x.impact.potential_value_unlocked, reverse=True)
        return recommendations
