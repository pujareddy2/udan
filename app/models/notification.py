from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)
    
    type: str = Field(nullable=False) # 'new_opportunity', 'deadline_reminder', 'document_expiry'
    title: str = Field(nullable=False)
    message: str = Field(nullable=False)
    
    related_entity_type: Optional[str] = Field(default=None)
    related_entity_id: Optional[int] = Field(default=None)
    
    is_read: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional["User"] = Relationship(back_populates="notifications")
