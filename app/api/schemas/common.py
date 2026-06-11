from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role_claims: List[str]

class ErrorResponse(BaseModel):
    error_code: str
    message: str
    actionable_steps: Optional[List[str]] = None

class OpportunityListSchema(BaseModel):
    id: int
    title: str
    benefit_value: float
    deadline: Optional[str] = None
    tags: List[str]

class OpportunityDetailSchema(OpportunityListSchema):
    description: str
    eligibility_rules: Dict[str, Any]
    required_documents: List[str]
    followup_questions: List[str]

class WalletDashboardResponse(BaseModel):
    wallet_status: str
    total_value_unlocked: float
    eligible_and_ready: List[OpportunityListSchema]
    blocked_by_documents: List[OpportunityListSchema]
    expiring_soon: List[OpportunityListSchema]
    under_review: List[OpportunityListSchema]

class DocumentDashboardResponse(BaseModel):
    wallet_status: str
    verified_documents: List[str]
    missing_documents: List[str]
    expiring_documents: List[str]

class MissedOpportunitySchema(BaseModel):
    opportunity_id: int
    title: str
    missed_value: float
    root_cause: str
    missed_date: str

class TimelineEventSchema(BaseModel):
    event_type: str
    title: str
    impact_value: float
    date: str
