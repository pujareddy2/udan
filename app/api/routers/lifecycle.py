from fastapi import APIRouter, Depends
from typing import List
from app.api.schemas.common import MissedOpportunitySchema, TimelineEventSchema
from app.core.security import get_current_user

router = APIRouter(prefix="/lifecycle", tags=["Lifecycle & Recovery Engine"])

@router.get("/missed-opportunities", response_model=List[MissedOpportunitySchema])
def get_missed_opportunities(user_id: int = Depends(get_current_user)):
    """
    Returns opportunities the user permanently lost and the root cause for losing them.
    """
    return []

@router.get("/recovery-plan")
def get_recovery_plan(user_id: int = Depends(get_current_user)):
    """
    Returns the actionable playbook preventing the user from losing future opportunities.
    """
    return {"recovery_plan": "Upload your Income Certificate before March."}

@router.get("/timeline", response_model=List[TimelineEventSchema])
def get_timeline(user_id: int = Depends(get_current_user)):
    """
    Returns the chronological feed of the user's actions and unlocked values on Udaan AI.
    """
    return []
