import math
from typing import Dict, Any, List

from app.services.eligibility import get_field, is_missing, safe_float, safe_list

# =================================================================
# INTELLIGENCE DATABASES
# =================================================================

DOCUMENT_INTELLIGENCE_DB = {
    "income certificate": {
        "processing_time_days": "3-7 Days",
        "how_to_apply": "Apply via State e-District Portal or local MeeSeva/CSC center.",
        "required_documents_for_this_document": ["Aadhaar", "Ration Card", "Self-Declaration"],
        "official_application_link": "https://edistrict.gov.in",
        "validity": "6 months to 1 financial year"
    },
    "caste certificate": {
        "processing_time_days": "7-15 Days",
        "how_to_apply": "Apply via Tahsildar / e-District Portal.",
        "required_documents_for_this_document": ["Aadhaar", "Ancestral proof", "School Transfer Certificate"],
        "official_application_link": "https://edistrict.gov.in",
        "validity": "Lifetime (Static) / Annual for OBC-NCL"
    },
    "land passbook": {
        "processing_time_days": "15-30 Days",
        "how_to_apply": "Revenue/Land Records Department (e.g., Dharani, Bhoomi).",
        "required_documents_for_this_document": ["Sale Deed", "Aadhaar"],
        "official_application_link": "State Specific Land Portal",
        "validity": "Lifetime"
    },
    "dpiit certificate": {
        "processing_time_days": "2-4 Weeks",
        "how_to_apply": "Online via Ministry of Commerce Startup India Portal.",
        "required_documents_for_this_document": ["Incorporation Certificate", "Pitch Deck", "PAN"],
        "official_application_link": "https://www.startupindia.gov.in/",
        "validity": "Max 10 years from incorporation"
    },
    "udyam registration": {
        "processing_time_days": "Instant",
        "how_to_apply": "Online via Ministry of MSME Udyam Registration Portal.",
        "required_documents_for_this_document": ["Aadhaar of proprietor", "PAN", "Bank Details"],
        "official_application_link": "https://udyamregistration.gov.in/",
        "validity": "Lifetime (Dynamic updates via ITR)"
    },
    "disability certificate": {
        "processing_time_days": "1-2 Months",
        "how_to_apply": "Medical Board / Dept of Empowerment of PWDs -> Swavlamban Card Portal.",
        "required_documents_for_this_document": ["Aadhaar", "Medical Reports", "Photo"],
        "official_application_link": "https://www.swavlambancard.gov.in/",
        "validity": "Lifetime (Permanent) / 5 Years (Temporary)"
    },
    "aadhaar": {
        "processing_time_days": "15-30 Days",
        "how_to_apply": "Visit nearest Aadhaar Enrollment Center.",
        "required_documents_for_this_document": ["Proof of Identity", "Proof of Address"],
        "official_application_link": "https://uidai.gov.in/",
        "validity": "Lifetime"
    }
}

MODULE_MANDATORY_FIELDS = {
    "student": ["age", "qualification", "state", "category", "annual_family_income"],
    "farmer": ["land_size_acres", "land_ownership_status", "state", "category"],
    "job seeker": ["highest_qualification", "age", "state"],
    "entrepreneur": ["business_stage", "age", "state"],
    "women entrepreneur": ["women_ownership_percentage", "business_stage", "state"],
    "startup": ["startup_registered", "dpiit_recognized"],
    "senior citizen": ["age", "state"]
}

MODULE_IMPORTANT_FIELDS = {
    "student": ["cgpa", "year", "semester", "pwd_status"],
    "farmer": ["crop_types", "irrigation_type"],
    "job seeker": ["skills", "years_of_experience", "apprenticeship_status"],
    "entrepreneur": ["annual_revenue", "udyam_registration"],
    "women entrepreneur": ["shg_member_status", "rural_urban"],
    "startup": ["funding_stage", "annual_revenue"],
    "senior citizen": ["receiving_pension", "annual_personal_income", "pwd_status"]
}

# =================================================================
# LAYER 1 — PROFILE READINESS
# =================================================================
def get_profile_readiness(profile: Any, module_type: str) -> float:
    mod = str(module_type).lower()
    
    # Resolve exact module key
    mod_key = "student"
    for k in MODULE_MANDATORY_FIELDS.keys():
        if k in mod: mod_key = k

    mandatory_fields = MODULE_MANDATORY_FIELDS[mod_key]
    important_fields = MODULE_IMPORTANT_FIELDS[mod_key]
    
    mand_filled = sum(1 for f in mandatory_fields if not is_missing(get_field(profile, f)))
    imp_filled = sum(1 for f in important_fields if not is_missing(get_field(profile, f)))
    
    mand_score = (mand_filled / len(mandatory_fields) * 60) if mandatory_fields else 60.0
    imp_score = (imp_filled / len(important_fields) * 40) if important_fields else 40.0
    
    return round(mand_score + imp_score, 2)

# =================================================================
# LAYER 2 — DOCUMENT READINESS
# =================================================================
def get_document_readiness(profile: Any, opp: Any) -> Dict[str, Any]:
    req_docs = safe_list(get_field(opp, 'required_documents'))
    if not req_docs:
        alt_docs = safe_list(get_field(opp, 'land_owner_required'))
        if alt_docs and isinstance(alt_docs[0], str) and "Certificate" in alt_docs[0]:
            req_docs = alt_docs
            
    if not req_docs:
        return {"score": 100.0, "missing": [], "action_plan": []}
        
    user_docs = set([str(d).lower() for d in safe_list(get_field(profile, 'available_documents'))])
    
    missing_docs = []
    action_plan = []
    total_weight = 0.0
    earned_weight = 0.0
    
    val = safe_float(get_field(opp, 'benefit_amount'), 0.0)
    
    for doc in req_docs:
        doc_lower = doc.lower()
        
        importance = "optional"
        weight = 1.0
        if any(w in doc_lower for w in ["aadhaar", "bank", "domicile"]):
            importance = "mandatory"
            weight = 3.0
        elif any(w in doc_lower for w in ["income", "caste", "dpiit", "udyam", "certificate", "passbook"]):
            importance = "critical"
            weight = 2.0
            
        total_weight += weight
        
        if doc_lower in user_docs:
            earned_weight += weight
        else:
            missing_docs.append(doc)
            
            # Enrich with real Indian Gov data if available
            db_entry = None
            for key, data in DOCUMENT_INTELLIGENCE_DB.items():
                if key in doc_lower:
                    db_entry = data
                    break
                    
            if not db_entry:
                db_entry = {
                    "processing_time_days": "Unknown",
                    "how_to_apply": "Check official scheme portal.",
                    "required_documents_for_this_document": ["Aadhaar"],
                    "official_application_link": "N/A"
                }
                
            action_plan.append({
                "document_name": doc,
                "importance": importance,
                "required_for": [get_field(opp, 'title', 'This Scheme')],
                "opportunities_unlocked": 1,
                "estimated_benefit_value": val,
                "processing_time_days": db_entry["processing_time_days"],
                "deadline_risk": "Medium",
                "how_to_apply": db_entry["how_to_apply"],
                "required_documents_for_this_document": db_entry["required_documents_for_this_document"],
                "official_application_link": db_entry["official_application_link"]
            })
            
    score = (earned_weight / total_weight) * 100 if total_weight > 0 else 100.0
    
    return {
        "score": round(score, 2),
        "missing": missing_docs,
        "action_plan": action_plan
    }

# =================================================================
# LAYER 3 — ELIGIBILITY READINESS
# =================================================================
def get_eligibility_readiness(core_checks: Dict[str, Any]) -> Dict[str, Any]:
    total_checks = 0
    passed_checks = 0
    gaps = []
    
    # We define mapping to format nice gap analysis
    hard_blockers = ['age', 'income', 'qualification', 'land_size']
    
    for factor, res in core_checks.items():
        if factor == 'module_specific': continue # We evaluate the raw base checks
        
        # We only count it if it was a real check (not "Not required")
        if "Any allowed" in res['reason'] or "Not required" in res['reason'] or "No limit" in res['reason']:
            continue
            
        total_checks += 1
        if res['passed']:
            passed_checks += 1
        else:
            impact = "hard_rejection" if any(b in factor for b in hard_blockers) else "threshold_rejection"
            gaps.append({
                "factor": factor,
                "current_value": "User Profile Value", # We don't have direct access here, but reason holds the string
                "required_value": res['reason'],
                "status": "failed",
                "impact": impact,
                "opportunities_affected": ["Current Scheme"],
                "estimated_benefit_loss": "Calculate dynamically"
            })
            
    score = (passed_checks / total_checks) * 100 if total_checks > 0 else 100.0
    
    return {
        "score": round(score, 2),
        "gaps": gaps
    }

# =================================================================
# MAIN ENTRY POINT
# =================================================================
def generate_readiness_report(profile: Any, opp: Any, core_checks: Dict[str, Any]) -> Dict[str, Any]:
    mod_type = get_field(opp, 'module_type', 'student')
    
    pr_score = get_profile_readiness(profile, mod_type)
    dr_data = get_document_readiness(profile, opp)
    er_data = get_eligibility_readiness(core_checks)
    
    val = safe_float(get_field(opp, 'benefit_amount'), 0.0)
    
    overall = (pr_score * 0.20) + (er_data['score'] * 0.40) + (dr_data['score'] * 0.30) + (100.0 * 0.10) # 10% skills baseline
    
    next_steps = []
    for doc in dr_data['action_plan']:
        next_steps.append(f"Apply for {doc['document_name']} via {doc.get('how_to_apply', 'portal')} (Takes {doc.get('processing_time_days', 'some time')}).")
    for gap in er_data['gaps']:
        next_steps.append(f"Review eligibility gap for {gap['factor']}: {gap['required_value']}")
    
    # Fill in the loss values for gaps
    for gap in er_data['gaps']:
        gap['estimated_benefit_loss'] = val

    return {
        "readiness_scores": {
            "overall_readiness": round(overall, 2),
            "profile_readiness": pr_score,
            "document_readiness": dr_data['score'],
            "eligibility_readiness": er_data['score']
        },
        "missing_documents": dr_data['missing'],
        "document_action_plan": dr_data['action_plan'],
        "eligibility_gaps": er_data['gaps'],
        "estimated_unlock_value": val if dr_data['action_plan'] or er_data['gaps'] else 0.0,
        "deadline_risk": "High" if dr_data['action_plan'] else "Low",
        "recommended_next_steps": next_steps
    }
