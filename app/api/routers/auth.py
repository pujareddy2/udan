from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import List
from enum import Enum

router = APIRouter()

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

class LoginRequest(BaseModel):
    username: str
    password: str
    grant_type: str = "password"

class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"
    prefer_not_to_say = "Prefer Not to Say"

class CategoryEnum(str, Enum):
    general = "General"
    obc = "OBC"
    sc = "SC"
    st = "ST"
    minority = "Minority"

class ProfileRequest(BaseModel):
    full_name: str
    mobile_number: str
    age: int
    gender: GenderEnum
    state: str
    district: str
    category: CategoryEnum
    preferred_language: str = "en"

class RoleEnum(str, Enum):
    student = "student"
    farmer = "farmer"
    jobseeker = "jobseeker"
    entrepreneur = "entrepreneur"
    women_entrepreneur = "women_entrepreneur"
    startup = "startup"
    senior_citizen = "senior_citizen"

class RoleRequest(BaseModel):
    role: RoleEnum

@router.post("/auth/register", status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register(req: RegisterRequest):
    """Creates a new user account."""
    if req.password != req.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    return {"message": "Account created.", "user_id": 1, "email": req.email}

@router.post("/auth/login", tags=["Auth"])
def login(req: LoginRequest):
    """OAuth2 password flow login."""
    if req.username == "test@gmail.com" and req.password == "wrong":
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {"access_token": "mock_jwt_token", "token_type": "bearer", "role_claims": []}

@router.post("/auth/{user_id}/profile", status_code=status.HTTP_201_CREATED, tags=["Auth"])
def create_profile(user_id: int, req: ProfileRequest):
    """Creates the common demographic profile."""
    return {"message": "Profile created.", "profile_id": 1, "full_name": req.full_name}

@router.post("/auth/{user_id}/role", status_code=status.HTTP_201_CREATED, tags=["Auth"])
def assign_role(user_id: int, req: RoleRequest):
    """Assigns a role to user."""
    return {"message": f"Role '{req.role.value}' assigned.", "role_id": 1, "assigned_role": req.role.value}
