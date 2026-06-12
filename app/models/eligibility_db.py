from sqlmodel import SQLModel, Field, Column
from sqlalchemy.types import JSON
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserOpportunityEligibility(SQLModel, table=True):
    __tablename__ = "user_opportunity_eligibility"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    opportunity_id: int = Field(foreign_key="opportunities.id", index=True)
    
    eligibility_score: float = Field(default=0.0, index=True)
    verdict: str = Field(index=True) # Eligible, Potentially Eligible, Needs Clarification, Not Eligible
    confidence: float = Field(default=0.0)
    
    missing_requirements: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    missing_documents: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    followup_questions: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    eligibility_explanation: str = Field(default="")
    
    calculated_at: datetime = Field(default_factory=datetime.utcnow, index=True)
