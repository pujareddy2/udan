from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
import uuid

router = APIRouter()

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
def register(req: RegisterRequest):
    """Creates a new user account."""
    if len(req.password) < 4:
        raise HTTPException(status_code=400, detail="Password too short")

    user_id = str(uuid.uuid4())
    
    return {
        "success": True,
        "user_id": user_id,
        "message": "User registered successfully"
    }

@router.post("/auth/{user_id}/profile", tags=["Auth"])
def update_auth_profile(user_id: str, req: ProfileRequest):
    """Saves the basic profile details during registration."""
    return {
        "success": True,
        "message": "Profile updated successfully"
    }

@router.post("/auth/{user_id}/role", tags=["Auth"])
def assign_auth_role(user_id: str, req: RoleRequest):
    """Assigns the primary persona role."""
    if req.role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Allowed: {ALLOWED_ROLES}")
    return {
        "success": True,
        "role": req.role,
        "message": "Role assigned successfully"
    }

@router.post("/auth/login", tags=["Auth"])
def login(req: LoginRequest):
    """Login with email and password."""
    # Mock Validation
    if req.email == "test@gmail.com" and req.password == "wrong":
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    return {
        "success": True,
        "user_id": "123", # Mock ID
        "role": "farmer", # Mock Role
        "access_token": "mock_jwt_token_12345",
        "profile_completion": 18
    }
