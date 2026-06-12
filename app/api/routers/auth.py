from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select
from typing import Dict, Any

from app.core.db import get_session
from app.models.domain import User, UserProfile, UserRole, FarmerProfile

router = APIRouter()

def get_password_hash(password: str) -> str:
    return password + "_hashed"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return plain_password + "_hashed" == hashed_password

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class ProfileRequest(BaseModel):
    full_name: str
    mobile_number: str
    gender: str
    date_of_birth: str
    state: str
    district: str
    preferred_language: str

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
        
    profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    if not profile:
        profile = UserProfile(
            user_id=user_id,
            full_name=req.full_name,
            mobile_number=req.mobile_number,
            age=25,
            gender=req.gender,
            state=req.state,
            district=req.district,
            category="General",
            preferred_language=req.preferred_language
        )
    else:
        profile.full_name = req.full_name
        profile.mobile_number = req.mobile_number
        profile.gender = req.gender
        profile.state = req.state
        profile.district = req.district
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
        raise HTTPException(status_code=404, detail="UserProfile not found")
    
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

@router.post("/profile-context/generate", tags=["Profile"])
def generate_profile_context():
    return {"success": True}

@router.post("/ai-discovery/run", tags=["Profile"])
def ai_discovery_run():
    return {"success": True}

@router.post("/eligibility/run", tags=["Profile"])
def eligibility_run():
    return {"success": True}
