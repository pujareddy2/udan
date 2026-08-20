from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy.types import JSON
from typing import Optional, List, Dict, Any
from datetime import datetime

class DocumentRecoveryGuide(SQLModel, table=True):
    __tablename__ = "document_recovery_guides"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    document_name: str = Field(index=True, unique=True)
    national_description: str
    difficulty_level: str = Field(default="Medium")
    min_days: int = Field(default=7)
    max_days: int = Field(default=14)
    
    document_id: Optional[int] = Field(default=None, foreign_key="document_master.id", index=True)
    document_master: Optional["DocumentMaster"] = Relationship(back_populates="recovery_guides")

class DocumentStateProcess(SQLModel, table=True):
    __tablename__ = "document_state_processes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    document_name: str = Field(index=True)
    state_name: str = Field(index=True)
    apply_link: str
    authority_name: str
    fees: float = Field(default=0.0)
    process_steps: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    supporting_documents: List[str] = Field(default_factory=list, sa_column=Column(JSON))

class DocumentSubstitute(SQLModel, table=True):
    __tablename__ = "document_substitutes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    target_document: str = Field(index=True)
    accepted_substitute: str = Field(index=True)

class UserRecoveryHistory(SQLModel, table=True):
    __tablename__ = "user_recovery_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    document_name: str = Field(index=True)
    status: str = Field(default="Started") # Started, Pending, Completed
    started_at: datetime = Field(default_factory=datetime.utcnow)
