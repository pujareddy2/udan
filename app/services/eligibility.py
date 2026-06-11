import math
import json
from typing import Dict, Any, List, Optional, Union

# =================================================================
# DYNAMIC QUESTION BANK (PART 2)
# =================================================================
DYNAMIC_QUESTION_BANK = {
    "annual_family_income": {
        "question": "What is your total annual family income from all sources?",
        "reason": "Income determines eligibility for EWS quotas and BPL subsidies.",
        "importance": "critical",
        "confidence_gain": 20
    },
    "income": {
        "question": "What is your total annual family income from all sources?",
        "reason": "Income determines eligibility for EWS quotas and BPL subsidies.",
        "importance": "critical",
        "confidence_gain": 20
    },
    "category": {
        "question": "Do you belong to General, SC, ST, or OBC category?",
        "reason": "Social category provides age relaxations and specific scheme access.",
        "importance": "critical",
        "confidence_gain": 15
    },
    "land_ownership_status": {
        "question": "Is the agricultural land registered in your name?",
        "reason": "Direct benefit transfers strictly require the land to be in the beneficiary's name.",
        "importance": "mandatory",
        "confidence_gain": 25
    },
    "land": {
        "question": "What is the total size of your land in acres?",
        "reason": "Required to determine eligibility for small/marginal farmer schemes.",
        "importance": "mandatory",
        "confidence_gain": 20
    },
    "dpiit_recognized": {
        "question": "Does your startup hold a valid DPIIT Recognition certificate?",
        "reason": "DPIIT recognition bypasses standard MSME requirements and unlocks tax holidays.",
        "importance": "high_value",
        "confidence_gain": 10
    },
    "hostel_status": {
        "question": "Are you currently residing in a recognized school/college hostel?",
        "reason": "Hostellers receive higher maintenance allowances.",
        "importance": "advanced",
        "confidence_gain": 5
    },
    "age": {
        "question": "What is your date of birth or age?",
        "reason": "Age is a fundamental requirement for most schemes.",
        "importance": "critical",
        "confidence_gain": 20
    },
    "state": {
        "question": "Which state do you currently reside in?",
        "reason": "Many schemes are state-specific.",
        "importance": "critical",
        "confidence_gain": 20
    },
    "qualification": {
        "question": "What is your highest educational qualification?",
        "reason": "Determines eligibility for student and job seeker schemes.",
        "importance": "critical",
        "confidence_gain": 15
    },
    "startup_registered": {
        "question": "Is your startup registered as a Private Limited or LLP?",
        "reason": "Required for core startup benefits.",
        "importance": "mandatory",
        "confidence_gain": 20
    },
    "startup": {
        "question": "Is your startup formally registered?",
        "reason": "Required for core startup benefits.",
        "importance": "mandatory",
        "confidence_gain": 20
    },
    "business_stage": {
        "question": "What is the current stage of your business?",
        "reason": "Grants and loans are tailored to specific business stages.",
        "importance": "mandatory",
        "confidence_gain": 15
    }
}

# =================================================================
# UTILITIES
# =================================================================
def is_missing(val: Any) -> bool:
    if val is None: return True
    if isinstance(val, float) and math.isnan(val): return True
    if isinstance(val, str) and val.strip().lower() in ('nan', '', 'null', 'none'): return True
    return False

def get_field(obj: Any, field_name: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(field_name, default)
    
    if hasattr(obj, field_name) and not is_missing(getattr(obj, field_name)):
        return getattr(obj, field_name)
        
    for json_col in ['eligibility_rules', 'benefits', 'metadata_info']:
        if hasattr(obj, json_col):
            col_val = getattr(obj, json_col)
            if isinstance(col_val, dict) and field_name in col_val and not is_missing(col_val[field_name]):
                return col_val[field_name]
            elif isinstance(col_val, str):
                try:
                    parsed = json.loads(col_val)
                    if isinstance(parsed, dict) and field_name in parsed and not is_missing(parsed[field_name]):
                        return parsed[field_name]
                except Exception:
                    pass
    return default

def safe_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val) if not is_missing(val) else default
    except (ValueError, TypeError):
        return default

def safe_list(val: Any) -> List[str]:
    if is_missing(val): return []
    if isinstance(val, list): return [str(v) for v in val]
    if isinstance(val, str):
        try:
            parsed = json.loads(val)
            if isinstance(parsed, list): return [str(v) for v in parsed]
        except Exception:
            pass
        return [v.strip() for v in val.split(',') if v.strip()]
    return []

# =================================================================
# LAYER 2 — AGE RELAXATION ENGINE
# =================================================================
def apply_age_relaxation(base_max_age: float, category: str, pwd_status: bool, gender: str, opp_specific_relaxation: Any = None) -> float:
    if is_missing(base_max_age):
        return float('inf')
        
    relaxation = 0.0
    cat_lower = str(category).lower() if not is_missing(category) else ""
    
    if cat_lower in ['sc', 'st']:
        relaxation = max(relaxation, 5.0)
    elif cat_lower == 'obc':
        relaxation = max(relaxation, 3.0)
        
    if pwd_status:
        relaxation += 10.0
        
    if not is_missing(opp_specific_relaxation):
        relaxation = max(relaxation, safe_float(opp_specific_relaxation))
        
    return base_max_age + relaxation

# =================================================================
# LAYER 3 — QUALIFICATION ENGINE
# =================================================================
QUAL_RANKING = {
    "none": 0, "8th": 10, "10th_pass": 20, "12th_pass": 30, "iti": 35,
    "diploma": 40, "degree": 50, "b.tech": 60, "b.e": 60, "m.tech": 70,
    "mba": 70, "phd": 80
}

def check_qualification_hierarchy(user_qual: str, required_qual: str) -> bool:
    if is_missing(required_qual) or required_qual.lower() == "any":
        return True
    if is_missing(user_qual):
        return False
        
    u_rank = QUAL_RANKING.get(str(user_qual).lower(), 0)
    r_rank = QUAL_RANKING.get(str(required_qual).lower(), 0)
    
    if r_rank == 0:
        return str(user_qual).lower() == str(required_qual).lower()
    return u_rank >= r_rank

# =================================================================
# LAYER 1 — CORE ELIGIBILITY CHECKS
# =================================================================
def check_age(profile: Any, opp: Any) -> Dict[str, Any]:
    min_age = safe_float(get_field(opp, 'min_age', None), 0.0)
    max_age = safe_float(get_field(opp, 'max_age', None), float('inf'))
    
    if min_age == 0.0 and max_age == float('inf'):
        return {"passed": True, "reason": "No age limit", "confidence": 100}
        
    user_age = get_field(profile, 'age')
    if is_missing(user_age):
        return {"passed": True, "reason": "User age unknown (assumed passed)", "confidence": 0}
        
    user_age = safe_float(user_age)
    effective_max = apply_age_relaxation(
        base_max_age=max_age,
        category=get_field(profile, 'category'),
        pwd_status=get_field(profile, 'pwd_status', False),
        gender=get_field(profile, 'gender'),
        opp_specific_relaxation=get_field(opp, 'age_relaxation')
    )
    
    if user_age < min_age: return {"passed": False, "reason": f"Age {user_age} < min {min_age}", "confidence": 100}
    if user_age > effective_max: return {"passed": False, "reason": f"Age {user_age} > max {effective_max}", "confidence": 100}
    return {"passed": True, "reason": f"Age {user_age} within bounds", "confidence": 100}

def check_income(profile: Any, opp: Any) -> Dict[str, Any]:
    min_inc = safe_float(get_field(opp, 'income_min', None), 0.0)
    max_inc = safe_float(get_field(opp, 'income_max', None), float('inf'))
    
    if min_inc == 0.0 and max_inc == float('inf'): return {"passed": True, "reason": "No limit", "confidence": 100}
        
    user_inc = get_field(profile, 'annual_family_income')
    if is_missing(user_inc): return {"passed": True, "reason": "Income unknown", "confidence": 0}
        
    user_inc = safe_float(user_inc)
    if user_inc < min_inc: return {"passed": False, "reason": f"Income < min {min_inc}", "confidence": 100}
    if user_inc > max_inc: return {"passed": False, "reason": f"Income > max {max_inc}", "confidence": 100}
    return {"passed": True, "reason": "Income within bounds", "confidence": 100}

def check_category(profile: Any, opp: Any) -> Dict[str, Any]:
    req_cat = get_field(opp, 'category')
    if is_missing(req_cat) or str(req_cat).lower() == 'any': return {"passed": True, "reason": "Any allowed", "confidence": 100}
    user_cat = get_field(profile, 'category')
    if is_missing(user_cat): return {"passed": True, "reason": "Unknown", "confidence": 0}
    if str(req_cat).lower() == str(user_cat).lower(): return {"passed": True, "reason": "Matched", "confidence": 100}
    return {"passed": False, "reason": f"Requires {req_cat}", "confidence": 100}

def check_gender(profile: Any, opp: Any) -> Dict[str, Any]:
    req_gender = get_field(opp, 'gender')
    if is_missing(req_gender) or str(req_gender).lower() == 'any': return {"passed": True, "reason": "Any allowed", "confidence": 100}
    user_gender = get_field(profile, 'gender')
    if is_missing(user_gender): return {"passed": True, "reason": "Unknown", "confidence": 0}
    if str(req_gender).lower() == str(user_gender).lower(): return {"passed": True, "reason": "Matched", "confidence": 100}
    return {"passed": False, "reason": f"Requires {req_gender}", "confidence": 100}

def check_state(profile: Any, opp: Any) -> Dict[str, Any]:
    req_state = get_field(opp, 'state')
    if is_missing(req_state) or str(req_state).lower() in ['any', 'all india']: return {"passed": True, "reason": "Any allowed", "confidence": 100}
    user_state = get_field(profile, 'state')
    if is_missing(user_state): return {"passed": True, "reason": "Unknown", "confidence": 0}
    if str(req_state).lower() == str(user_state).lower(): return {"passed": True, "reason": "Matched", "confidence": 100}
    return {"passed": False, "reason": f"Requires {req_state}", "confidence": 100}

def check_district(profile: Any, opp: Any) -> Dict[str, Any]:
    req_dist = get_field(opp, 'district')
    if is_missing(req_dist) or str(req_dist).lower() == 'any': return {"passed": True, "reason": "Any allowed", "confidence": 100}
    user_dist = get_field(profile, 'district')
    if is_missing(user_dist): return {"passed": True, "reason": "Unknown", "confidence": 0}
    if str(req_dist).lower() == str(user_dist).lower(): return {"passed": True, "reason": "Matched", "confidence": 100}
    return {"passed": False, "reason": f"Requires {req_dist}", "confidence": 100}

def check_qualification(profile: Any, opp: Any) -> Dict[str, Any]:
    req_qual = get_field(opp, 'qualification')
    if is_missing(req_qual): return {"passed": True, "reason": "Not required", "confidence": 100}
    user_qual = get_field(profile, 'qualification') or get_field(profile, 'highest_qualification') or get_field(profile, 'current_qualification')
    if is_missing(user_qual): return {"passed": True, "reason": "Unknown", "confidence": 0}
    if check_qualification_hierarchy(user_qual, req_qual): return {"passed": True, "reason": "Satisfied", "confidence": 100}
    return {"passed": False, "reason": f"Does not meet {req_qual}", "confidence": 100}

def check_cgpa(profile: Any, opp: Any) -> Dict[str, Any]:
    req_cgpa = safe_float(get_field(opp, 'cgpa_required', None), 0.0)
    if req_cgpa == 0.0: return {"passed": True, "reason": "Not required", "confidence": 100}
    user_cgpa = get_field(profile, 'cgpa')
    if is_missing(user_cgpa): return {"passed": True, "reason": "Unknown", "confidence": 0}
    if safe_float(user_cgpa) >= req_cgpa: return {"passed": True, "reason": "Met", "confidence": 100}
    return {"passed": False, "reason": f"Below {req_cgpa}", "confidence": 100}

def check_experience(profile: Any, opp: Any) -> Dict[str, Any]:
    req_exp = safe_float(get_field(opp, 'experience_required', None), 0.0)
    if req_exp == 0.0: return {"passed": True, "reason": "Not required", "confidence": 100}
    user_exp = get_field(profile, 'years_of_experience')
    if is_missing(user_exp): return {"passed": True, "reason": "Unknown", "confidence": 0}
    if safe_float(user_exp) >= req_exp: return {"passed": True, "reason": "Met", "confidence": 100}
    return {"passed": False, "reason": f"Below {req_exp}", "confidence": 100}

def check_land(profile: Any, opp: Any) -> Dict[str, Any]:
    min_land = safe_float(get_field(opp, 'land_size_min', None), 0.0)
    max_land = safe_float(get_field(opp, 'land_size_max', None), float('inf'))
    if min_land == 0.0 and max_land == float('inf'): return {"passed": True, "reason": "No limit", "confidence": 100}
    user_land = get_field(profile, 'land_size_acres')
    if is_missing(user_land): return {"passed": True, "reason": "Unknown", "confidence": 0}
    user_land = safe_float(user_land)
    if user_land < min_land or user_land > max_land: return {"passed": False, "reason": "Out of bounds", "confidence": 100}
    return {"passed": True, "reason": "Met", "confidence": 100}

def check_crop(profile: Any, opp: Any) -> Dict[str, Any]:
    req_crop = get_field(opp, 'crop_type')
    if is_missing(req_crop) or str(req_crop).lower() in ['any', 'false', 'none']: return {"passed": True, "reason": "No limit", "confidence": 100}
    user_crops = safe_list(get_field(profile, 'crop_types'))
    if not user_crops: return {"passed": True, "reason": "Unknown", "confidence": 0}
    if str(req_crop).lower() in [c.lower() for c in user_crops]: return {"passed": True, "reason": "Met", "confidence": 100}
    return {"passed": False, "reason": f"Requires {req_crop}", "confidence": 100}

def check_startup(profile: Any, opp: Any) -> Dict[str, Any]:
    req_reg = get_field(opp, 'startup_registered')
    if is_missing(req_reg) or str(req_reg).lower() in ['false', '0', 'none']: return {"passed": True, "reason": "Not required", "confidence": 100}
    user_reg = get_field(profile, 'startup_registered')
    if is_missing(user_reg): return {"passed": True, "reason": "Unknown", "confidence": 0}
    if str(user_reg).lower() in ['true', '1', 'yes']: return {"passed": True, "reason": "Met", "confidence": 100}
    return {"passed": False, "reason": "Must be registered", "confidence": 100}

def check_business_stage(profile: Any, opp: Any) -> Dict[str, Any]:
    req_stage = get_field(opp, 'business_stage')
    if is_missing(req_stage): return {"passed": True, "reason": "Any", "confidence": 100}
    user_stage = get_field(profile, 'business_stage')
    if is_missing(user_stage): return {"passed": True, "reason": "Unknown", "confidence": 0}
    if str(user_stage).lower() == str(req_stage).lower(): return {"passed": True, "reason": "Matched", "confidence": 100}
    return {"passed": False, "reason": f"Requires {req_stage}", "confidence": 100}

# =================================================================
# LAYER 4 — DOCUMENT INTELLIGENCE (PART 6)
# =================================================================
def calculate_document_score(profile: Any, opp: Any) -> Dict[str, Any]:
    req_docs = safe_list(get_field(opp, 'required_documents'))
    if not req_docs:
        alt_docs = safe_list(get_field(opp, 'land_owner_required'))
        if alt_docs and isinstance(alt_docs[0], str) and "Certificate" in alt_docs[0]:
            req_docs = alt_docs
            
    if not req_docs:
        return {"document_score": 100.0, "missing_documents": [], "document_readiness_percentage": 100.0}
        
    user_docs = set([str(d).lower() for d in safe_list(get_field(profile, 'available_documents'))])
    
    missing_docs = []
    provided_count = 0
    total_weight = 0.0
    earned_weight = 0.0
    
    for doc in req_docs:
        doc_lower = doc.lower()
        # Tiered importance logic
        importance = "optional"
        weight = 1.0
        if any(w in doc_lower for w in ["aadhaar", "bank", "domicile"]):
            importance = "mandatory"
            weight = 3.0
        elif any(w in doc_lower for w in ["income", "caste", "dpiit", "udyam"]):
            importance = "high_value"
            weight = 2.0
            
        total_weight += weight
        if doc_lower in user_docs:
            provided_count += 1
            earned_weight += weight
        else:
            missing_docs.append({"name": doc, "importance": importance})
            
    readiness = (earned_weight / total_weight) * 100 if total_weight > 0 else 100.0
    
    return {
        "document_score": round(readiness, 2),
        "missing_documents": missing_docs,
        "document_readiness_percentage": round(readiness, 2)
    }

# =================================================================
# LAYER 5 — SKILL INTELLIGENCE
# =================================================================
def calculate_skill_score(profile: Any, opp: Any) -> Dict[str, Any]:
    req_skills = safe_list(get_field(opp, 'required_skills'))
    actual_skills = [s for s in req_skills if "?" not in s] 
    
    if not actual_skills:
        return {"skill_score": 100.0, "missing_skills": [], "skill_readiness_percentage": 100.0}
        
    user_skills = set([str(s).lower() for s in safe_list(get_field(profile, 'skills'))])
    
    missing_skills = []
    provided_count = 0
    
    for skill in actual_skills:
        if skill.lower() in user_skills:
            provided_count += 1
        else:
            missing_skills.append({"name": skill, "importance": "mandatory"})
            
    readiness = (provided_count / len(actual_skills)) * 100 if actual_skills else 100.0
    
    return {
        "skill_score": round(readiness, 2),
        "missing_skills": missing_skills,
        "skill_readiness_percentage": round(readiness, 2)
    }

# =================================================================
# LAYER 6 — FOLLOWUP INTELLIGENCE (PART 2 & 5)
# =================================================================
def generate_followup_questions(profile: Any, opp: Any, core_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    questions = []
    val = safe_float(get_field(opp, 'benefit_amount'), 0.0)
    benefit_str = f"₹{val}" if val > 0 else "its benefits"
    
    req_questions = safe_list(get_field(opp, 'required_followup_questions'))
    alt_q = safe_list(get_field(opp, 'required_skills'))
    req_questions.extend([q for q in alt_q if "?" in q])
    
    answered_q = set([str(q).lower() for q in safe_list(get_field(profile, 'answered_questions'))])
    
    # 1. Explicit DB Followups
    for q in req_questions:
        if q.lower() not in answered_q:
            questions.append({
                "field_name": "db_explicit",
                "question": q,
                "reason": "Required by opportunity",
                "importance": "mandatory",
                "confidence_gain": 5,
                "opportunities_unlocked": f"Unlocks {get_field(opp, 'title', 'this scheme')} worth {benefit_str}",
                "priority_score": 10.0 + (val / 1000.0)
            })
            
    # 2. Dynamic Missing Fields
    for field, res in core_results.items():
        if res.get('confidence', 100) < 100:
            q_data = DYNAMIC_QUESTION_BANK.get(field)
            if q_data:
                priority = 5.0 + (val / 1000.0) + (q_data['confidence_gain'] * 2)
                if q_data['importance'] == 'critical': priority += 50.0
                if q_data['importance'] == 'mandatory': priority += 30.0
                
                questions.append({
                    "field_name": field,
                    "question": q_data['question'],
                    "reason": q_data['reason'],
                    "importance": q_data['importance'],
                    "confidence_gain": q_data['confidence_gain'],
                    "opportunities_unlocked": f"Unlocks {get_field(opp, 'title', 'this scheme')} worth {benefit_str}",
                    "priority_score": round(priority, 2)
                })
            else:
                questions.append({
                    "field_name": field,
                    "question": f"Please provide information for: {field}",
                    "reason": f"Missing {field}",
                    "importance": "mandatory",
                    "confidence_gain": 10,
                    "opportunities_unlocked": f"Required for {benefit_str}",
                    "priority_score": 10.0 + (val / 1000.0)
                })
                
    questions.sort(key=lambda x: x['priority_score'], reverse=True)
    return questions

# =================================================================
# LAYER 7 — CONFIDENCE ENGINE (PART 4)
# =================================================================
def calculate_confidence(core_results: Dict[str, Any], doc_res: Dict[str, Any], unanswered_followups: int) -> float:
    confidence = 100.0
    
    # Penalize for missing critical fields
    for field in ['age', 'income', 'state', 'category']:
        if field in core_results and core_results[field].get('confidence', 100) < 100:
            confidence -= 15.0
            
    # Penalize for missing module core fields
    for field in ['land', 'startup', 'business_stage']:
        if field in core_results and core_results[field].get('confidence', 100) < 100:
            confidence -= 20.0
            
    # Penalize for missing critical docs
    for doc in doc_res['missing_documents']:
        if doc['importance'] == 'mandatory': confidence -= 10.0
        elif doc['importance'] == 'high_value': confidence -= 5.0
            
    # Penalize for unanswered followups
    confidence -= (unanswered_followups * 2.0)
    
    return max(0.0, min(100.0, confidence))

# =================================================================
# LAYER 8 — READINESS ENGINE (PART 7)
# =================================================================
def calculate_readiness(doc_res: Dict[str, Any], skill_res: Dict[str, Any], followup_count: int, eligible: bool) -> Dict[str, float]:
    profile_readiness = max(0.0, 100.0 - (followup_count * 10))
    eligibility_readiness = 100.0 if eligible else 0.0
    doc_score = doc_res['document_score']
    skill_score = skill_res['skill_score']
    
    # Weighted Readiness Model: PR 20%, ER 40%, DR 30%, SR 10%
    overall = (profile_readiness * 0.20) + (eligibility_readiness * 0.40) + (doc_score * 0.30) + (skill_score * 0.10)
    
    return {
        "overall": round(overall, 2),
        "profile_readiness": profile_readiness,
        "documents_score": doc_score,
        "skills_score": skill_score,
        "eligibility_score": eligibility_readiness
    }

# =================================================================
# LAYER 9 — VALUE ENGINE
# =================================================================
def calculate_opportunity_value(opp: Any, eligible: bool, readiness: float) -> Dict[str, float]:
    val = safe_float(get_field(opp, 'benefit_amount'), 0.0)
    
    total = val
    potential = 0.0
    missed = 0.0
    
    if eligible:
        if readiness >= 100.0: potential = val
        else: potential = val 
    else:
        total = 0.0
        missed = val
        
    return {
        "total_benefit_value": total if readiness >= 100.0 else 0.0,
        "potential_value": potential,
        "missed_value": missed
    }

# =================================================================
# LAYER 10 — PRIORITY ENGINE
# =================================================================
def calculate_priority(opp: Any, eligible: bool, readiness: float, confidence: float, val_dict: Dict[str, float]) -> Dict[str, Any]:
    db_priority = safe_float(get_field(opp, 'priority_score'), 0.0)
    benefit_val = val_dict['potential_value'] or val_dict['total_benefit_value']
    
    score = 0.0
    if not eligible:
        return {"level": "Low", "numeric_score": 0.0}
        
    score += min(benefit_val / 1000.0, 50.0) 
    score += (readiness / 100.0) * 30.0 
    score += (confidence / 100.0) * 10.0 
    score += db_priority 
    
    level = "Low"
    if score > 70: level = "High"
    elif score > 40: level = "Medium"
    
    return {"level": level, "numeric_score": round(score, 2)}

# =================================================================
# LAYER 11 — ACTION ENGINE
# =================================================================
def generate_next_actions(doc_res: Dict[str, Any], skill_res: Dict[str, Any], followups: List[Any], eligible: bool) -> List[str]:
    actions = []
    
    for doc in doc_res['missing_documents']:
        actions.append(f"Upload or Apply for {doc['name']}")
        
    for skill in skill_res['missing_skills']:
        actions.append(f"Acquire skill: {skill['name']}")
        
    for f in followups:
        actions.append(f"Answer Question: {f['question']}")
        
    if not actions and eligible:
        actions.append("Ready to Apply")
        
    return actions

# =================================================================
# LAYER 12 — MODULE SPECIFIC ENGINES
# =================================================================
class BaseEligibility:
    def evaluate(self, profile: Any, opp: Any) -> Dict[str, Any]:
        return {"passed": True, "reason": "Base module", "confidence": 100}

class StudentEligibility(BaseEligibility):
    def evaluate(self, profile: Any, opp: Any):
        return check_cgpa(profile, opp)

class FarmerEligibility(BaseEligibility):
    def evaluate(self, profile: Any, opp: Any):
        res1 = check_land(profile, opp)
        res2 = check_crop(profile, opp)
        if not res1['passed']: return res1
        if not res2['passed']: return res2
        return {"passed": True, "reason": "Farmer specific checks passed", "confidence": (res1.get('confidence', 100)+res2.get('confidence', 100))/2}

class JobSeekerEligibility(BaseEligibility):
    def evaluate(self, profile: Any, opp: Any):
        return check_experience(profile, opp)

class EntrepreneurEligibility(BaseEligibility):
    def evaluate(self, profile: Any, opp: Any):
        return check_business_stage(profile, opp)

class WomenEntrepreneurEligibility(BaseEligibility):
    def evaluate(self, profile: Any, opp: Any):
        gender = get_field(profile, 'gender')
        if not is_missing(gender) and str(gender).lower() not in ['female', 'woman', 'women']:
            return {"passed": False, "reason": "Strictly for women entrepreneurs", "confidence": 100}
        return check_business_stage(profile, opp)

class StartupEligibility(BaseEligibility):
    def evaluate(self, profile: Any, opp: Any):
        return check_startup(profile, opp)

class SeniorCitizenEligibility(BaseEligibility):
    def evaluate(self, profile: Any, opp: Any):
        age_res = check_age(profile, opp)
        if age_res['passed'] and get_field(profile, 'age') is not None and safe_float(get_field(profile, 'age')) < 60:
             pass
        return age_res

def get_module_engine(module_type: str) -> BaseEligibility:
    mod = str(module_type).lower()
    if 'student' in mod: return StudentEligibility()
    if 'farmer' in mod: return FarmerEligibility()
    if 'job' in mod: return JobSeekerEligibility()
    if 'women' in mod: return WomenEntrepreneurEligibility()
    if 'entrepreneur' in mod: return EntrepreneurEligibility()
    if 'startup' in mod: return StartupEligibility()
    if 'senior' in mod: return SeniorCitizenEligibility()
    return BaseEligibility()

# =================================================================
# LAYER 13 — MASTER ENGINE
# =================================================================
def check_eligibility(profile: Any, opportunity: Any) -> Dict[str, Any]:
    
    core_checks = {
        "age": check_age(profile, opportunity),
        "income": check_income(profile, opportunity),
        "category": check_category(profile, opportunity),
        "gender": check_gender(profile, opportunity),
        "state": check_state(profile, opportunity),
        "district": check_district(profile, opportunity),
        "qualification": check_qualification(profile, opportunity),
    }
    
    mod_type = get_field(opportunity, 'module_type', '')
    mod_engine = get_module_engine(mod_type)
    core_checks[mod_type if mod_type else 'module_specific'] = mod_engine.evaluate(profile, opportunity)
    
    eligible = True
    reasons = []
    for k, v in core_checks.items():
        if not v['passed']:
            eligible = False
            reasons.append(v['reason'])
            
    doc_res = calculate_document_score(profile, opportunity)
    skill_res = calculate_skill_score(profile, opportunity)
    
    followups = generate_followup_questions(profile, opportunity, core_checks)
    
    confidence = calculate_confidence(core_checks, doc_res, len(followups))
    
    readiness = calculate_readiness(doc_res, skill_res, len(followups), eligible)
    
    val_engine = calculate_opportunity_value(opportunity, eligible, readiness['overall'])
    
    priority = calculate_priority(opportunity, eligible, readiness['overall'], confidence, val_engine)
    
    actions = generate_next_actions(doc_res, skill_res, followups, eligible)
    
    return {
        "eligible": eligible,
        "match_percentage": readiness['overall'] if eligible else 0.0,
        "confidence": round(confidence, 2),
        "readiness_score": readiness['overall'],
        "document_score": doc_res['document_score'],
        "skill_score": skill_res['skill_score'],
        "priority": priority['level'],
        "priority_score": priority['numeric_score'],
        "total_benefit_value": val_engine['total_benefit_value'],
        "potential_value": val_engine['potential_value'],
        "missed_value": val_engine['missed_value'],
        "reasons": reasons,
        "missing_documents": doc_res['missing_documents'],
        "missing_skills": skill_res['missing_skills'],
        "followup_questions": followups,
        "recommended_actions": actions
    }
