from fastapi import APIRouter, Depends
from typing import List
from app.api.schemas.common import OpportunityListSchema, OpportunityDetailSchema
from app.core.security import get_current_user

router = APIRouter(prefix="/opportunities", tags=["Opportunity Engine"])

@router.get("/eligible", response_model=List[OpportunityListSchema])
def get_eligible_opportunities(user_id: int = Depends(get_current_user)):
    """
    Returns all opportunities the user is strictly eligible for based on their demographic profile.
    """
    return []

@router.get("/recommended", response_model=List[OpportunityListSchema])
def get_recommended_opportunities(user_id: int = Depends(get_current_user)):
    """
    Returns opportunities the user is not yet eligible for, but could unlock if they acquire missing documents.
    """
    return []

@router.get("/{opportunity_id}", response_model=OpportunityDetailSchema)
def get_opportunity_details(opportunity_id: int, user_id: int = Depends(get_current_user)):
    """
    Returns the deep-dive details, rules, and required documents for a specific opportunity.
    """
    return {
        "id": opportunity_id,
        "title": "Mock Scheme",
        "benefit_value": 0.0,
        "tags": [],
        "description": "Details",
        "eligibility_rules": {},
        "required_documents": [],
        "followup_questions": []
    }
