from sqlmodel import SQLModel, Field, Column
from sqlalchemy.types import JSON
from typing import Optional, List, Dict, Any
from datetime import datetime

class ApplicationCoaching(SQLModel, table=True):
    __tablename__ = "application_coaching"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    opportunity_id: str = Field(index=True)
    
    why_it_matters: str
    motivation_message: str
    approval_probability: float = Field(default=0.0)
    difficulty_level: str = Field(default="Medium")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ApplicationRiskAnalysis(SQLModel, table=True):
    __tablename__ = "application_risk_analysis"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    opportunity_id: str = Field(index=True)
    
    risk_level: str = Field(default="Low")
    urgency_level: str = Field(default="Low")
    risk_factors: List[str] = Field(default_factory=list, sa_column=Column(JSON))

class ApplicationStrategy(SQLModel, table=True):
    __tablename__ = "application_strategy"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    opportunity_id: str = Field(index=True)
    
    priority_rank: str = Field(default="Apply Later") # Apply First, Apply Later, Prepare First, Not Recommended

class ApplicationActionPlan(SQLModel, table=True):
    __tablename__ = "application_action_plans"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    opportunity_id: str = Field(index=True)
    
    next_best_action: str
    success_steps: List[str] = Field(default_factory=list, sa_column=Column(JSON))
