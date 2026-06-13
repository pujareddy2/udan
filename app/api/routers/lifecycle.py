from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.core.db import get_session
from app.models.domain import MissedOpportunity, Opportunity

router = APIRouter()

@router.get("/lifecycle/missed-opportunities", tags=["Lifecycle"])
def get_missed_opportunities(user_id: int = 5, session: Session = Depends(get_session)):
    mo = session.exec(select(MissedOpportunity).where(MissedOpportunity.user_id == user_id)).first()
    if mo:
        opp = session.exec(select(Opportunity).where(Opportunity.id == mo.opportunity_id)).first()
        opp_name = opp.title if opp else "National Merit Scholarship"
        return {
            "opportunity_name": opp_name,
            "value_lost": mo.missed_value,
            "reason": mo.root_cause,
            "recovery_action": "Generate Income Certificate"
        }
    return {
        "opportunity_name": "National Merit Scholarship",
        "value_lost": 12000,
        "reason": "Missing Income Certificate",
        "recovery_action": "Generate Income Certificate"
    }

@router.get("/lifecycle/recovery-plan", tags=["Lifecycle"])
def get_recovery_plan():
    """Get actionable recovery playbook."""
    return {
        "recovery_plan": "Upload your Income Certificate before March 31 to stay eligible for PM-KISAN and NSP. Visit Block Development Office.",
        "action_items": [
            {"doc": "Income Certificate", "deadline": "2025-03-31", "issuer": "Tehsildar Office"},
            {"doc": "Aadhaar Update (Mobile Link)", "deadline": "2025-04-15", "issuer": "UIDAI Centre"}
        ]
    }

@router.get("/lifecycle/timeline", tags=["Lifecycle"])
def get_timeline():
    """Get full chronological activity timeline."""
    return [
        {
            "event_type": "APPLIED",
            "title": "Applied for NSP Central Sector Scholarship",
            "impact_value": 12000.0,
            "date": "2025-01-10"
        }
    ]

@router.get("/timeline", tags=["Timeline"])
def get_general_timeline():
    """Get full chronological activity timeline."""
    return [
        {
            "event_type": "APPLIED",
            "title": "Applied for NSP Central Sector Scholarship",
            "impact_value": 12000.0,
            "date": "2025-01-10"
        }
    ]

@router.get("/timeline/milestones", tags=["Timeline"])
def get_timeline_milestones():
    """Get major user milestones."""
    return [
        {
            "title": "Profile Completed",
            "date": "2024-12-01"
        }
    ]

@router.get("/timeline/achievements", tags=["Timeline"])
def get_timeline_achievements():
    """Get user achievements."""
    return [
        {
            "title": "First Scheme Unlocked",
            "date": "2025-01-15"
        }
    ]
