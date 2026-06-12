from sqlmodel import SQLModel, Field, Column
from sqlalchemy.types import JSON
from typing import Optional, List, Dict, Any
from datetime import datetime

class ProfileContext(SQLModel, table=True):
    __tablename__ = "profile_context"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True, index=True)
    
    # Core Outputs
    personas: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    primary_intents: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    priority_categories: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Generated Search Payloads
    search_keywords: Dict[str, List[str]] = Field(default_factory=dict, sa_column=Column(JSON))
    context_scores: Dict[str, float] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Recalculation Tracking
    profile_hash: str = Field(index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ContextHistory(SQLModel, table=True):
    __tablename__ = "context_history"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    previous_personas: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    archived_at: datetime = Field(default_factory=datetime.utcnow)
