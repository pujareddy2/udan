from sqlmodel import SQLModel, Field, Column
from sqlalchemy.types import JSON
from typing import Optional, List, Dict, Any
from datetime import datetime

class MissedOpportunityAnalysis(SQLModel, table=True):
    __tablename__ = "missed_opportunity_analysis"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    opportunity_id: str = Field(index=True)
    
    primary_cause: str
    secondary_cause: Optional[str] = None
    
    value_lost: float = Field(default=0.0)
    future_value_protected: float = Field(default=0.0)
    future_opportunities_protected: int = Field(default=0)
    
    emotional_impact_message: str
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BehaviorAnalytics(SQLModel, table=True):
    __tablename__ = "behavior_analytics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, unique=True)
    
    missed_count: int = Field(default=0)
    chronic_delay_score: float = Field(default=0.0)
    behavior_risk_score: str = Field(default="Low") # Low, Medium, High
    
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class UserRecoveryAction(SQLModel, table=True):
    __tablename__ = "user_recovery_actions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    opportunity_id: str = Field(index=True)
    
    priority_level: str = Field(default="Optional") # Do First, Do Next, Optional
    action_type: str
    success_probability: float = Field(default=0.0)
    roadmap_steps: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
