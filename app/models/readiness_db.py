from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class UserReadiness(SQLModel, table=True):
    __tablename__ = "user_readiness"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, unique=True)
    
    overall_readiness: float = Field(default=0.0, index=True)
    unlockable_opportunities: int = Field(default=0)
    potential_value: float = Field(default=0.0)
    
    calculated_at: datetime = Field(default_factory=datetime.utcnow)

class ReadinessBreakdown(SQLModel, table=True):
    __tablename__ = "readiness_breakdown"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, unique=True)
    
    profile_score: float = Field(default=0.0)
    document_score: float = Field(default=0.0)
    skill_score: float = Field(default=0.0)
    business_score: float = Field(default=0.0)
    application_score: float = Field(default=0.0)
    verification_score: float = Field(default=0.0)

class ReadinessRecommendation(SQLModel, table=True):
    __tablename__ = "readiness_recommendations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    missing_item_name: str = Field(index=True)
    action_type: str = Field(default="Upload") # Upload, Verify, Fill
    
    opportunities_blocked_count: int = Field(default=0)
    value_blocked_amount: float = Field(default=0.0)
    readiness_gain: float = Field(default=0.0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
