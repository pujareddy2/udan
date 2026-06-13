from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.core.db import get_session
from app.models.domain import FarmerProfile

router = APIRouter()

@router.get("/farmer/services", tags=["Intelligence"])
def get_farmer_services():
    return {
        "services": [
            {
                "name": "PM Kisan",
                "description": "Direct Income Support",
                "icon": "pm_kisan"
            },
            {
                "name": "Crop Insurance",
                "description": "Protect your harvest",
                "icon": "crop_insurance"
            },
            {
                "name": "Subsidies",
                "description": "Machinery & Seeds",
                "icon": "subsidies"
            },
            {
                "name": "Agriculture Loans",
                "description": "Kisan Credit Card",
                "icon": "agri_loans"
            }
        ]
    }

@router.get("/farmer/recommendations", tags=["Intelligence"])
def get_farmer_recommendations(user_id: int = None, session: Session = Depends(get_session)):
    recs = []
    
    if user_id:
        farmer_profile = session.exec(select(FarmerProfile).where(FarmerProfile.user_id == user_id)).first()
        if farmer_profile and farmer_profile.land_size_acres > 0:
            recs.append({
                "scheme": "Rythu Bandhu",
                "benefit": f"₹{10000 * farmer_profile.land_size_acres}",
                "confidence": 95,
                "reason": f"{farmer_profile.land_size_acres} acres {farmer_profile.land_type} land"
            })
            
    # Default fallback
    if not recs:
        recs.append({
            "scheme": "PM Kisan",
            "benefit": "₹6000",
            "confidence": 90,
            "reason": "Registered Farmer"
        })
        
    return {
        "recommendations": recs
    }

@router.get("/approval", tags=["Intelligence"])
def get_approval_intelligence():
    return {
        "probability": 87,
        "level": "High"
    }


@router.get("/opportunity-health/{opportunity_id}", tags=["Intelligence"])
def get_opportunity_health(opportunity_id: str):
    return {
        "opportunity_id": opportunity_id,
        "health_score": 95,
        "status": "Apply Immediately"
    }

@router.get("/trust/{opportunity_id}", tags=["Intelligence"])
def get_trust_score(opportunity_id: str):
    return {
        "opportunity_id": opportunity_id,
        "trust_score": 100,
        "source_type": "Government"
    }
