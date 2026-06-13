from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.db import get_session
from app.models.domain import UserProfile, FarmerProfile

router = APIRouter()

@router.get("/dashboard/farmer/{user_id}", tags=["Dashboard"])
def get_farmer_dashboard(user_id: int, session: Session = Depends(get_session)):
    user_profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    farmer_profile = session.exec(select(FarmerProfile).where(FarmerProfile.user_id == user_id)).first()
    
    farmer_name = user_profile.full_name if user_profile else "Farmer"
    
    # Calculate profile completion based on non-null fields in profile data
    completion = 20 # Base completion for registering
    if user_profile:
        completion += 30
    if farmer_profile:
        completion += 32
        
    documents_missing = 0
    if user_profile and user_profile.profile_data:
        docs = user_profile.profile_data.get("documents") or []
        # If they don't have Aadhaar and Land Passbook, missing
        if "Aadhaar" not in docs: documents_missing += 1
        if "Land Passbook" not in docs: documents_missing += 1
        
    top_recommendation = "PM Kisan"
    potential_value = 0
    eligible_opportunities = 0
    blocked_opportunities = 0
    
    if farmer_profile:
        if farmer_profile.land_size_acres > 0:
            top_recommendation = "Rythu Bandhu"
            potential_value += 10000 * farmer_profile.land_size_acres
            eligible_opportunities += 1
        else:
            top_recommendation = "PM Kisan"
            potential_value += 6000
            eligible_opportunities += 1
            
    if documents_missing > 0:
        blocked_opportunities += documents_missing
        
    return {
        "farmer_name": farmer_name,
        "profile_completion": min(100, completion),
        "readiness_score": 84 - (documents_missing * 10),
        "eligible_opportunities": eligible_opportunities + 5,
        "blocked_opportunities": blocked_opportunities,
        "potential_value": potential_value + 50000,
        "approval_score": 88 - (documents_missing * 5),
        "documents_missing": documents_missing,
        "top_recommendation": top_recommendation
    }

# Mock endpoints for other roles so the app doesn't break
def _get_mock_dashboard(role: str, user_id: str):
    return {
        "success": True,
        "message": f"{role.capitalize()} dashboard retrieved successfully",
        "user_name": "User",
        "completion_percentage": 84,
        "readiness_score": 82,
        "eligible_opportunities": 12,
        "potential_opportunities": 5,
        "documents_missing": 2,
        "eligible_value": 50000,
        "potential_value": 120000,
        "approval_probability": 89,
        "top_opportunity": "PM Kisan" if role == "farmer" else "NSP Scholarship"
    }

@router.get("/dashboard/student/{user_id}", tags=["Dashboard"])
def get_student_dashboard(user_id: str):
    return _get_mock_dashboard("student", user_id)

@router.get("/dashboard/jobseeker/{user_id}", tags=["Dashboard"])
def get_jobseeker_dashboard(user_id: int, session: Session = Depends(get_session)):
    from app.models.domain import JobSeekerProfile as JobSeekerProfileModel
    user_profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    jobseeker_profile = session.exec(select(JobSeekerProfileModel).where(JobSeekerProfileModel.user_id == user_id)).first()

    # --- Name ---
    user_name = "User"
    if user_profile and user_profile.full_name:
        user_name = user_profile.full_name

    # --- Category ---
    category = "General"
    if user_profile and user_profile.category:
        category = user_profile.category
    if user_profile and user_profile.profile_data:
        category = user_profile.profile_data.get("category", category)

    # --- Qualification & role ---
    qualification = "Graduate"
    preferred_job_role = "Professional"
    experience_years = "Fresher"
    skills = []
    employment_status = "Unemployed"
    has_caste_cert = False
    documents = []

    if jobseeker_profile:
        qualification = jobseeker_profile.education_level or qualification
        preferred_job_role = jobseeker_profile.preferred_job_role or preferred_job_role
        experience_years = f"{int(jobseeker_profile.years_of_experience)} Year(s)" if jobseeker_profile.years_of_experience else "Fresher"
        skills = jobseeker_profile.skills or []
        employment_status = jobseeker_profile.employment_status or employment_status

    if user_profile and user_profile.profile_data:
        pd = user_profile.profile_data
        qualification = pd.get("qualification", qualification)
        preferred_job_role = pd.get("preferred_job_role", preferred_job_role)
        if pd.get("experience_years"):
            try:
                yrs = float(pd["experience_years"])
                experience_years = f"{int(yrs)} Year(s)" if yrs >= 1 else "Fresher"
            except Exception:
                pass
        if pd.get("skills"):
            skills = pd["skills"]
        if pd.get("employment_status"):
            employment_status = pd["employment_status"]
        documents = pd.get("documents") or []
        if "Caste Certificate" in documents:
            has_caste_cert = True

    # --- Location ---
    state = user_profile.state if user_profile else ""
    district = user_profile.district if user_profile else ""

    # --- Readiness / Documents ---
    docs_needed = ["Aadhaar", "Graduation Certificate", "Caste Certificate"]
    documents_missing = sum(1 for d in docs_needed if d not in documents)

    profile_completion = 60
    if user_profile:
        profile_completion += 15
    if jobseeker_profile or (user_profile and user_profile.profile_data):
        profile_completion += 15
    if skills:
        profile_completion += 10
    profile_completion = min(profile_completion, 100)

    doc_score = max(0, 100 - documents_missing * 15)
    skill_score = min(100, 60 + len(skills) * 5)
    overall_readiness = round((profile_completion + doc_score + skill_score) / 3)

    eligible_value = 44900 + (8000 if has_caste_cert else 0)

    return {
        "success": True,
        "message": "Jobseeker dashboard retrieved successfully",
        "user_name": user_name,
        "category": category,
        "qualification": qualification,
        "preferred_job_role": preferred_job_role,
        "experience_years": experience_years,
        "skills": skills,
        "employment_status": employment_status,
        "state": state,
        "district": district,
        "has_caste_cert": has_caste_cert,
        "completion_percentage": profile_completion,
        "readiness_score": overall_readiness,
        "profile_data_score": profile_completion,
        "document_score": doc_score,
        "skills_score": skill_score,
        "eligible_opportunities": 4,
        "potential_opportunities": 5,
        "documents_missing": documents_missing,
        "eligible_value": eligible_value,
        "potential_value": 120000,
        "approval_probability": 89,
        "top_opportunity": "SSC CGL 2026"
    }

@router.get("/dashboard/entrepreneur/{user_id}", tags=["Dashboard"])
def get_entrepreneur_dashboard(user_id: str):
    return _get_mock_dashboard("entrepreneur", user_id)

@router.get("/dashboard/women-entrepreneur/{user_id}", tags=["Dashboard"])
def get_women_entrepreneur_dashboard(user_id: str):
    return _get_mock_dashboard("women_entrepreneur", user_id)

@router.get("/dashboard/startup/{user_id}", tags=["Dashboard"])
def get_startup_dashboard(user_id: str):
    return _get_mock_dashboard("startup", user_id)

@router.get("/dashboard/senior-citizen/{user_id}", tags=["Dashboard"])
def get_senior_citizen_dashboard(user_id: str):
    return _get_mock_dashboard("senior_citizen", user_id)
