import hashlib
import json
from typing import Dict, Any, List, Tuple
from pydantic import BaseModel
from app.services.profile_understanding import NormalizedProfile

# ==========================================
# 1. CORE DATA SCHEMAS
# ==========================================
class SearchContextObject(BaseModel):
    user_id: str
    personas: List[str]
    primary_intents: List[str]
    priority_categories: List[str]
    search_keywords: Dict[str, List[str]]
    context_scores: Dict[str, float]
    profile_hash: str

# ==========================================
# 2. INTENT & CATEGORY MAPPINGS
# ==========================================
PERSONA_INTENTS = {
    "High Performing Student": ["Merit Scholarships", "Fellowships", "Research Grants"],
    "Low Income Student": ["Financial Aid", "Government Grants", "Fee Reimbursement"],
    "Skill Development Student": ["Training Programs", "Internships", "Skill Certifications"],
    "Marginal Farmer": ["Financial Survival", "Crop Protection", "Direct Benefit Transfers"],
    "Small Farmer": ["Equipment Subsidy", "Agriculture Loans", "Crop Insurance"],
    "Insurance-Seeking Farmer": ["Crop Insurance Protection", "Weather Insurance"],
    "Fresh Graduate": ["Apprenticeships", "Entry Level Government Jobs"],
    "Skilling Candidate": ["Skill Development Schemes", "Training Programs"],
    "Bootstrapped Startup": ["Seed Funding", "Government Grants", "Incubation"],
    "SHG Women Entrepreneur": ["SHG Grants", "Microfinance", "Women Empowerment Schemes"],
    "Pension-Seeking Citizen": ["Old Age Pension", "Financial Security"],
    "Healthcare-Priority Citizen": ["Senior Health Schemes", "Disability Benefits", "Medical Subsidies"]
}

CATEGORY_MAP = {
    "Financial Survival": ["PM Kisan", "Subsidies"],
    "Merit Scholarships": ["Scholarships", "International Programs"],
    "Financial Aid": ["Government Schemes", "Scholarships"],
    "Training Programs": ["Skill Development", "Training Programs"],
    "Seed Funding": ["Startup India", "Innovation Grants"],
    "SHG Grants": ["Women Grants", "SHG Programs"],
    "Old Age Pension": ["Pension Schemes", "Social Welfare"]
}

# ==========================================
# 3. PROFILE CONTEXT ENGINE
# ==========================================
class ProfileContextEngine:
    """
    STAGE 3: Context & Strategy Pipeline
    Converts a normalized JSON profile into an actionable Search Strategy object.
    """
    
    def build_context(self, profile: NormalizedProfile) -> SearchContextObject:
        # Step 1: Compute Hash
        profile_hash = self._compute_hash(profile)
        
        # Step 2: Persona Generation
        personas = self._generate_personas(profile.primary_role, profile.normalized_fields)
        if not personas:
            personas = [f"Generic {profile.primary_role}"]
            
        # Step 3: Intent & Category Mapping
        intents, categories = self._map_intents_and_categories(personas)
        
        # Step 4: Context Scoring
        scores = self._calculate_context_scores(profile.normalized_fields)
        
        # Step 5: Rank Categories (Simplistic logic using scores)
        ranked_categories = self._rank_categories(categories, scores)
        
        # Step 6: Keyword Generation
        keywords = self._generate_keywords(personas, ranked_categories, profile.normalized_fields.get("state", ""))
        
        return SearchContextObject(
            user_id=profile.user_id,
            personas=personas,
            primary_intents=intents,
            priority_categories=ranked_categories,
            search_keywords=keywords,
            context_scores=scores,
            profile_hash=profile_hash
        )

    def _compute_hash(self, profile: NormalizedProfile) -> str:
        """Computes SHA-256 hash to detect changes triggering recalculation."""
        profile_dict = profile.model_dump()
        profile_str = json.dumps(profile_dict, sort_keys=True)
        return hashlib.sha256(profile_str.encode("utf-8")).hexdigest()

    def _generate_personas(self, role: str, fields: Dict[str, Any]) -> List[str]:
        """Deterministic Rule Trees for 7 Modules."""
        personas = []
        
        if role == "Student":
            cgpa = fields.get("cgpa", 0.0)
            income = fields.get("income", 9999999)
            if cgpa >= 8.0:
                personas.append("High Performing Student")
            if income < 250000:
                personas.append("Low Income Student")
            if not fields.get("skills"):
                personas.append("Skill Development Student")
                
        elif role == "Farmer":
            land = fields.get("land_area", 0.0)
            if land > 0 and land < 2.5:
                personas.append("Marginal Farmer")
            elif land >= 2.5 and land <= 5.0:
                personas.append("Small Farmer")
            if fields.get("insurance") is False:
                personas.append("Insurance-Seeking Farmer")
                
        elif role == "Job Seeker":
            exp = fields.get("experience", 0)
            if exp < 1:
                personas.append("Fresh Graduate")
            else:
                personas.append("Experienced Professional")
            if not fields.get("certifications"):
                personas.append("Skilling Candidate")
                
        elif role in ["Entrepreneur", "Startup"]:
            inv = fields.get("investment_capacity", 9999999)
            if inv < 500000:
                personas.append("Bootstrapped Startup")
                
        elif role == "Women Entrepreneur":
            if fields.get("shg_member") is True:
                personas.append("SHG Women Entrepreneur")
                
        elif role == "Senior Citizen":
            if fields.get("pension_status") is False:
                personas.append("Pension-Seeking Citizen")
            if fields.get("health_status") == "Chronic":
                personas.append("Healthcare-Priority Citizen")

        return personas

    def _map_intents_and_categories(self, personas: List[str]) -> Tuple[List[str], List[str]]:
        intents = set()
        categories = set()
        
        for persona in personas:
            p_intents = PERSONA_INTENTS.get(persona, [])
            for intent in p_intents:
                intents.add(intent)
                c_cats = CATEGORY_MAP.get(intent, ["General Schemes"])
                for cat in c_cats:
                    categories.add(cat)
                    
        return list(intents), list(categories)

    def _calculate_context_scores(self, fields: Dict[str, Any]) -> Dict[str, float]:
        """Calculates Urgency, Need, and Interest scores."""
        scores = {"need": 50.0, "urgency": 50.0, "interest": 50.0}
        
        income = fields.get("income", 500000)
        # Need scales inversely to income (1L = 90, 10L = 10)
        if income <= 100000:
            scores["need"] = 90.0
        elif income > 1000000:
            scores["need"] = 10.0
        else:
            scores["need"] = max(10.0, 100.0 - (income / 10000))
            
        # Urgency triggers
        if fields.get("insurance") is False or fields.get("pension_status") is False:
            scores["urgency"] = 90.0
            
        # Interest
        if fields.get("skills"):
            scores["interest"] = 80.0
            
        # Overall Opportunity Score
        scores["overall"] = round((scores["need"] * 0.5) + (scores["urgency"] * 0.3) + (scores["interest"] * 0.2), 2)
        
        return scores

    def _rank_categories(self, categories: List[str], scores: Dict[str, float]) -> List[str]:
        # Simple ranking based on overall score priority logic
        if scores["need"] > 80:
            # Prioritize financial schemes
            return sorted(categories, key=lambda x: "Subsidy" in x or "Pension" in x or "Aid" in x, reverse=True)
        return list(categories)

    def _generate_keywords(self, personas: List[str], categories: List[str], state: str) -> Dict[str, List[str]]:
        """Synthesizes exact query strings for Search Engines."""
        primary = []
        secondary = []
        long_tail = []
        
        state_str = f" in {state}" if state else " in India"
        
        for cat in categories:
            for persona in personas:
                p_clean = persona.replace(" Student", "").replace(" Farmer", "")
                primary.append(f"Government {cat.lower()} for {p_clean.lower()}{state_str}")
                secondary.append(f"{cat.lower()} eligibility {state_str} 2026")
                long_tail.append(f"How to apply for {cat.lower()} online{state_str} as {persona.lower()}")
                
        return {
            "primary": list(set(primary))[:5],
            "secondary": list(set(secondary))[:5],
            "long_tail": list(set(long_tail))[:5]
        }
