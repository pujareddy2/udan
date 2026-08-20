from typing import Optional, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    is_active: bool = Field(default=True)
    last_login: Optional[datetime] = Field(default=None)
    module_type: Optional[str] = Field(default=None, index=True)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    profile: Optional["UserProfile"] = Relationship(back_populates="user")
    wallet_entries: list["OpportunityWallet"] = Relationship(back_populates="user")
    documents: list["Document"] = Relationship(back_populates="user")
    notifications: list["Notification"] = Relationship(back_populates="user")

class UserProfile(SQLModel, table=True):
    __tablename__ = "user_profiles"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True, index=True)
    
    full_name: str
    mobile_number: str = Field(index=True)
    age: int
    gender: str
    state: str = Field(index=True)
    district: str
    category: str
    preferred_language: str = Field(default="en")
    
    # Store all the dynamic data (land size, business stage, etc) based on the module
    profile_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="profile")
