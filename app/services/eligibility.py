from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import datetime

# ==========================================
# 1. OUTPUT SCHEMAS
# ==========================================
class EligibilityCheckResult(BaseModel):
    passed: bool
    missing: bool
    weight: float
    message: str
    missing_field: Optional[str] = None

class EligibilityVerdict(BaseModel):
    opportunity_id: int
    user_id: int
    eligibility_score: float
    verdict: str # "Eligible", "Potentially Eligible", "Needs Clarification", "Not Eligible"
    missing_requirements: List[str]
    missing_documents: List[str]
    followup_questions: List[str]
    eligibility_explanation: str

# ==========================================
# 2. UNIVERSAL RULE ENGINE
# ==========================================
class EligibilityEngine:
    """
    STAGE 9: Core Decision Engine
    Mathematically parses JSON constraints to generate Deterministic Eligibility.
    """
    
    def evaluate_bulk_eligibility(self, user_profile: Dict[str, Any], user_documents: List[str], opportunities: List[Dict[str, Any]]) -> List[EligibilityVerdict]:
        results = []
        for opp in opportunities:
            results.append(self.evaluate_single_eligibility(user_profile, user_documents, opp))
        return results

    def evaluate_single_eligibility(self, user: Dict[str, Any], docs: List[str], opp: Dict[str, Any]) -> EligibilityVerdict:
        rules = opp.get("eligibility_rules", {})
        required_docs = opp.get("required_documents", [])
        
        checks = []
        
        # 1. Execute Core Checks dynamically
        if "income_max" in rules:
            checks.append(self.check_income(user.get("income"), rules["income_max"]))
        if "age_min" in rules or "age_max" in rules:
            checks.append(self.check_age(
                user.get("age"), 
                user.get("category"), 
                rules.get("age_min"), 
                rules.get("age_max"), 
                rules.get("age_relaxations", {})
            ))
        if "category" in rules:
            checks.append(self.check_category(user.get("category"), rules["category"]))
        if "state" in rules:
            checks.append(self.check_state(user.get("state"), rules["state"]))
        if "cgpa_min" in rules:
            checks.append(self.check_cgpa(user.get("cgpa"), rules["cgpa_min"]))
        if "land_area_max" in rules:
            checks.append(self.check_land(user.get("land_area"), rules["land_area_max"]))
        if "dpiit_required" in rules:
            checks.append(self.check_dpiit(user.get("is_dpiit_registered"), rules["dpiit_required"]))
            
        # 1.5 Module-Specific Checks (Job Seekers, Women Entrepreneurs, etc.)
        if "required_skills" in rules:
            checks.append(self.check_skills(user.get("skills", []), rules["required_skills"]))
        if "experience_min" in rules:
            checks.append(self.check_experience(user.get("experience_years"), rules["experience_min"]))
        if "gender" in rules:
            checks.append(self.check_gender(user.get("gender"), rules["gender"]))
            
        # 2. Document Check
        doc_check = self.check_documents(docs, required_docs)
        checks.append(doc_check)
        
        # 3. Calculate Score
        return self._compute_verdict(checks, opp, user, required_docs, doc_check)

    def _compute_verdict(self, checks: List[EligibilityCheckResult], opp: Dict[str, Any], user: Dict[str, Any], req_docs: List[str], doc_check: EligibilityCheckResult) -> EligibilityVerdict:
        total_weight = 0.0
        earned_weight = 0.0
        missing_reqs = []
        followups = []
        hard_fail = False
        
        for chk in checks:
            total_weight += chk.weight
            if chk.passed:
                earned_weight += chk.weight
            elif chk.missing:
                missing_reqs.append(chk.missing_field)
                followups.append(self._generate_followup(chk.missing_field))
            else:
                hard_fail = True
                
        # Calculate base score (0-100)
        score = (earned_weight / total_weight * 100.0) if total_weight > 0 else 100.0
        
        missing_docs = []
        if doc_check.missing:
            # specifically extract which docs are missing
            user_docs_lower = [d.lower() for d in user.get("documents", [])]
            for rd in req_docs:
                if rd.lower() not in user_docs_lower:
                    missing_docs.append(rd)
        
        # Verdict Logic
        verdict = ""
        if hard_fail:
            score = min(score, 59.0)
            verdict = "Not Eligible"
        elif missing_reqs:
            verdict = "Needs Clarification"
        elif score >= 85:
            verdict = "Eligible"
        else:
            verdict = "Potentially Eligible"
            
        # Explanation logic
        if verdict == "Eligible":
            explanation = f"You perfectly meet the criteria for {opp.get('title', 'this scheme')}."
        elif verdict == "Needs Clarification":
            explanation = f"We need {len(missing_reqs)} more details to confirm your eligibility."
        elif verdict == "Not Eligible":
            explanation = "You do not meet the strict requirements for this scheme."
        else:
            explanation = "You meet most criteria, but are missing some supporting documents."

        return EligibilityVerdict(
            opportunity_id=opp.get("id", 0),
            user_id=user.get("id", 0),
            eligibility_score=round(score, 2),
            verdict=verdict,
            missing_requirements=missing_reqs,
            missing_documents=missing_docs,
            followup_questions=followups,
            eligibility_explanation=explanation
        )

    def _generate_followup(self, field: str) -> str:
        qs = {
            "income": "What is your annual family income?",
            "age": "What is your current age?",
            "category": "What is your social category (e.g., SC/ST/OBC/General)?",
            "state": "Which state are you currently a resident of?",
            "cgpa": "What is your current CGPA?",
            "land_area": "How many acres of land do you own?",
            "dpiit": "Is your startup officially registered with DPIIT?",
            "skills": "What are your key professional skills?",
            "experience_years": "How many years of professional experience do you have?",
            "gender": "What is your gender?"
        }
        return qs.get(field, f"Could you please provide your {field}?")

    # --- DETERMINISTIC RULE CHECKERS ---

    def check_income(self, user_val: Optional[float], rule_max: float) -> EligibilityCheckResult:
        if user_val is None:
            return EligibilityCheckResult(passed=False, missing=True, weight=20.0, message="Income missing", missing_field="income")
        passed = user_val <= rule_max
        return EligibilityCheckResult(passed=passed, missing=False, weight=20.0, message="Income check" + (" passed" if passed else " failed"))

    def check_age(self, user_val: Optional[int], user_category: Optional[str], rule_min: Optional[int], rule_max: Optional[int], relaxations: Dict[str, int]) -> EligibilityCheckResult:
        if user_val is None:
            return EligibilityCheckResult(passed=False, missing=True, weight=15.0, message="Age missing", missing_field="age")
        
        passed = True
        
        # Apply Category Age Relaxation to the maximum age limit
        effective_max = rule_max
        if rule_max is not None and user_category and user_category.upper() in relaxations:
            relaxation_years = relaxations[user_category.upper()]
            effective_max = rule_max + relaxation_years

        if rule_min and user_val < rule_min: 
            passed = False
        if effective_max and user_val > effective_max: 
            passed = False
            
        message = "Age check"
        if effective_max != rule_max:
            message += f" (Relaxation of {relaxations[user_category.upper()]} years applied for {user_category.upper()})"
            
        return EligibilityCheckResult(passed=passed, missing=False, weight=15.0, message=message)

    def check_category(self, user_val: Optional[str], valid_list: List[str]) -> EligibilityCheckResult:
        if not user_val:
            return EligibilityCheckResult(passed=False, missing=True, weight=25.0, message="Category missing", missing_field="category")
        passed = user_val.upper() in [v.upper() for v in valid_list]
        return EligibilityCheckResult(passed=passed, missing=False, weight=25.0, message="Category check")

    def check_state(self, user_val: Optional[str], valid_list: List[str]) -> EligibilityCheckResult:
        if not user_val:
            return EligibilityCheckResult(passed=False, missing=True, weight=30.0, message="State missing", missing_field="state")
        passed = user_val.lower() in [v.lower() for v in valid_list]
        return EligibilityCheckResult(passed=passed, missing=False, weight=30.0, message="State check")

    def check_cgpa(self, user_val: Optional[float], rule_min: float) -> EligibilityCheckResult:
        if user_val is None:
            return EligibilityCheckResult(passed=False, missing=True, weight=20.0, message="CGPA missing", missing_field="cgpa")
        passed = user_val >= rule_min
        return EligibilityCheckResult(passed=passed, missing=False, weight=20.0, message="CGPA check")

    def check_land(self, user_val: Optional[float], rule_max: float) -> EligibilityCheckResult:
        if user_val is None:
            return EligibilityCheckResult(passed=False, missing=True, weight=20.0, message="Land area missing", missing_field="land_area")
        passed = user_val <= rule_max
        return EligibilityCheckResult(passed=passed, missing=False, weight=20.0, message="Land check")

    def check_dpiit(self, user_val: Optional[bool], required: bool) -> EligibilityCheckResult:
        if user_val is None:
            return EligibilityCheckResult(passed=False, missing=True, weight=30.0, message="DPIIT status missing", missing_field="dpiit")
        passed = (user_val == required)
        return EligibilityCheckResult(passed=passed, missing=False, weight=30.0, message="DPIIT check")

    def check_skills(self, user_skills: List[str], required_skills: List[str]) -> EligibilityCheckResult:
        if not user_skills:
            return EligibilityCheckResult(passed=False, missing=True, weight=25.0, message="Skills missing", missing_field="skills")
        
        user_lower = [s.lower().strip() for s in user_skills]
        # Must possess ALL required skills to pass
        missing = [s for s in required_skills if s.lower().strip() not in user_lower]
        
        if missing:
            return EligibilityCheckResult(passed=False, missing=False, weight=25.0, message=f"Missing skills: {', '.join(missing)}")
        return EligibilityCheckResult(passed=True, missing=False, weight=25.0, message="All required skills present")

    def check_experience(self, user_val: Optional[float], rule_min: float) -> EligibilityCheckResult:
        if user_val is None:
            return EligibilityCheckResult(passed=False, missing=True, weight=20.0, message="Experience missing", missing_field="experience_years")
        passed = user_val >= rule_min
        return EligibilityCheckResult(passed=passed, missing=False, weight=20.0, message="Experience check")

    def check_gender(self, user_val: Optional[str], required_gender: str) -> EligibilityCheckResult:
        if not user_val:
            return EligibilityCheckResult(passed=False, missing=True, weight=30.0, message="Gender missing", missing_field="gender")
        passed = user_val.lower() == required_gender.lower()
        return EligibilityCheckResult(passed=passed, missing=False, weight=30.0, message="Gender check")

    def check_documents(self, user_docs: List[str], required_docs: List[str]) -> EligibilityCheckResult:
        if not required_docs:
            return EligibilityCheckResult(passed=True, missing=False, weight=10.0, message="No docs required")
        
        user_lower = [d.lower() for d in user_docs]
        missing = [d for d in required_docs if d.lower() not in user_lower]
        
        if missing:
            return EligibilityCheckResult(passed=False, missing=True, weight=15.0, message="Docs missing", missing_field="documents")
            
        return EligibilityCheckResult(passed=True, missing=False, weight=15.0, message="All docs present")

# Helper functions for readiness/eligibility matching
import json

def get_field(obj: Any, field: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(field, default)
    return getattr(obj, field, default)

def is_missing(val: Any) -> bool:
    if val is None:
        return True
    if isinstance(val, str) and val.strip() in ("", "None", "nan", "NaN"):
        return True
    if isinstance(val, float):
        import math
        return math.isnan(val)
    return False

def safe_float(val: Any, default: float = 0.0) -> float:
    if val is None or val == "":
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def safe_list(val: Any) -> List[Any]:
    if val is None:
        return []
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        val_str = val.strip()
        if not val_str:
            return []
        if val_str.startswith("[") and val_str.endswith("]"):
            try:
                parsed = json.loads(val_str)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
        return [item.strip() for item in val_str.split(",") if item.strip()]
    return [val]
