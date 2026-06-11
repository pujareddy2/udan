from typing import Optional
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

class Document(SQLModel, table=True):
    __tablename__ = "documents"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)
    document_type: str = Field(nullable=False)
    
    file_path: Optional[str] = Field(default=None)
    extracted_data: dict = Field(default={}, sa_column=Column(JSON))
    is_verified: bool = Field(default=False)
    
    issue_date: Optional[date] = Field(default=None)
    expiry_date: Optional[date] = Field(default=None, index=True)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional["User"] = Relationship(back_populates="documents")
