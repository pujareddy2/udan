import json
from typing import Dict, Any

QUAL_LEVELS = {
    "none": 0,
    "8th_pass": 1,
    "10th_pass": 2,
    "12th_pass": 3,
    "higher_secondary": 3,
    "iti": 3,
    "diploma": 4,
    "graduate": 5,
    "post-graduate": 6
}

def _parse_json_list(val: Any) -> list:
    if not val or val == "[]" or str(val).strip() == "":
        return []
    if isinstance(val, list):
        return [str(v).lower() for v in val]
    try:
        parsed = json.loads(val)
        return [str(v).lower() for v in parsed]
    except:
        return []

def check_eligibility(profile: Dict[str, Any], opp: Dict[str, Any]) -> Dict[str, Any]:
    reasons = []
    missing_docs = []
    missing_skills = []
    
    prof_age = profile.get("age")
    prof_cat = (profile.get("category") or "general").lower()
    prof_state = (profile.get("state") or "").lower()
    prof_qual = (profile.get("qualification") or "none").lower()
    prof_skills = [s.lower() for s in profile.get("skills", [])]
    prof_docs = [d.lower() for d in profile.get("documents", [])]

    core_failed = False
    
    # 1. Min Age
    min_age_str = opp.get("min_age", "")
    if min_age_str and prof_age is not None:
        try:
            if prof_age < int(float(min_age_str)):
                reasons.append(f"Minimum age required is {min_age_str}.")
                core_failed = True
        except ValueError:
            pass

    # 2. Max Age with relaxation
    max_age = None
    if prof_cat == "obc":
        max_age = opp.get("max_age_obc") or opp.get("max_age_general")
    elif prof_cat in ["sc", "st"]:
        max_age = opp.get("max_age_sc_st") or opp.get("max_age_general")
    elif prof_cat == "pwd":
        max_age = opp.get("max_age_pwd") or opp.get("max_age_general")
    else:
        max_age = opp.get("max_age_general")
        
    if max_age and prof_age is not None:
        try:
            if prof_age > int(float(max_age)):
                reasons.append(f"Age exceeds the maximum allowed age for {prof_cat.upper()} category ({max_age}).")
                core_failed = True
        except ValueError:
            pass
            
    # 3. States
    req_states = _parse_json_list(opp.get("states", ""))
    if req_states and prof_state not in req_states:
        reasons.append(f"Only available for residents of specific states.")
        core_failed = True
        
    # 4. Categories
    req_cats = _parse_json_list(opp.get("categories", ""))
    if req_cats and prof_cat not in req_cats:
        reasons.append(f"Reserved for specific categories.")
        core_failed = True

    # 5. Qualifications
    req_quals = _parse_json_list(opp.get("qualifications", ""))
    if req_quals:
        user_level = QUAL_LEVELS.get(prof_qual, 0)
        qual_passed = False
        for rq in req_quals:
            req_level = QUAL_LEVELS.get(rq, 0)
            if user_level >= req_level:
                qual_passed = True
                break
        if not qual_passed:
            reasons.append(f"Requires higher educational qualification level.")
            core_failed = True

    # Check skills and docs
    req_skills = _parse_json_list(opp.get("required_skills", ""))
    for s in req_skills:
        if s not in prof_skills:
            missing_skills.append(s)
            
    req_docs = _parse_json_list(opp.get("required_documents", ""))
    for d in req_docs:
        if d not in prof_docs:
            missing_docs.append(d)

    if core_failed:
        return {
            "verdict": "not_eligible",
            "reasons": reasons,
            "missing_documents": missing_docs,
            "missing_skills": missing_skills,
            "readiness": 0
        }
        
    if missing_skills or missing_docs:
        if missing_skills:
            reasons.append("You are missing some required skills.")
        if missing_docs:
            reasons.append("You are missing some required documents.")
            
        readiness = 100 - (len(missing_skills) * 20) - (len(missing_docs) * 10)
        readiness = max(10, min(95, readiness)) # Clamp between 10 and 95
        
        return {
            "verdict": "partial",
            "reasons": reasons,
            "missing_documents": missing_docs,
            "missing_skills": missing_skills,
            "readiness": readiness
        }
        
    return {
        "verdict": "eligible",
        "reasons": ["You meet all criteria and have the necessary documents and skills."],
        "missing_documents": [],
        "missing_skills": [],
        "readiness": 100
    }
