from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.core.db import get_session
from app.models.domain import UserProfile

router = APIRouter()

@router.get("/{module}/documents/summary", tags=["Documents"])
def get_module_documents_summary(module: str, user_id: int = None, session: Session = Depends(get_session)):
    available = 5
    missing = ["Income Certificate", "Land Passbook"]
    
    if user_id:
        user_profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
        if user_profile and user_profile.profile_data:
            docs = user_profile.profile_data.get("documents", [])
            available = len(docs)
            missing = []
            if "Aadhaar" not in docs: missing.append("Aadhaar")
            if "Land Passbook" not in docs: missing.append("Land Passbook")
            if "Income Certificate" not in docs: missing.append("Income Certificate")
            
    return {
        "available_documents": available,
        "missing_documents": len(missing),
        "missing": missing
    }

@router.get("/documents/{document_name}", tags=["Documents"])
def get_document_details(document_name: str):
    return {
        "name": document_name,
        "sample_image": "",
        "authority": "MeeSeva",
        "validity": "1 Year",
        "purpose": "Income Verification" if "Income" in document_name else "Verification",
        "required_for": [
            "Scholarships",
            "Subsidies"
        ]
    }

@router.get("/documents/{document_name}/recovery-guide", tags=["Documents"])
def get_document_recovery_guide(document_name: str):
    return {
        "document": document_name,
        "apply_link": "https://ts.meeseva.telangana.gov.in/",
        "required_documents": [
            "Aadhaar"
        ],
        "processing_time": "7 Days",
        "steps": [
            "Visit MeeSeva",
            "Submit Application"
        ]
    }
