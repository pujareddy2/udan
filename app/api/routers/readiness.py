from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.core.db import get_session
from app.models.domain import UserProfile, FarmerProfile, User

router = APIRouter()

@router.get("/readiness", tags=["Readiness Engine"])
def get_readiness(user_id: int = None, session: Session = Depends(get_session)):
    doc_readiness = 75
    profile_readiness = 90
    eligibility_readiness = 86
    digital_readiness = 82
    missing_docs = ["Income Certificate"]
    
    is_student = False
    if user_id:
        user = session.get(User, user_id)
        if user and (user.module_type == "student" or user.module_type == "students"):
            is_student = True

    if is_student:
        profile_readiness = 90
        doc_readiness = 75
        academic_readiness = 88
        skills_readiness = 76
        overall = 82
        
        # Check database profile if exists to make it slightly dynamic
        if user_id:
            user_profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
            if user_profile and user_profile.profile_data:
                profile_data = user_profile.profile_data
                docs = profile_data.get("documents", [])
                # If they have some docs, update doc readiness
                if len(docs) > 0:
                    doc_readiness = min(100, 40 + len(docs) * 15)
                # Compute dynamic overall
                overall = (profile_readiness + doc_readiness + academic_readiness + skills_readiness) // 4
        
        return {
            "overall_score": overall,
            "breakdown": {
                "profile": profile_readiness,
                "documents": doc_readiness,
                "academic": academic_readiness,
                "skills": skills_readiness
            },
            "overall_readiness": overall,
            "profile_readiness": profile_readiness,
            "document_readiness": doc_readiness,
            "academic_readiness": academic_readiness,
            "skills_readiness": skills_readiness,
            "missing_documents": ["Income Certificate", "Bonafide Certificate", "EWS Certificate"]
        }

    if user_id:
        user_profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
        farmer_profile = session.exec(select(FarmerProfile).where(FarmerProfile.user_id == user_id)).first()

        if user_profile:
            profile_readiness = 90
            docs = (user_profile.profile_data or {}).get("documents", [])
            doc_readiness = min(100, len(docs) * 25) if docs else 40
            smart = (user_profile.profile_data or {}).get("smartphone", False)
            internet = (user_profile.profile_data or {}).get("internet_access", False)
            digital_readiness = (50 if smart else 0) + (50 if internet else 0)
            
            required_student_docs = {
                "aadhaar": "Aadhaar Card",
                "student_id": "Student ID Card",
                "bonafide": "Bonafide Certificate",
                "income_certificate": "Income Certificate"
            }
            missing_docs = []
            for key, name in required_student_docs.items():
                if key not in docs and name not in docs:
                    missing_docs.append(name)
            if not missing_docs and not docs:
                missing_docs = ["Income Certificate"]

        if farmer_profile:
            eligibility_readiness = min(100, 70 + int(bool(farmer_profile.land_size_acres)) * 15)

    overall = (doc_readiness + profile_readiness + eligibility_readiness + digital_readiness) // 4

    return {
        "overall_score": overall,
        "breakdown": {
            "profile": profile_readiness,
            "documents": doc_readiness,
            "eligibility": eligibility_readiness,
            "digital": digital_readiness
        },
        "overall_readiness": overall,
        "profile_readiness": profile_readiness,
        "document_readiness": doc_readiness,
        "eligibility_readiness": eligibility_readiness,
        "digital_readiness": digital_readiness,
        "missing_documents": missing_docs
    }

