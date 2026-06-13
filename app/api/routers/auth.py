from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select
from typing import Dict, Any, List, Optional

from app.core.db import get_session
from app.models.domain import User, UserProfile, UserRole, FarmerProfile, JobSeekerProfile

router = APIRouter()

def get_password_hash(password: str) -> str:
    return password + "_hashed"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return plain_password + "_hashed" == hashed_password

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class ProfileRequest(BaseModel):
    full_name: Optional[str] = None
    name: Optional[str] = None
    mobile_number: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    preferred_language: Optional[str] = None

class RoleRequest(BaseModel):
    role: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

ALLOWED_ROLES = [
    "student",
    "farmer",
    "jobseeker",
    "entrepreneur",
    "women_entrepreneur",
    "startup",
    "senior_citizen"
]

@router.post("/auth/register", status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register(req: RegisterRequest, session: Session = Depends(get_session)):
    if len(req.password) < 4:
        raise HTTPException(status_code=400, detail="Password too short")
    
    existing_user = session.exec(select(User).where(User.email == req.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    user = User(
        email=req.email,
        password_hash=get_password_hash(req.password)
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    user_id = str(user.id)
    return {
        "success": True,
        "user_id": user_id,
        "userId": user_id,
        "id": user_id,
        "message": "User registered successfully"
    }

@router.post("/auth/{user_id}/profile", tags=["Auth"])
def update_auth_profile(user_id: int, req: ProfileRequest, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    resolved_full_name = req.full_name or req.name or ""
    profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    if not profile:
        profile = UserProfile(
            user_id=user_id,
            full_name=resolved_full_name,
            mobile_number=req.mobile_number or "",
            age=25,
            gender=req.gender or "",
            state=req.state or "",
            district=req.district or "",
            category="General",
            preferred_language=req.preferred_language or "en"
        )
    else:
        profile.full_name = resolved_full_name or profile.full_name
        if req.mobile_number is not None:
            profile.mobile_number = req.mobile_number
        if req.gender is not None:
            profile.gender = req.gender
        if req.state is not None:
            profile.state = req.state
        if req.district is not None:
            profile.district = req.district
        if req.preferred_language is not None:
            profile.preferred_language = req.preferred_language
        
    session.add(profile)
    session.commit()
    return {"success": True, "message": "Profile updated successfully"}

@router.post("/auth/{user_id}/role", tags=["Auth"])
def assign_auth_role(user_id: int, req: RoleRequest, session: Session = Depends(get_session)):
    # Normalize plural to singular if needed
    role = req.role.lower()
    if role.endswith('s') and role[:-1] in ALLOWED_ROLES:
        role = role[:-1]
    
    if role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role '{req.role}'. Allowed: {ALLOWED_ROLES}")
        
    user = session.get(User, user_id)
    if user:
        user.module_type = role
        session.add(user)
        session.commit()
        
    return {"success": True, "role": role, "message": "Role assigned successfully"}

@router.post("/auth/login", tags=["Auth"])
def login(req: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == req.email)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    if not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    user_id = str(user.id)
    return {
        "success": True,
        "user_id": user_id,
        "userId": user_id,
        "id": user_id,
        "role": user.module_type,
        "access_token": "mock_jwt_token_12345",
        "profile_completion": 100
    }

@router.put("/profile/{user_id}/farmer", tags=["Profile"])
def update_farmer_profile(user_id: int, payload: dict, session: Session = Depends(get_session)):
    user_profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    if not user_profile:
        user_profile = UserProfile(user_id=user_id)
        session.add(user_profile)
    
    # Store dynamic fields into JSON column
    user_profile.profile_data = payload
    session.add(user_profile)
    
    # Also update or create FarmerProfile for specific structured data
    farmer_profile = session.exec(select(FarmerProfile).where(FarmerProfile.user_id == user_id)).first()
    if not farmer_profile:
        farmer_profile = FarmerProfile(
            user_id=user_id,
            land_size_acres=float(payload.get("land_area", 0.0) or 0.0),
            land_type="Irrigated" if payload.get("owns_land") else "None",
            primary_crop=payload.get("crop_type", "Unknown"),
            pm_kisan_id="Yes" if payload.get("pm_kisan_enrolled") else None,
            annual_income=float(payload.get("annual_income", 0.0) or 0.0)
        )
    else:
        farmer_profile.land_size_acres = float(payload.get("land_area", farmer_profile.land_size_acres) or 0.0)
        farmer_profile.primary_crop = payload.get("crop_type", farmer_profile.primary_crop)
        farmer_profile.annual_income = float(payload.get("annual_income", farmer_profile.annual_income) or 0.0)
    
    session.add(farmer_profile)
    session.commit()
    return {"success": True, "message": "Farmer profile updated"}

class JobSeekerProfileSaveRequest(BaseModel):
    state: Optional[str] = None
    district: Optional[str] = None
    village_city: Optional[str] = None
    urban_or_rural: Optional[str] = None
    
    category: Optional[str] = None
    annual_family_income: Optional[str] = None
    family_size: Optional[int] = None
    special_category: Optional[str] = None
    
    qualification: Optional[str] = None
    experience_years: Optional[str] = None
    preferred_job_role: Optional[str] = None
    employment_status: Optional[str] = None
    
    target_sector: Optional[str] = None
    preferred_job_type: Optional[str] = None
    
    skills: Optional[List[str]] = None
    smartphone: Optional[bool] = None
    internet_access: Optional[bool] = None
    digital_payment_access: Optional[bool] = None
    
    documents: Optional[List[str]] = None

class ProfileUpdateResponse(BaseModel):
    success: bool
    message: str

@router.put("/profile/{user_id}/jobseeker", response_model=ProfileUpdateResponse, tags=["Profile"])
def update_jobseeker_profile(user_id: int, req: JobSeekerProfileSaveRequest, session: Session = Depends(get_session)):
    user_profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    if not user_profile:
        user_profile = UserProfile(user_id=user_id)
        session.add(user_profile)
    
    # Store complete payload into JSON column
    payload = req.dict()
    user_profile.profile_data = payload
    session.add(user_profile)
    
    # Also update or create JobSeekerProfile for specific structured data
    jobseeker_profile = session.exec(select(JobSeekerProfile).where(JobSeekerProfile.user_id == user_id)).first()
    
    try:
        years_exp = float(req.experience_years) if req.experience_years else 0.0
    except ValueError:
        years_exp = 0.0
        
    is_disabled = (req.special_category == "PwD")
    
    if not jobseeker_profile:
        jobseeker_profile = JobSeekerProfile(
            user_id=user_id,
            education_level=req.qualification or "Unknown",
            skills=req.skills or [],
            employment_status=req.employment_status or "Unemployed",
            years_of_experience=years_exp,
            preferred_job_role=req.preferred_job_role or "Unknown",
            is_disabled=is_disabled
        )
    else:
        jobseeker_profile.education_level = req.qualification or jobseeker_profile.education_level
        if req.skills is not None:
            jobseeker_profile.skills = req.skills
        jobseeker_profile.employment_status = req.employment_status or jobseeker_profile.employment_status
        jobseeker_profile.years_of_experience = years_exp
        jobseeker_profile.preferred_job_role = req.preferred_job_role or jobseeker_profile.preferred_job_role
        jobseeker_profile.is_disabled = is_disabled
        
    session.add(jobseeker_profile)
    session.commit()
    return ProfileUpdateResponse(success=True, message="Job Seeker profile updated")

@router.post("/profile-context/generate", tags=["Profile"])
def generate_profile_context():
    return {"success": True}

@router.post("/ai-discovery/run", tags=["Profile"])
def ai_discovery_run():
    return {"success": True}

@router.post("/eligibility/run", tags=["Profile"])
def eligibility_run():
    return {"success": True}
