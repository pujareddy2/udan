from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.core.db import get_session
from app.api.schemas.profile import JobSeekerProfileSaveRequest, ProfileUpdateResponse
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from app.models.domain import UserProfile, JobSeekerProfile
router = APIRouter()

class StudentProfile(BaseModel):
    college_name: str
    university: str
    degree: str
    branch: str
    specialization: str
    current_year: int
    graduation_year: int
    cgpa: float
    percentage: float
    state: str
    district: str
    category: str
    special_category: str
    annual_family_income: float
    family_size: int
    documents: List[str] = []
    opportunity_interests: List[str] = []
    smartphone: bool = False
    internet_access: bool = False
    tenth_percentage: float
    twelfth_percentage: float
    diploma_percentage: Optional[float] = None
    skills: List[str] = []
    certifications: List[str] = []
    projects: List[str] = []
    hackathons: List[str] = []
    research_papers: List[str] = []
    career_goals: List[str] = []

class FarmerProfile(BaseModel):
    land_size_acres: float
    land_type: str
    primary_crop: str
    pm_kisan_id: Optional[str] = None
    has_kisan_credit_card: bool = False
    annual_income: float

class JobSeekerProfile(BaseModel):
    highest_qualification: str
    degree: str
    branch: str
    graduation_year: int
    cgpa: float
    category: str
    annual_family_income: float
    skills: List[str] = []
    experience_years: float = 0.0
    internships: List[str] = []
    projects: List[str] = []
    certifications: List[str] = []
    preferred_job_type: List[str] = []
    preferred_location: List[str] = []
    expected_salary: float
    documents: List[str] = []

class EntrepreneurProfile(BaseModel):
    business_type: str
    industry_sector: str
    annual_turnover: float
    years_in_operation: float
    msme_udyam_number: Optional[str] = None
    number_of_employees: int = 1

class WomenEntrepreneurProfile(BaseModel):
    business_type: str
    industry_sector: str
    annual_turnover: float
    percentage_women_ownership: float
    msme_udyam_number: Optional[str] = None
    marital_status: str

class StartupProfile(BaseModel):
    dpiit_recognized: bool
    startup_india_id: Optional[str] = None
    funding_stage: str
    patent_count: int = 0
    incubator_attached: bool = False
    annual_turnover: float

class SeniorCitizenProfile(BaseModel):
    marital_status: str
    living_arrangement: str
    pension_status: str
    health_conditions: List[str] = []
    annual_income: float
    is_disabled: bool = False

@router.get("/profile/{user_id}/{role}/status", tags=["Profile"])
def get_profile_status(user_id: str, role: str):
    """Get profile completion % and missing fields."""
    if role == "student":
        return {
            "completion_percentage": 100,
            "fields_completed": 45,
            "total_fields": 53,
            "documents_ready": 4,
            "documents_required": 7,
            "skills_count": 8,
            "interests_count": 4,
            "profile_strength": "Strong",
            "missing_fields": [
                "income_certificate",
                "cgpa"
            ]
        }
    elif role == "jobseeker":
        return {
            "completion_percentage": 100,
            "profile_strength": "Strong",
            "skills_count": 8,
            "documents_ready": 4,
            "experience_score": 70,
            "missing_fields": [
                "resume",
                "expected_salary"
            ]
        }
    return {
        "completion_percentage": 100,
        "next_page": f"{role}_profile"
    }

# @router.put("/profile/{user_id}/{role}", tags=["Profile"])

@router.put("/profile/{user_id}/jobseeker", response_model=ProfileUpdateResponse, tags=["Profile"])
def update_jobseeker_profile(user_id: int, req: JobSeekerProfileSaveRequest, session: Session = Depends(get_session)):
    # Store complete payload
    payload = req.dict()
    user_profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    if not user_profile:
        user_profile = UserProfile(user_id=user_id)
        session.add(user_profile)
    user_profile.profile_data = payload
    session.add(user_profile)
    # Update or create structured JobSeekerProfile
    jobseeker = session.exec(select(JobSeekerProfile).where(JobSeekerProfile.user_id == user_id)).first()
    if not jobseeker:
        jobseeker = JobSeekerProfile(
            user_id=user_id,
            education_level=req.education_level or "",
            skills=req.skills or [],
            employment_status=req.employment_status or "",
            years_of_experience=req.years_of_experience or 0.0,
            preferred_job_role=req.preferred_job_role or "",
            is_disabled=req.is_disabled or False,
        )
    else:
        jobseeker.education_level = req.education_level or jobseeker.education_level
        if req.skills is not None:
            jobseeker.skills = req.skills
        jobseeker.employment_status = req.employment_status or jobseeker.employment_status
        jobseeker.years_of_experience = req.years_of_experience or jobseeker.years_of_experience
        jobseeker.preferred_job_role = req.preferred_job_role or jobseeker.preferred_job_role
        jobseeker.is_disabled = req.is_disabled if req.is_disabled is not None else jobseeker.is_disabled
    session.add(jobseeker)
    session.commit()
    return ProfileUpdateResponse(success=True, message="Job Seeker profile updated")
def update_role_profile(user_id: str, role: str, profile_data: Dict[str, Any]):
    """Update role-specific profile (triggers AI engines)."""
    if role == "student":
        return {
            "success": True,
            "user_id": user_id,
            "role": "student",
            "completion_percentage": 84,
            "profile_strength": "Strong",
            "documents_ready": len(profile_data.get("documents", [])) if "documents" in profile_data else 4,
            "skills_count": len(profile_data.get("skills", [])) if "skills" in profile_data else 8,
            "interests_count": len(profile_data.get("opportunity_interests", [])) if "opportunity_interests" in profile_data else 4,
            "next_step": "dashboard"
        }
    elif role == "jobseeker":
        return {
            "success": True,
            "user_id": user_id,
            "role": "jobseeker",
            "completion_percentage": 84,
            "profile_strength": "Strong",
            "documents_ready": len(profile_data.get("documents", [])) if "documents" in profile_data else 4,
            "skills_count": len(profile_data.get("skills", [])) if "skills" in profile_data else 8,
            "next_step": "dashboard"
        }
    return {"message": f"{role} profile updated successfully."}
