from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from app.core.db import get_session
from app.models.domain import UserProfile, FarmerProfile, User

router = APIRouter()

@router.get("/wallet/summary", tags=["Wallet"])
def get_wallet_summary(user_id: int = None, session: Session = Depends(get_session)):
    ready = 4
    blocked = 2
    needs_clarification = 1
    applied = 3
    under_review = 1
    approved = 2
    rejected = 1
    
    if user_id:
        user = session.get(User, user_id)
        if user and (user.module_type == "student" or user.module_type == "students"):
            ready = 6
            blocked = 2
            needs_clarification = 0
            applied = 4
            under_review = 2
            approved = 1
            rejected = 1
        else:
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
        "approved": approved,
        "rejected": rejected
    }

@router.get("/wallet/opportunities", tags=["Wallet"])
def get_wallet_opportunities(user_id: int = None, session: Session = Depends(get_session)):
    opportunities = []
    
    user = None
    if user_id:
        user = session.get(User, user_id)
        
    if user and (user.module_type == "student" or user.module_type == "students"):
        opportunities.append({
            "id": "INSPIRE",
            "title": "INSPIRE Scholarship",
            "category": "Scholarships",
            "benefit": "₹80,000 / year",
            "eligibility_score": 96,
            "approval_probability": 89,
            "deadline": "5 Days Left",
            "missing_requirement": "Income Certificate",
            "apply_link": "https://online-inspire.gov.in/"
        })
        opportunities.append({
            "id": "SIH_2026",
            "title": "Smart India Hackathon 2026",
            "category": "Hackathons",
            "benefit": "₹1,00,000 prize",
            "eligibility_score": 90,
            "approval_probability": 85,
            "deadline": "8 Days Left",
            "missing_requirement": "None",
            "apply_link": "https://sih.gov.in/"
        })
        opportunities.append({
            "id": "AICTE_INTERN",
            "title": "AICTE Research Internship",
            "category": "Internships",
            "benefit": "₹15,000 / month",
            "eligibility_score": 85,
            "approval_probability": 83,
            "deadline": "3 Days Left",
            "missing_requirement": "Bonafide",
            "apply_link": "https://internship.aicte-india.org/"
        })
        opportunities.append({
            "id": "NSP_SCHOLARSHIP",
            "title": "National Means-cum-Merit Scholarship",
            "category": "Scholarships",
            "benefit": "₹12,000 / year",
            "eligibility_score": 91,
            "approval_probability": 91,
            "deadline": "31 Jul 2026",
            "missing_requirement": "None",
            "apply_link": "https://scholarships.gov.in/"
        })
    else:
        opportunities.append({
            "id": "PM_KISAN",
            "title": "PM Kisan Samman Nidhi",
            "category": "Income",
            "benefit": "₹6,000",
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
