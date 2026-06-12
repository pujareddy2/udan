import re
import json
import difflib
from typing import Dict, Any, List, Tuple
from pydantic import BaseModel, Field

# ==========================================
# 1. CORE DATA SCHEMAS
# ==========================================
class NormalizedProfile(BaseModel):
    user_id: str
    primary_role: str
    secondary_roles: List[str]
    profile_confidence: float
    profile_completeness: float
    normalized_fields: Dict[str, Any]
    missing_fields: List[Dict[str, Any]]
    followup_questions: List[Dict[str, str]]

# ==========================================
# 2. CONFIGURATIONS & WEIGHTS
# ==========================================
INDIAN_STATES = ["Andhra Pradesh", "Telangana", "Maharashtra", "Karnataka", "Tamil Nadu", "Kerala", "Gujarat"]

MODULE_WEIGHTS = {
    "Student": {"cgpa": 30, "income": 20, "category": 20, "state": 10, "skills": 10, "degree": 10},
    "Farmer": {"land_area": 30, "state": 20, "crop_type": 20, "income": 20, "insurance": 10},
    "Job Seeker": {"qualification": 30, "skills": 30, "experience": 20, "state": 20},
    "Entrepreneur": {"business_type": 30, "investment_capacity": 30, "years_experience": 20, "state": 20},
    "Women Entrepreneur": {"shg_member": 40, "business_details": 40, "state": 20},
    "Startup": {"dpiit_status": 40, "startup_stage": 30, "industry": 30},
    "Senior Citizen": {"age": 40, "pension_status": 30, "income": 30}
}

FOLLOWUP_BANK = {
    "land_area": "How many acres of land do you currently cultivate?",
    "category": "To check your eligibility for reservation-based schemes, what is your social category (e.g., General, OBC, SC/ST)?",
    "income": "What is your approximate annual family income?",
    "shg_member": "Are you registered as a member of any Self Help Group (SHG)?",
    "dpiit_status": "Is your startup registered with DPIIT?"
}

# ==========================================
# 3. PROFILE UNDERSTANDING AGENT
# ==========================================
class ProfileUnderstandingAgent:
    """
    STAGE 2: AI Discovery Pipeline
    Converts raw unstructured text/voice inputs into a single mathematically normalized JSON profile.
    """
    
    def process_input(self, user_id: str, raw_text: str, input_type: str = "text") -> NormalizedProfile:
        # Step 1: Security
        safe_text = self._sanitize_pii(raw_text)
        
        # Step 2: Extraction via Gemini
        raw_extraction = self._call_gemini_extraction(safe_text)
        
        # Step 3: Resolution & Normalization
        primary_role, secondary_roles = self._resolve_roles(raw_extraction)
        normalized_data = self._normalize_fields(raw_extraction.get("extracted_entities", {}))
        
        # Step 4: Mathematical Scoring
        completeness, missing_fields = self._calculate_completeness(primary_role, normalized_data)
        confidence = self._calculate_confidence(primary_role, normalized_data, raw_extraction)
        
        # Step 5: Follow-up Generation
        followups = self._generate_followups(missing_fields)
        
        return NormalizedProfile(
            user_id=user_id,
            primary_role=primary_role,
            secondary_roles=secondary_roles,
            profile_confidence=confidence,
            profile_completeness=completeness,
            normalized_fields=normalized_data,
            missing_fields=missing_fields,
            followup_questions=followups
        )

    def _sanitize_pii(self, text: str) -> str:
        """Strips 12-digit Aadhaar formats before hitting the LLM."""
        return re.sub(r'\b\d{4}\s?\d{4}\s?\d{4}\b', '[REDACTED_AADHAAR]', text)

    def _call_gemini_extraction(self, text: str) -> Dict[str, Any]:
        """
        Production Prompt Strategy ensuring strict JSON from Gemini.
        Note: In production, integrate `google-genai` client here.
        """
        system_prompt = """
        You are an expert Government Scheme Profiler. Extract entities from user text.
        Return STRICT JSON format.
        Roles: [Student, Farmer, Job Seeker, Entrepreneur, Women Entrepreneur, Startup, Senior Citizen].
        {
          "primary_role": "string",
          "secondary_roles": ["string"],
          "parsing_uncertainty_flags": ["string"],
          "extracted_entities": {}
        }
        """
        # Mocking the LLM extraction for architecture logic implementation
        # Assume Gemini extracted the following:
        return {
            "primary_role": "Student",
            "secondary_roles": ["Startup"],
            "parsing_uncertainty_flags": [],
            "extracted_entities": {
                "income": "2 lakh",
                "state": "TS",
                "cgpa": "8.5"
            }
        }

    def _resolve_roles(self, extraction: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Conflict resolution logic for roles."""
        primary = extraction.get("primary_role", "Job Seeker")
        secondary = extraction.get("secondary_roles", [])
        
        # Rule: Women Entrepreneur auto-assigns Entrepreneur
        if primary == "Women Entrepreneur" and "Entrepreneur" not in secondary:
            secondary.append("Entrepreneur")
            
        # Rule: Force Senior Citizen if age > 60
        entities = extraction.get("extracted_entities", {})
        age = str(entities.get("age", ""))
        if age.isdigit() and int(age) >= 60:
            if "Senior Citizen" not in secondary and primary != "Senior Citizen":
                secondary.append("Senior Citizen")
                
        return primary, secondary

    def _normalize_fields(self, raw_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Deterministic conversion of text into backend constants."""
        normalized = {}
        
        for key, value in raw_fields.items():
            if not value:
                continue
                
            val_str = str(value).lower().strip()
            
            # Income Normalization
            if key == "income":
                clean_num = re.sub(r'[^\d.]', '', val_str)
                if not clean_num: continue
                num = float(clean_num)
                if "lakh" in val_str or "l" in val_str:
                    num *= 100000
                elif "k" in val_str or "thousand" in val_str:
                    num *= 1000
                normalized[key] = int(num)
                
            # State Normalization
            elif key == "state":
                if val_str in ["ts", "tg", "telangana"]:
                    normalized[key] = "Telangana"
                else:
                    # Fuzzy Match
                    matches = difflib.get_close_matches(val_str.title(), INDIAN_STATES, n=1, cutoff=0.6)
                    normalized[key] = matches[0] if matches else val_str.title()
                    
            # Direct Float mappings
            elif key == "cgpa":
                normalized[key] = float(re.sub(r'[^\d.]', '', val_str))
                
            else:
                normalized[key] = str(value).title()
                
        return normalized

    def _calculate_completeness(self, role: str, fields: Dict[str, Any]) -> Tuple[float, List[Dict]]:
        """Calculates exact mathematical % based on schema weights."""
        weights = MODULE_WEIGHTS.get(role, {})
        if not weights:
            return 100.0, []
            
        total_possible = sum(weights.values())
        achieved = 0.0
        missing = []
        
        for field, weight in weights.items():
            if field in fields:
                achieved += weight
            else:
                missing.append({"field": field, "weight": weight})
                
        # Sort missing by weight descending
        missing = sorted(missing, key=lambda x: x["weight"], reverse=True)
        return round((achieved / total_possible) * 100, 2), missing

    def _calculate_confidence(self, role: str, fields: Dict[str, Any], extraction: Dict[str, Any]) -> float:
        """Determines how trustworthy the parsed profile is."""
        confidence = 100.0
        
        flags = extraction.get("parsing_uncertainty_flags", [])
        confidence -= (len(flags) * 10.0)
        
        # Penalize if income is insanely high (likely error)
        income = fields.get("income", 0)
        if isinstance(income, int) and income > 100000000:
            confidence -= 20.0
            
        return max(0.0, confidence)

    def _generate_followups(self, missing_fields: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generates dynamic questions to recover high-weight missing fields."""
        questions = []
        # Target the top 2 highest weighted missing fields
        for item in missing_fields[:2]:
            field = item["field"]
            if field in FOLLOWUP_BANK:
                questions.append({"field": field, "question": FOLLOWUP_BANK[field]})
            else:
                questions.append({"field": field, "question": f"Please provide your {field.replace('_', ' ')}."})
        return questions
