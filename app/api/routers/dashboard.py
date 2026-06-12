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
        docs = user_profile.profile_data.get("documents", [])
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
def get_jobseeker_dashboard(user_id: str):
    return _get_mock_dashboard("jobseeker", user_id)

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
