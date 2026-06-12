from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

router = APIRouter()

class StudentProfile(BaseModel):
    education_level: str
    current_course: str
    institution_type: str
    annual_family_income: float
    previous_year_marks_percentage: float
    is_orphan: bool = False
    is_disabled: bool = False

class FarmerProfile(BaseModel):
    land_size_acres: float
    land_type: str
    primary_crop: str
    pm_kisan_id: Optional[str] = None
    has_kisan_credit_card: bool = False
    annual_income: float

class JobSeekerProfile(BaseModel):
    education_level: str
    skills: List[str]
    employment_status: str
    years_of_experience: float = 0.0
    preferred_job_role: str
    is_disabled: bool = False

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
def get_profile_status(user_id: int, role: str):
    """Get profile completion % and missing fields."""
    return {"completion_percentage": 100, "missing_fields": []}

@router.put("/profile/{user_id}/{role}", tags=["Profile"])
def update_role_profile(user_id: int, role: str, profile_data: Dict[str, Any]):
    """Update role-specific profile (triggers AI engines)."""
    # In a real app we'd validate profile_data against the correct Pydantic model
    return {"message": f"{role} profile updated successfully."}
