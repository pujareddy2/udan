from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.core.db import get_session
from app.models.domain import UserProfile, FarmerProfile, User, Document

router = APIRouter()

@router.get("/readiness", tags=["Readiness Engine"])
def get_readiness(user_id: int = None, session: Session = Depends(get_session)):
    doc_readiness = 75
    profile_readiness = 90
    eligibility_readiness = 86
    digital_readiness = 82
    missing_docs = ["Income Certificate"]
    
    is_student = False
    is_jobseeker = False
    if user_id:
        user = session.get(User, user_id)
        if user:
            if user.module_type in ["student", "students"]:
                is_student = True
            elif user.module_type in ["jobseeker", "jobseekers"]:
                is_jobseeker = True

    if is_jobseeker:
        user_docs = session.exec(select(Document).where(Document.user_id == user_id)).all()
        # Check verified documents
        verified_docs = {d.document_master.document_name for d in user_docs if d.status == "Verified" and d.document_master}
        
        doc_score = 70
        if "Caste Certificate (OBC)" in verified_docs:
            doc_score += 20
        if "Income Certificate" in verified_docs:
            doc_score += 10
            
        # Check skills
        from app.models.domain import JobSeekerProfile
        js_profile = session.exec(select(JobSeekerProfile).where(JobSeekerProfile.user_id == user_id)).first()
        skills_score = 80
        if js_profile:
            skills = js_profile.skills or []
            if "Java Programming" in skills:
                skills_score = 100
                
        profile_score = 85
        overall_score = (profile_score + doc_score + skills_score) // 3
        
        return {
            "overall": overall_score,
            "profile": profile_score,
            "documents": doc_score,
            "skills": skills_score,
            "overall_score": overall_score,
            "overall_readiness": overall_score
        }

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

