from fastapi import APIRouter

router = APIRouter()

def _get_mock_opportunities(role: str):
    return {
        "success": True,
        "message": f"Opportunities summary for {role}",
        "total": 12,
        "eligible": 7,
        "potential": 3,
        "blocked": 2
    }

@router.get("/student/opportunities/summary", tags=["Opportunities"])
def get_student_opportunities():
    return _get_mock_opportunities("student")

@router.get("/farmer/opportunities/summary", tags=["Opportunities"])
def get_farmer_opportunities():
    return _get_mock_opportunities("farmer")

@router.get("/jobseeker/opportunities/summary", tags=["Opportunities"])
def get_jobseeker_opportunities():
    return _get_mock_opportunities("jobseeker")

@router.get("/entrepreneur/opportunities/summary", tags=["Opportunities"])
def get_entrepreneur_opportunities():
    return _get_mock_opportunities("entrepreneur")

@router.get("/women-entrepreneur/opportunities/summary", tags=["Opportunities"])
def get_women_entrepreneur_opportunities():
    return _get_mock_opportunities("women-entrepreneur")

@router.get("/startup/opportunities/summary", tags=["Opportunities"])
def get_startup_opportunities():
    return _get_mock_opportunities("startup")

@router.get("/senior-citizen/opportunities/summary", tags=["Opportunities"])
def get_senior_citizen_opportunities():
    return _get_mock_opportunities("senior-citizen")

@router.get("/opportunities/categories", tags=["Opportunities"])
def get_opportunity_categories(user_id: int = None):
    categories = [
        {"name": "Scholarships", "available": 1240, "matched": 14, "eligible": 8, "icon": "award", "note": "Merit & means-based"},
        {"name": "Internships", "available": 860, "matched": 12, "eligible": 6, "icon": "briefcase", "note": "Govt & corporate"},
        {"name": "Fellowships", "available": 95, "matched": 5, "eligible": 2, "icon": "star", "note": "Research & policy"},
        {"name": "Research Programs", "available": 310, "matched": 6, "eligible": 3, "icon": "flask", "note": "Funded projects"},
        {"name": "Hackathons", "available": 42, "matched": 4, "eligible": 2, "icon": "code", "note": "Build · win · get hired"},
        {"name": "Jobs", "available": 5600, "matched": 25, "eligible": 15, "icon": "building", "note": "Full-time & part-time careers"},
        {"name": "Competitions", "available": 150, "matched": 8, "eligible": 4, "icon": "trophy", "note": "National & global contests"},
        {"name": "Conferences", "available": 75, "matched": 5, "eligible": 3, "icon": "globe", "note": "Academic & tech summits"},
        {"name": "Training Programs", "available": 320, "matched": 18, "eligible": 10, "icon": "book", "note": "Skill certifications"}
    ]
    return {"categories": categories}


from sqlmodel import Session, select
from app.core.db import get_session
from app.models.domain import Opportunity, Document
from fastapi import Depends
from datetime import datetime

@router.get("/opportunities/recommended", tags=["Opportunities"])
def get_recommended_opportunities(user_id: int = 5, session: Session = Depends(get_session)):
    import json
    from app.models.domain import JobSeekerProfile, Opportunity, Document
    opps = session.exec(select(Opportunity).where(Opportunity.module == "jobseeker")).all()
    user_docs = session.exec(select(Document).where(Document.user_id == user_id)).all()
    verified_docs = {d.document_master.document_name for d in user_docs if d.status == "Verified" and d.document_master}
    
    # Get user skills from JobSeekerProfile
    js_profile = session.exec(select(JobSeekerProfile).where(JobSeekerProfile.user_id == user_id)).first()
    user_skills = set(js_profile.skills or []) if js_profile else set()
    
    res = []
    now = datetime.now()
    
    for opp in opps:
        # Exclude scholarship since it's in the missed opportunities section
        if "National Merit Scholarship" in opp.title:
            continue
            
        # Parse docs from DB
        req_docs = []
        if opp.required_documents:
            if isinstance(opp.required_documents, list):
                req_docs = opp.required_documents
            else:
                try:
                    req_docs = json.loads(opp.required_documents)
                except:
                    req_docs = []
                    
        # Parse skills from DB (stored in followup_questions)
        req_skills = []
        if opp.followup_questions:
            if isinstance(opp.followup_questions, list):
                req_skills = opp.followup_questions
            else:
                try:
                    req_skills = json.loads(opp.followup_questions)
                except:
                    req_skills = []
                    
        missing_docs = [d for d in req_docs if d not in verified_docs]
        missing_skills = [s for s in req_skills if s not in user_skills]
        
        blocked_reason = f"Missing {', '.join(missing_docs)}" if missing_docs else "None"
        
        # Calculate match score
        total_reqs = len(req_docs) + len(req_skills)
        if total_reqs > 0:
            met_reqs = (len(req_docs) - len(missing_docs)) + (len(req_skills) - len(missing_skills))
            match_score = int((met_reqs / total_reqs) * 100)
        else:
            match_score = 100
            
        trust_score = 100
        official_url = "gov.in"
        is_official_govt = True
        is_skilling = False
        
        if "SSC CGL" in opp.title:
            official_url = "ssc.gov.in"
            trust_score = 100
        elif "RRB NTPC" in opp.title:
            official_url = "rrbsecunderabad.nic.in"
            trust_score = 100
        elif "NATS" in opp.title:
            official_url = "nats.education.gov.in"
            trust_score = 98
        elif "PMKVY" in opp.title:
            official_url = "pmkvyofficial.org"
            trust_score = 90
            is_skilling = True
            
        deadline_str = "Open"
        days_remaining = 30
        if opp.deadlines:
            dl = opp.deadlines[0]
            deadline_str = dl.deadline_date.strftime('%Y-%m-%d')
            delta = dl.deadline_date - now
            days_remaining = max(0, delta.days)
            
        benefit_str = f"₹{opp.benefit_value:,.0f} / mo"
        if "NATS" in opp.title:
            benefit_str = "₹12,000 / month"
        elif "PMKVY" in opp.title:
            benefit_str = "Free Course + ₹8,000 Stipend"
            
        res.append({
            "id": opp.id,
            "name": opp.title,
            "match_score": match_score,
            "trust_score": trust_score,
            "approval_probability": max(40, 100 - len(missing_docs) * 20 - len(missing_skills) * 15),
            "benefit": benefit_str,
            "deadline": deadline_str,
            "days_remaining": days_remaining,
            "blocked_reason": blocked_reason,
            "official_url": official_url,
            "is_official_govt": is_official_govt,
            "is_skilling": is_skilling,
            "missing_docs": missing_docs,
            "missing_skills": missing_skills,
            "ready_percentage": 100 if not missing_skills else 60,
            "apply_link": f"https://{official_url}"
        })
        
    return {"opportunities": res}

@router.get("/trust/{opportunity_id}", tags=["Trust Engine"])
def get_opportunity_trust(opportunity_id: int, session: Session = Depends(get_session)):
    opp = session.get(Opportunity, opportunity_id)
    if not opp:
        return {
            "trust_score": 100,
            "source_type": "Government",
            "verified": True
        }
    source_type = "Government" if opp.provider_type == "government" else "Private"
    return {
        "trust_score": 100 if source_type == "Government" else 85,
        "source_type": source_type,
        "verified": True
    }

