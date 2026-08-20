from typing import Optional, List
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

class Opportunity(SQLModel, table=True):
    __tablename__ = "opportunities"
    __table_args__ = {'extend_existing': True}

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    module_type: str = Field(index=True, nullable=False)
    provider: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    
    # Deterministic Engine Rules mapped from CSV columns
    eligibility_rules: dict = Field(default={}, sa_column=Column(JSON, nullable=False))
    
    # Grouped fields
    benefits: dict = Field(default={}, sa_column=Column(JSON))
    metadata_info: dict = Field(default={}, sa_column=Column(JSON))
    required_documents: list = Field(default=[], sa_column=Column(JSON))
    
    url: Optional[str] = Field(default=None)
    deadline: Optional[date] = Field(default=None, index=True)
    priority_score: Optional[int] = Field(default=0, index=True)
    is_active: bool = Field(default=True)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    wallet_entries: List["OpportunityWallet"] = Relationship(
        back_populates="opportunity",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
