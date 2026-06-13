"""
Eligibility Engine (Puja's Module emulation/implementation)
============================================================
Checks if a user profile is eligible for a given opportunity.
Used for testing and end-to-end integration demo flow.
"""

import json
from typing import Dict, List, Any


def _parse_list(val: Any) -> List[str]:
    """Parse JSON array or list of strings safely."""
    if not val:
        return []
    if isinstance(val, list):
        return val
    try:
        parsed = json.loads(val)
        if isinstance(parsed, list):
            return [str(x) for x in parsed]
        return [str(parsed)]
    except Exception:
        return [str(val)]


def check_eligibility(profile: Dict[str, Any], opp: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determines user eligibility for an opportunity.
    Returns:
        {
            "verdict": "eligible" | "partial" | "not_eligible",
            "reasons": list[str],
            "missing_documents": list[str],
            "missing_skills": list[str],
            "readiness": int (0-100)
        }
    """
    reasons = []
    missing_docs = []
    missing_skills = []

    # Extract profile fields
    age = profile.get("age")
    category = str(profile.get("category") or "general").strip().lower()
    state = str(profile.get("state") or "").strip().lower()
    qualification = str(profile.get("qualification") or "").strip().lower()
    user_skills = [s.strip().lower() for s in (profile.get("skills") or [])]

    # Extract opportunity fields
    opp_title = opp.get("title", "Opportunity")
    opp_min_age = opp.get("min_age")
    opp_max_gen = opp.get("max_age_general")
    opp_max_obc = opp.get("max_age_obc")
    opp_max_sc_st = opp.get("max_age_sc_st")
    opp_max_pwd = opp.get("max_age_pwd")

    opp_quals = _parse_list(opp.get("qualifications"))
    opp_cats = _parse_list(opp.get("categories"))
    opp_states = _parse_list(opp.get("states"))
    opp_docs = _parse_list(opp.get("required_documents"))
    opp_req_skills = _parse_list(opp.get("required_skills"))

    core_eligible = True

    # 1. Age Check
    if age is not None:
        # Min age check
        if opp_min_age:
            try:
                min_a = int(opp_min_age)
                if age < min_a:
                    core_eligible = False
                    reasons.append(f"Age {age} is below the minimum age of {min_a} required.")
            except ValueError:
                pass

        # Max age check with category relaxation
        max_a_str = opp_max_gen
        if "pwd" in category and opp_max_pwd:
            max_a_str = opp_max_pwd
        elif ("sc" in category or "st" in category) and opp_max_sc_st:
            max_a_str = opp_max_sc_st
        elif "obc" in category and opp_max_obc:
            max_a_str = opp_max_obc

        if max_a_str:
            try:
                max_a = int(max_a_str)
                if age > max_a:
                    core_eligible = False
                    reasons.append(f"Age {age} exceeds the maximum age of {max_a} allowed for {category.upper()} category.")
            except ValueError:
                pass
    else:
        # If age is unknown, we assume they pass but flag it
        pass

    # 2. State Check
    if opp_states:
        opp_states_lower = [s.lower() for s in opp_states]
        if state not in opp_states_lower:
            core_eligible = False
            reasons.append(f"Domicile state must be one of: {', '.join(opp_states)}.")

    # 3. Category Check
    if opp_cats:
        opp_cats_lower = [c.lower() for c in opp_cats]
        # map OBC-NCL / SC / ST to matching keys
        cat_matches = False
        for c in opp_cats_lower:
            if c in category or category in c:
                cat_matches = True
                break
        if not cat_matches:
            core_eligible = False
            reasons.append(f"Category {category.upper()} is not eligible for this scheme.")

    # 4. Qualification Check
    if opp_quals:
        # Hierarchical levels of qualifications
        QUAL_LEVELS = {
            "none": 0,
            "8th_pass": 1,
            "10th_pass": 2,
            "12th_pass": 3,
            "higher_secondary": 3,
            "iti": 3,
            "diploma": 4,
            "graduate": 5,
            "post-graduate": 6,
        }

        user_level = QUAL_LEVELS.get(qualification, 0)
        qual_matches = False
        for q in opp_quals:
            q_lower = q.lower().strip()
            # If explicit match
            if q_lower == qualification or q_lower in qualification:
                qual_matches = True
                break
            # Or if user level is equal/higher than required level
            req_level = QUAL_LEVELS.get(q_lower)
            if req_level is not None and user_level >= req_level:
                qual_matches = True
                break

        if not qual_matches:
            core_eligible = False
            reasons.append(f"Qualification '{qualification}' does not meet requirements: {', '.join(opp_quals)}.")

    if not core_eligible:
        return {
            "verdict": "not_eligible",
            "reasons": reasons,
            "missing_documents": [],
            "missing_skills": [],
            "readiness": 0
        }

    # If core criteria met, check missing skills and documents
    reasons.append("Basic criteria (Age, Domicile, Qualification, Category) matched successfully.")

    # 5. Missing Skills Check
    for skill in opp_req_skills:
        skill_norm = skill.strip().lower().replace(" ", "_").replace("-", "_")
        user_skills_norm = [s.replace(" ", "_").replace("-", "_") for s in user_skills]
        if skill_norm not in user_skills_norm:
            missing_skills.append(skill)
            reasons.append(f"Missing required skill: {skill}.")

    # 6. Missing Documents Check
    user_docs = [d.strip().lower() for d in (profile.get("documents") or [])]
    for doc in opp_docs:
        doc_norm = doc.strip().lower()
        if doc_norm not in user_docs:
            missing_docs.append(doc)
            reasons.append(f"Must submit document: {doc.replace('_', ' ').title()}.")

    # Determine verdict
    if missing_skills or missing_docs:
        verdict = "partial"
        # Calculate readiness: 100% minus deductions
        readiness = 100 - (len(missing_skills) * 20) - (len(missing_docs) * 10)
        readiness = max(10, min(95, readiness))
    else:
        verdict = "eligible"
        readiness = 100

    return {
        "verdict": verdict,
        "reasons": reasons,
        "missing_documents": missing_docs,
        "missing_skills": missing_skills,
        "readiness": readiness
    }
