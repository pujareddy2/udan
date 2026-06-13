from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.core.db import get_session
from app.models.domain import FarmerProfile, UserProfile, Opportunity, Document
from app.services.eligibility import EligibilityEngine
from pydantic import BaseModel
import json

router = APIRouter()

class ScamScanRequest(BaseModel):
    text: str

@router.post("/scam/scan", tags=["Intelligence"])
def scan_job_post(req: ScamScanRequest):
    text_lower = req.text.lower()
    
    # Rules to flag a scam
    suspect_signatures = []
    
    if "deposit" in text_lower or "refundable" in text_lower or "security charge" in text_lower or "laptop dispatch" in text_lower:
        suspect_signatures.append("Mandatory refundable security deposit or fee requests")
    if "whatsapp" in text_lower or "telegram" in text_lower:
        suspect_signatures.append("Redirection to unofficial chat groups (WhatsApp/Telegram)")
    if "earn" in text_lower and ("daily" in text_lower or "work from home" in text_lower or "working from home" in text_lower):
        suspect_signatures.append("Suspicious work-from-home high earning claims")
        
    if suspect_signatures:
        return {
            "status": "flagged",
            "risk_level": "High",
            "reason": "Suspect signatures: " + ", ".join(suspect_signatures) + ".",
            "signatures": suspect_signatures
        }
    return {
        "status": "safe",
        "risk_level": "Low",
        "reason": "Shield Idle. No known scam signatures detected in the text.",
        "signatures": []
    }

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
    engine = EligibilityEngine()
    
    if user_id:
        user_profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
        farmer_profile = session.exec(select(FarmerProfile).where(FarmerProfile.user_id == user_id)).first()
        user_docs_records = session.exec(select(Document).where(Document.user_id == user_id)).all()
        user_docs = [d.document_master.document_name for d in user_docs_records if d.document_master and d.status == "Verified"] if user_docs_records else []
        
        if user_profile and farmer_profile:
            # Build user dict
            user_dict = {
                "id": user_id,
                "income": farmer_profile.annual_income,
                "age": user_profile.age,
                "category": user_profile.category,
                "state": user_profile.state,
                "land_area": farmer_profile.land_size_acres,
                "gender": user_profile.gender
            }
            
            # Get farmer opportunities
            opps = session.exec(select(Opportunity).where(Opportunity.module == "farmer")).all()
            for opp in opps:
                rules = opp.eligibility_rules if isinstance(opp.eligibility_rules, dict) else (json.loads(opp.eligibility_rules) if opp.eligibility_rules else {})
                docs = opp.required_documents if isinstance(opp.required_documents, list) else (json.loads(opp.required_documents) if opp.required_documents else [])
                
                opp_dict = {
                    "id": opp.id,
                    "title": opp.title,
                    "eligibility_rules": rules,
                    "required_documents": docs
                }
                
                verdict = engine.evaluate_single_eligibility(user_dict, user_docs, opp_dict)
                
                if verdict.verdict in ["Eligible", "Potentially Eligible", "Needs Clarification"]:
                    recs.append({
                        "id": opp.id,
                        "scheme": opp.title,
                        "benefit": f"₹{opp.benefit_value:,.0f}",
                        "confidence": int(verdict.eligibility_score),
                        "reason": verdict.eligibility_explanation,
                        "missing_docs": verdict.missing_documents,
                        "status": verdict.verdict,
                        "description": opp.description,
                        "benefit_summary": opp.benefit_summary,
                        "apply_link": opp.apply_link,
                        "opportunity_type": opp.opportunity_type
                    })
            
    # Remove hardcoded fallback to enforce dynamic rules
    if not recs:
        # Just return empty if no real opportunities match
        pass
        
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
