from sqlmodel import SQLModel, Field, Column
from sqlalchemy.types import JSON
from typing import Optional, List, Dict, Any
from datetime import datetime

class OpportunityTrustScore(SQLModel, table=True):
    __tablename__ = "opportunity_trust_scores"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    opportunity_id: str = Field(index=True, unique=True)
    url: str
    
    trust_score: float = Field(default=0.0)
    trust_level: str
    source_type: str
    verified: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ApprovalPrediction(SQLModel, table=True):
    __tablename__ = "approval_predictions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    opportunity_id: str = Field(index=True)
    
    approval_probability: float = Field(default=0.0)
    level: str
    
    missing_items: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    improvement_actions: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    current_prob_sim: float = Field(default=0.0)
    potential_prob_sim: float = Field(default=0.0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OpportunityHealthScore(SQLModel, table=True):
    __tablename__ = "opportunity_health_scores"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    opportunity_id: str = Field(index=True)
    
    health_score: float = Field(default=0.0)
    status: str
    next_action: str
    potential_value: float = Field(default=0.0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
