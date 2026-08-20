from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON, UniqueConstraint

class OpportunityWallet(SQLModel, table=True):
    __tablename__ = "opportunity_wallet"
    __table_args__ = (UniqueConstraint('user_id', 'opportunity_id', name='_user_opp_uc'), {'extend_existing': True})

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)
    opportunity_id: int = Field(foreign_key="opportunities.id", index=True, nullable=False)
    
    status: str = Field(nullable=False) # 'saved', 'applied'
    
    # Store answers to dynamic follow up questions asked specifically for this opportunity
    dynamic_answers: dict = Field(default={}, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional["User"] = Relationship(back_populates="wallet_entries")
    opportunity: Optional["Opportunity"] = Relationship(back_populates="wallet_entries")
