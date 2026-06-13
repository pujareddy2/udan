from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.db import get_session
from app.models.domain import User, UserProfile, Opportunity, Document, DocumentMaster, Application, MissedOpportunity
from app.models.timeline_db import TimelineEvent
from app.models.wallet_db import OpportunityWallet
from typing import Dict, List, Any
from datetime import datetime

router = APIRouter()

@router.get("/jobseeker/roadmap", tags=["Job Seeker"])
def get_jobseeker_roadmap(user_id: int = 5, session: Session = Depends(get_session)):
    # Find user profile
    user_profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    if not user_profile:
        return {"steps": [{"title": "Complete your Profile", "impact": "Unlock matched job roles"}]}
        
    # Get user documents status
    user_docs = session.exec(select(Document).where(Document.user_id == user_id)).all()
    verified_docs = {d.document_master.document_name for d in user_docs if d.status == "Verified" and d.document_master}
    
    # Check if Caste Certificate (OBC) is verified
    has_caste = "Caste Certificate (OBC)" in verified_docs

    # Check if Java Programming skill is present in JobSeekerProfile
    from app.models.domain import JobSeekerProfile
    js_profile = session.exec(select(JobSeekerProfile).where(JobSeekerProfile.user_id == user_id)).first()
    has_java = False
    if js_profile:
        skills = js_profile.skills or []
        if "Java Programming" in skills:
            has_java = True

    # Check if they have applied for SSC CGL 2026
    from app.models.domain import Application, Opportunity
    cgl_app = session.exec(
        select(Application)
        .join(Opportunity)
        .where(Application.user_id == user_id)
        .where(Opportunity.title == "SSC CGL 2026")
    ).first()
    has_applied_cgl = cgl_app is not None

    steps = [
        {
            "title": "Complete profile registration (100%)",
            "checked": True,
            "description": "Profile fully updated with verification data."
        },
        {
            "title": "Obtain Caste Certificate",
            "checked": has_caste,
            "description": "Blocks RRB NTPC opportunity. Visit Tehsildar Office."
        },
        {
            "title": "Complete Java Skill Fix Course",
            "checked": has_java,
            "description": "Unlocks PMKVY Java Developer stipend value."
        },
        {
            "title": "Apply for SSC CGL 2026",
            "checked": has_applied_cgl,
            "description": "Registration closes 20 Jul 2026."
        }
    ]
    return {"steps": steps}

@router.get("/jobseeker/applications", tags=["Job Seeker"])
def get_jobseeker_applications(user_id: int = 5, session: Session = Depends(get_session)):
    apps = session.exec(select(Application).where(Application.user_id == user_id)).all()
    res = []
    for a in apps:
        opp = a.opportunity
        res.append({
            "id": a.id,
            "opportunity_name": opp.title if opp else "Unknown Opportunity",
            "status": a.current_status,
            "last_updated": a.last_updated.strftime('%Y-%m-%d')
        })
    return res

@router.get("/jobseeker/deadlines", tags=["Job Seeker"])
def get_jobseeker_deadlines(user_id: int = 5, session: Session = Depends(get_session)):
    opps = session.exec(select(Opportunity).where(Opportunity.module == "jobseeker")).all()
    res = []
    now = datetime.now()
    for opp in opps:
        for deadline in opp.deadlines:
            delta = deadline.deadline_date - now
            days_remaining = max(0, delta.days)
            res.append({
                "scheme": opp.title,
                "days_remaining": days_remaining,
                "deadline_date": deadline.deadline_date.strftime('%Y-%m-%d')
            })
            
    # Sort by nearest deadline
    res = sorted(res, key=lambda x: x["days_remaining"])
    return {"deadlines": res}

@router.get("/jobseeker/opportunity-summary", tags=["Job Seeker"])
def get_jobseeker_opportunity_summary(user_id: int = 5, session: Session = Depends(get_session)):
    # Opportunity Wallet counts
    apps = session.exec(select(Application).where(Application.user_id == user_id)).all()
    status_counts = {
        "Ready": 0,
        "Blocked": 0,
        "Applied": 0,
        "Under Review": 0,
        "Recovered": 0,
        "Missed": 0
    }
    
    # Map database application states
    for a in apps:
        if a.current_status == "Applied":
            status_counts["Applied"] += 1
        elif a.current_status == "Under Review":
            status_counts["Under Review"] += 1
            
    # Query missed opportunities
    missed_count = len(session.exec(select(MissedOpportunity).where(MissedOpportunity.user_id == user_id)).all())
    status_counts["Missed"] = missed_count
    
    # Remaining are Ready/Blocked based on docs
    user_docs = session.exec(select(Document).where(Document.user_id == user_id)).all()
    verified_docs = {d.document_master.document_name for d in user_docs if d.status == "Verified" and d.document_master}
    
    opps = session.exec(select(Opportunity).where(Opportunity.module == "jobseeker")).all()
    
    # Exclude those already applied or under review
    applied_opp_ids = {a.opportunity_id for a in apps}
    
    for opp in opps:
        if opp.id in applied_opp_ids:
            continue
        # Check if they have all docs verified
        blocked = False
        for rd in opp.required_documents or []:
            if rd not in verified_docs:
                blocked = True
                break
        if blocked:
            status_counts["Blocked"] += 1
        else:
            status_counts["Ready"] += 1
            
    return status_counts

@router.get("/jobseeker/value-summary", tags=["Job Seeker"])
def get_jobseeker_value_summary(user_id: int = 5, session: Session = Depends(get_session)):
    # Compute eligible, potential, blocked, and recovery value
    opps = session.exec(select(Opportunity).where(Opportunity.module == "jobseeker")).all()
    user_docs = session.exec(select(Document).where(Document.user_id == user_id)).all()
    verified_docs = {d.document_master.document_name for d in user_docs if d.status == "Verified" and d.document_master}
    
    eligible = 0.0
    potential = 0.0
    blocked = 0.0
    recovery = 0.0
    
    for opp in opps:
        val = opp.benefit_value or 0.0
        potential += val
        
        # Check eligibility requirements
        is_blocked = False
        for rd in opp.required_documents or []:
            if rd not in verified_docs:
                is_blocked = True
                break
                
        if is_blocked:
            blocked += val
            # If the missing document can be recovered (e.g. Income Certificate)
            recovery += val
        else:
            eligible += val
            
    return {
        "eligible_value": eligible,
        "potential_value": potential,
        "blocked_value": blocked,
        "recovery_value": recovery
    }

@router.get("/jobseeker/document-summary", tags=["Job Seeker"])
def get_jobseeker_document_summary(user_id: int = 5, session: Session = Depends(get_session)):
    user_docs = session.exec(select(Document).where(Document.user_id == user_id)).all()
    
    verified = []
    missing = []
    expiring = []
    
    all_masters = session.exec(select(DocumentMaster)).all()
    uploaded_master_names = {d.document_master.document_name for d in user_docs if d.document_master}
    
    for d in user_docs:
        name = d.document_master.document_name if d.document_master else "Document"
        if d.status == "Verified":
            verified.append(name)
        elif d.status == "Expired":
            expiring.append(name)
            
    for m in all_masters:
        if m.document_name not in uploaded_master_names:
            missing.append(m.document_name)
            
    return {
        "verified": verified,
        "missing": missing,
        "expiring": expiring,
        "recoverable": ["Income Certificate"] if "Income Certificate" in missing else []
    }

from pydantic import BaseModel

class AddSkillRequest(BaseModel):
    user_id: int = 5
    skill: str

@router.post("/jobseeker/add-skill", tags=["Job Seeker"])
def add_jobseeker_skill(req: AddSkillRequest, session: Session = Depends(get_session)):
    from app.models.domain import JobSeekerProfile
    js_profile = session.exec(select(JobSeekerProfile).where(JobSeekerProfile.user_id == req.user_id)).first()
    if not js_profile:
        raise HTTPException(status_code=404, detail="Jobseeker profile not found")
    
    current_skills = list(js_profile.skills or [])
    if req.skill not in current_skills:
        current_skills.append(req.skill)
        js_profile.skills = current_skills
        session.add(js_profile)
        session.commit()
        session.refresh(js_profile)
    return {"success": True, "skills": js_profile.skills}

class ApplyRequest(BaseModel):
    user_id: int
    opportunity_id: int

@router.post("/jobseeker/apply", tags=["Job Seeker"])
def apply_opportunity(req: ApplyRequest, session: Session = Depends(get_session)):
    from app.models.domain import Application, Opportunity
    opp = session.get(Opportunity, req.opportunity_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    app_record = session.exec(
        select(Application)
        .where(Application.user_id == req.user_id)
        .where(Application.opportunity_id == req.opportunity_id)
    ).first()
    
    if not app_record:
        app_record = Application(
            user_id=req.user_id,
            opportunity_id=req.opportunity_id,
            current_status="Applied",
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
        session.add(app_record)
        session.commit()
        session.refresh(app_record)
    else:
        app_record.current_status = "Applied"
        app_record.last_updated = datetime.utcnow()
        session.add(app_record)
        session.commit()
        
    return {"success": True, "status": app_record.current_status}
