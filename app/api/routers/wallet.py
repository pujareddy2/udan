from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from app.core.db import get_session
from app.models.domain import UserProfile, FarmerProfile

router = APIRouter()

@router.get("/wallet/summary", tags=["Wallet"])
def get_wallet_summary(user_id: int = None, session: Session = Depends(get_session)):
    ready = 4
    blocked = 2
    needs_clarification = 1
    applied = 3
    under_review = 1
    approved = 2
    
    if user_id:
        farmer_profile = session.exec(select(FarmerProfile).where(FarmerProfile.user_id == user_id)).first()
        if farmer_profile:
            ready = 1 if farmer_profile.land_size_acres > 0 else 0
            blocked = 0 if farmer_profile.land_size_acres > 0 else 1
            
    return {
        "ready": ready,
        "blocked": blocked,
        "needs_clarification": needs_clarification,
        "applied": applied,
        "under_review": under_review,
        "approved": approved
    }

@router.get("/wallet/opportunities", tags=["Wallet"])
def get_wallet_opportunities(user_id: int = None, session: Session = Depends(get_session)):
    opportunities = []
    
    # Default PM Kisan
    opportunities.append({
        "id": "PM_KISAN",
        "title": "PM Kisan Samman Nidhi",
        "category": "Income",
        "benefit": "₹6000",
        "eligibility_score": 96,
        "approval_probability": 92,
        "apply_link": "https://pmkisan.gov.in/"
    })
    
    if user_id:
        farmer_profile = session.exec(select(FarmerProfile).where(FarmerProfile.user_id == user_id)).first()
        if farmer_profile and farmer_profile.land_size_acres > 0:
            opportunities.append({
                "id": "RYTHU_BANDHU",
                "title": "Rythu Bandhu",
                "category": "Subsidy",
                "benefit": f"₹{10000 * farmer_profile.land_size_acres}",
                "eligibility_score": 99,
                "approval_probability": 98,
                "apply_link": "http://rythubandhu.telangana.gov.in/"
            })
            
            opportunities.append({
                "id": "CROP_INSURANCE",
                "title": "PM Fasal Bima Yojana",
                "category": "Insurance",
                "benefit": "Full Coverage",
                "eligibility_score": 85,
                "approval_probability": 80,
                "apply_link": "https://pmfby.gov.in/"
            })
            
    return {
        "opportunities": opportunities
    }
