from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from app.core.db import get_session
from app.api.schemas.auth import UserRegister, ProfileCreate, RoleCreate
from app.services.auth import register_user, create_profile, assign_role, authenticate_user
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token
from app.api.schemas.common import TokenResponse
from fastapi import HTTPException

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def api_register_user(data: UserRegister, session: Session = Depends(get_session)):
    """
    Step 1: Create Account
    Validates email uniqueness and hashes password.
    """
    user = register_user(session, data)
    return {
        "message": "Account created successfully.",
        "user_id": user.id,
        "email": user.email
    }

@router.post("/login", response_model=TokenResponse)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    """
    Authenticate user and return a JWT Bearer token.
    (Note: `username` field is used for email).
    """
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    roles = [r.role for r in user.roles]
    
    # Generate JWT
    access_token = create_access_token(data={"sub": str(user.id), "roles": roles})
    
    return {"access_token": access_token, "token_type": "bearer", "role_claims": roles}

@router.post("/{user_id}/profile", status_code=status.HTTP_201_CREATED)
def api_create_profile(user_id: int, data: ProfileCreate, session: Session = Depends(get_session)):
    """
    Step 2: Create Common Profile
    Generates unified demographic profile for the user.
    """
    profile = create_profile(session, user_id, data)
    return {
        "message": "Profile created successfully.",
        "profile_id": profile.id,
        "full_name": profile.full_name
    }

@router.post("/{user_id}/role", status_code=status.HTTP_201_CREATED)
def api_assign_role(user_id: int, data: RoleCreate, session: Session = Depends(get_session)):
    """
    Step 3: Role Selection
    Assigns a role to the user. Can be called multiple times for multi-role users.
    """
    role = assign_role(session, user_id, data)
    return {
        "message": f"Role '{role.role}' assigned successfully.",
        "role_id": role.id,
        "assigned_role": role.role
    }
