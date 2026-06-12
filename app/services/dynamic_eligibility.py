from typing import Dict, Any, List, Optional
from pydantic import BaseModel

# ==========================================
# 1. OUTPUT SCHEMAS
# ==========================================
class DynamicQuestion(BaseModel):
    field: str
    question: str
    type: str = "boolean"
    priority_score: float

class DynamicSession(BaseModel):
    intro_text: str
    questions: List[DynamicQuestion]
    total_opportunities_unlocked: int

# ==========================================
# 2. DYNAMIC ELIGIBILITY ENGINE
# ==========================================
class DynamicEligibilityEngine:
    """
    STAGE 10: Intelligent Clarification Layer
    Optimizes missing fields to ask the absolute highest-impact questions (Max 3).
    """
    
    def __init__(self):
        # Mocking the DynamicQuestionBank database
        self.question_bank = {
            "land_ownership": {"q": "Is the agricultural land registered in your name?", "penalty": 2},
            "pm_kisan_enrolled": {"q": "Are you currently enrolled in PM Kisan?", "penalty": 2},
            "cgpa": {"q": "What is your current CGPA?", "penalty": 4},
            "dpiit": {"q": "Is your startup officially registered with DPIIT?", "penalty": 3},
            "income": {"q": "What is your annual family income?", "penalty": 4},
            "experience_years": {"q": "How many years of professional experience do you have?", "penalty": 3}
        }
        
        # Mocking the Database Memory (UserQuestionAnswer)
        self.user_memory = ["income"] # Assume user already answered income in a past session

    def generate_session(self, user_module: str, user_documents: List[str], missing_fields_from_stage9: List[Dict[str, Any]]) -> DynamicSession:
        """
        Takes the raw missing fields from Stage 9 Eligibility Engine.
        missing_fields format: [{"field": "land_ownership", "unlock_count": 12, "value": 20000}]
        """
        
        # 1. Smart Skipping Engine (Filter Known Data)
        filtered_fields = self._smart_skip(missing_fields_from_stage9, user_documents)
        
        # 2. Prioritization Engine
        scored_questions = []
        total_unlocks = 0
        
        for item in filtered_fields:
            field = item["field"]
            
            # Module Enforcement (Don't ask Farmers about CGPA)
            if not self._is_relevant_to_module(field, user_module):
                continue
                
            # Score it
            score = self._calculate_priority_score(item)
            bank_data = self.question_bank.get(field, {"q": f"Please provide your {field}.", "penalty": 5})
            
            scored_questions.append(DynamicQuestion(
                field=field,
                question=bank_data["q"],
                priority_score=score
            ))
            total_unlocks += item.get("unlock_count", 0)

        # 3. Sort & Trim (Max 3)
        scored_questions.sort(key=lambda x: x.priority_score, reverse=True)
        top_3 = scored_questions[:3]

        # 4. Conversational Engine
        intro = self._generate_intro(len(top_3), total_unlocks)
        
        return DynamicSession(
            intro_text=intro,
            questions=top_3,
            total_opportunities_unlocked=total_unlocks
        )

    # --- ENGINES ---

    def _smart_skip(self, missing_fields: List[Dict[str, Any]], docs: List[str]) -> List[Dict[str, Any]]:
        """Removes fields if the user has already answered them, or if we can infer from documents."""
        docs_lower = [d.lower() for d in docs]
        valid = []
        
        for item in missing_fields:
            field = item["field"]
            
            # Skip if in DB Memory
            if field in self.user_memory:
                continue
                
            # Document Inference
            if field == "land_ownership" and "land passbook" in docs_lower:
                continue
            if field == "dpiit" and "dpiit certificate" in docs_lower:
                continue
                
            valid.append(item)
            
        return valid

    def _calculate_priority_score(self, item: Dict[str, Any]) -> float:
        """
        Priority Score = (40% * Conf) + (30% * Unlocks) + (20% * Value) + (10% * Readiness) - Penalty
        """
        conf_gain = item.get("confidence_gain", 50)
        unlocks = item.get("unlock_count", 1) * 10 # Normalizing
        value = min(item.get("value", 0) / 1000, 100) # Normalizing
        readiness = 20 # Static for mock
        
        bank_data = self.question_bank.get(item["field"], {"penalty": 5})
        penalty = bank_data["penalty"]
        
        score = (0.40 * conf_gain) + (0.30 * unlocks) + (0.20 * value) + (0.10 * readiness) - penalty
        return round(score, 2)

    def _is_relevant_to_module(self, field: str, module: str) -> bool:
        """Strict module siloing."""
        module = module.lower()
        if module == "farmer" and field in ["cgpa", "dpiit", "experience_years"]: return False
        if module == "student" and field in ["land_ownership", "pm_kisan_enrolled"]: return False
        return True

    def _generate_intro(self, question_count: int, unlock_count: int) -> str:
        if question_count == 0:
            return "Your profile is fully complete! Let's view your opportunities."
        return f"We found {unlock_count} opportunities that perfectly match your profile! We just need {question_count} quick details to unlock them:"
