from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from typing import Dict, Any

from app.core.db import get_session
from app.models.domain import (
    User, StudentProfile, FarmerProfile, JobSeekerProfile,
    EntrepreneurProfile, WomenEntrepreneurProfile, StartupProfile, SeniorCitizenProfile
)
from app.services.profile_completion_service import analyze_profile
from app.services.event_triggers import schedule_background_recalculation

# Map string roles to SQLModel classes
ROLE_MODELS = {
    "student": StudentProfile,
    "farmer": FarmerProfile,
    "jobseeker": JobSeekerProfile,
    "entrepreneur": EntrepreneurProfile,
    "women_entrepreneur": WomenEntrepreneurProfile,
    "startup": StartupProfile,
    "senior_citizen": SeniorCitizenProfile
}

router = APIRouter(prefix="/profile", tags=["Profile Completion"])

@router.get("/{user_id}/{role}/status")
def get_profile_status_endpoint(user_id: int, role: str, session: Session = Depends(get_session)):
    """
    Get the current completion %, missing fields, and follow-up questions for a role.
    """
    if role not in ROLE_MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid role: {role}")
        
    model = ROLE_MODELS[role]
    profile = session.exec(select(model).where(model.user_id == user_id)).first()
    
    # Analyze the profile
    analysis = analyze_profile(profile, role)
    return analysis

@router.put("/{user_id}/{role}")
def update_profile_endpoint(
    user_id: int, 
    role: str, 
    data: Dict[str, Any], 
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """
    Update the role-specific profile and trigger background intelligence recalculations.
    """
    if role not in ROLE_MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid role: {role}")
        
    model = ROLE_MODELS[role]
    profile = session.exec(select(model).where(model.user_id == user_id)).first()
    
    # If it doesn't exist, create it
    if not profile:
        profile = model(user_id=user_id)
        session.add(profile)
        
    # Update fields dynamically based on the payload
    # Note: In production, we use the specific Pydantic schemas created in `schemas/profile.py`
    # to strictly validate `data` before this step.
    for key, value in data.items():
        if hasattr(profile, key):
            setattr(profile, key, value)
            
    session.commit()
    session.refresh(profile)
    
    # TRIGGER BACKGROUND ENGINES
    schedule_background_recalculation(background_tasks, user_id)
    
    # Calculate new status
    new_analysis = analyze_profile(profile, role)
    
    return {
        "message": "Profile updated successfully.",
        "analysis": new_analysis
    }
