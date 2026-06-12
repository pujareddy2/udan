from sqlmodel import SQLModel, Field, Column
from sqlalchemy.types import JSON
from typing import Optional, List, Dict, Any
from datetime import datetime

class Notification(SQLModel, table=True):
    __tablename__ = "notifications"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    opportunity_id: Optional[str] = Field(default=None, index=True)
    
    type: str = Field(index=True) # DEADLINE_ALERT, VALUE_UNLOCK, etc.
    priority: str = Field(default="P3") # P0, P1, P2, P3
    
    title: str
    message: str
    
    value_impact: float = Field(default=0.0)
    action_text: str
    action_link: Optional[str] = None
    
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationBehavior(SQLModel, table=True):
    __tablename__ = "notification_behavior"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, unique=True)
    
    opened_count: int = Field(default=0)
    ignored_count: int = Field(default=0)
    action_completion_rate: float = Field(default=0.0)
    
    daily_p0_count: int = Field(default=0)
    daily_p1_count: int = Field(default=0)
    last_notified_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationDigest(SQLModel, table=True):
    __tablename__ = "notification_digests"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    digest_type: str = Field(default="Evening") # Morning, Evening, Weekly
    content_summary: str
    is_read: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
