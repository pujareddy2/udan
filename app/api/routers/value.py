from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.core.db import get_session
from app.models.domain import FarmerProfile, User

router = APIRouter()

@router.get("/value", tags=["Value Engine"])
def get_value_metrics(user_id: int = None, session: Session = Depends(get_session)):
    eligible = 56000
    potential = 120000
    blocked = 30000
    recovery = 64000
    
    if user_id:
        user = session.get(User, user_id)
        if user and (user.module_type == "student" or user.module_type == "students"):
            eligible = 50000
            potential = 180000
            blocked = 70000
            recovery = 70000
        else:
            farmer_profile = session.exec(select(FarmerProfile).where(FarmerProfile.user_id == user_id)).first()
            if farmer_profile:
                base = 6000 # PM Kisan
                if farmer_profile.land_size_acres > 0:
                    base += 10000 * farmer_profile.land_size_acres # Rythu Bandhu
                
                eligible = base
                potential = base + 50000 # Insurance/Loans
                blocked = base if farmer_profile.land_size_acres > 0 else 0
                recovery = blocked
            
    return {
        "eligible_value": eligible,
        "potential_value": potential,
        "blocked_value": blocked,
        "recovery_value": recovery
    }
