from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.core.db import get_session
from app.models.domain import UserProfile

router = APIRouter()

@router.get("/readiness", tags=["Readiness Engine"])
def get_readiness(user_id: int = None, session: Session = Depends(get_session)):
    doc_readiness = 75
    profile_readiness = 90
    eligibility_readiness = 86
    digital_readiness = 82
    
    if user_id:
        user_profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
        if user_profile and user_profile.profile_data:
            # Estimate document readiness
            docs = user_profile.profile_data.get("documents", [])
            doc_readiness = min(100, len(docs) * 20)
            
            # Estimate digital readiness
            smart = user_profile.profile_data.get("smartphone", False)
            internet = user_profile.profile_data.get("internet_access", False)
            digital_readiness = (50 if smart else 0) + (50 if internet else 0)
            
    overall = (doc_readiness + profile_readiness + eligibility_readiness + digital_readiness) // 4
    
    return {
        "overall_readiness": overall,
        "profile_readiness": profile_readiness,
        "document_readiness": doc_readiness,
        "eligibility_readiness": eligibility_readiness,
        "digital_readiness": digital_readiness
    }
