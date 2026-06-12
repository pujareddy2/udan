from sqlmodel import SQLModel, Field, Column
from sqlalchemy.types import JSON
from typing import Optional, List, Dict, Any
from datetime import datetime

class TimelineEvent(SQLModel, table=True):
    __tablename__ = "timeline_events"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    opportunity_id: Optional[str] = Field(default=None, index=True)
    
    category: str = Field(index=True) # PROFILE, DISCOVERY, ELIGIBILITY, DOCUMENT, APPLICATION, etc.
    sub_type: str = Field(index=True)
    importance: str = Field(default="Low") # Critical, High, Medium, Low
    
    story_text: str
    
    value_gained: float = Field(default=0.0)
    readiness_gain: float = Field(default=0.0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TimelineMilestone(SQLModel, table=True):
    __tablename__ = "timeline_milestones"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    title: str
    description: str
    unlocked_at: datetime = Field(default_factory=datetime.utcnow)

class TimelineAchievement(SQLModel, table=True):
    __tablename__ = "timeline_achievements"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    title: str
    description: str
    unlocked_at: datetime = Field(default_factory=datetime.utcnow)

class TimelinePrediction(SQLModel, table=True):
    __tablename__ = "timeline_predictions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    opportunity_id: Optional[str] = Field(default=None, index=True)
    
    expected_event_name: str
    expected_date: datetime

class TimelineAnalytics(SQLModel, table=True):
    __tablename__ = "timeline_analytics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, unique=True)
    
    total_value_earned: float = Field(default=0.0)
    total_opportunities_found: int = Field(default=0)
    total_applications_submitted: int = Field(default=0)
    total_approvals: int = Field(default=0)
    total_recoveries: int = Field(default=0)
    
    last_updated: datetime = Field(default_factory=datetime.utcnow)
