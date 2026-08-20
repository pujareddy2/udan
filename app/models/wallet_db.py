from sqlmodel import SQLModel, Field, Column
from sqlalchemy.types import JSON
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class OpportunityWallet(SQLModel, table=True):
    __tablename__ = "opportunity_wallet"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    opportunity_id: str = Field(index=True)
    
    bucket_status: str = Field(default="Needs Clarification", index=True) # Ready, Blocked, Needs Clarification, Applied, Under Review, Missed, Recovered
    health_score: float = Field(default=0.0)
    
    last_status_change: datetime = Field(default_factory=datetime.utcnow)

class WalletSnapshot(SQLModel, table=True):
    __tablename__ = "wallet_snapshots"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    snapshot_date: date = Field(default_factory=date.today)
    
    ready_count: int = Field(default=0)
    ready_value: float = Field(default=0.0)
    
    blocked_count: int = Field(default=0)
    blocked_value: float = Field(default=0.0)
    
    missed_value: float = Field(default=0.0)
    recovered_value: float = Field(default=0.0)

class WalletInsight(SQLModel, table=True):
    __tablename__ = "wallet_insights"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    insight_text: str
    insight_type: str = Field(default="Info") # Warning, Motivation, Value Unlock
    is_active: bool = Field(default=True)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
