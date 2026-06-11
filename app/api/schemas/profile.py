from pydantic import BaseModel, Field
from typing import Optional, List

class StudentProfileUpdate(BaseModel):
    education_level: Optional[str] = None
    current_course: Optional[str] = None
    institution_type: Optional[str] = None
    annual_family_income: Optional[float] = None
    previous_year_marks_percentage: Optional[float] = None
    is_orphan: Optional[bool] = None
    is_disabled: Optional[bool] = None

class FarmerProfileUpdate(BaseModel):
    land_size_acres: Optional[float] = None
    land_type: Optional[str] = None
    primary_crop: Optional[str] = None
    pm_kisan_id: Optional[str] = None
    has_kisan_credit_card: Optional[bool] = None
    annual_income: Optional[float] = None

class JobSeekerProfileUpdate(BaseModel):
    education_level: Optional[str] = None
    skills: Optional[List[str]] = None
    employment_status: Optional[str] = None
    years_of_experience: Optional[float] = None
    preferred_job_role: Optional[str] = None
    is_disabled: Optional[bool] = None

class EntrepreneurProfileUpdate(BaseModel):
    business_type: Optional[str] = None
    industry_sector: Optional[str] = None
    annual_turnover: Optional[float] = None
    years_in_operation: Optional[float] = None
    msme_udyam_number: Optional[str] = None
    number_of_employees: Optional[int] = None

class WomenEntrepreneurProfileUpdate(BaseModel):
    business_type: Optional[str] = None
    industry_sector: Optional[str] = None
    annual_turnover: Optional[float] = None
    percentage_women_ownership: Optional[float] = None
    msme_udyam_number: Optional[str] = None
    marital_status: Optional[str] = None

class StartupProfileUpdate(BaseModel):
    dpiit_recognized: Optional[bool] = None
    startup_india_id: Optional[str] = None
    funding_stage: Optional[str] = None
    patent_count: Optional[int] = None
    incubator_attached: Optional[bool] = None
    annual_turnover: Optional[float] = None

class SeniorCitizenProfileUpdate(BaseModel):
    marital_status: Optional[str] = None
    living_arrangement: Optional[str] = None
    pension_status: Optional[str] = None
    health_conditions: Optional[List[str]] = None
    annual_income: Optional[float] = None
    is_disabled: Optional[bool] = None
