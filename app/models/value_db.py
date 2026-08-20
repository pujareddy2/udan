from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class UserValueSummary(SQLModel, table=True):
    __tablename__ = "user_value_summary"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, unique=True)
    
    eligible_value: float = Field(default=0.0)
    potential_value: float = Field(default=0.0)
    protected_value: float = Field(default=0.0)
    missed_value: float = Field(default=0.0)
    recovery_value: float = Field(default=0.0)
    
    lifetime_value_estimate: float = Field(default=0.0)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)

class OpportunityValueScore(SQLModel, table=True):
    __tablename__ = "opportunity_value_scores"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    opportunity_id: str = Field(index=True, unique=True) # Linking to main opportunity DB
    
    financial_value: float = Field(default=0.0)
    career_value: float = Field(default=0.0)
    training_value: float = Field(default=0.0)
    protection_value: float = Field(default=0.0)
    future_value: float = Field(default=0.0)

class DocumentValueImpact(SQLModel, table=True):
    __tablename__ = "document_value_impact"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    document_name: str = Field(index=True)
    
    blocked_value: float = Field(default=0.0)
    opportunities_blocked_count: int = Field(default=0)
    
    calculated_at: datetime = Field(default_factory=datetime.utcnow)

class ValueForecast(SQLModel, table=True):
    __tablename__ = "value_forecasts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    forecast_30_days: float = Field(default=0.0)
    forecast_90_days: float = Field(default=0.0)
    forecast_180_days: float = Field(default=0.0)
    
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
