from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy.types import JSON
from typing import Optional, List, Dict, Any
from datetime import datetime

class OpportunityAlias(SQLModel, table=True):
    __tablename__ = "opportunity_aliases"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    opportunity_id: int = Field(foreign_key="opportunities.id", index=True)
    alias_name: str = Field(index=True)
    language: str = Field(default="en")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OpportunityVersion(SQLModel, table=True):
    __tablename__ = "opportunity_versions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    opportunity_id: int = Field(foreign_key="opportunities.id", index=True)
    version_number: int = Field(default=1, index=True)
    
    snapshot_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OpportunityChangeLog(SQLModel, table=True):
    __tablename__ = "opportunity_change_log"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    opportunity_id: int = Field(foreign_key="opportunities.id", index=True)
    
    field_changed: str = Field(index=True)
    old_value: Optional[str] = Field(default=None)
    new_value: Optional[str] = Field(default=None)
    
    source_id: Optional[int] = Field(default=None, foreign_key="opportunity_sources.id")
    
    changed_at: datetime = Field(default_factory=datetime.utcnow)

class OpportunitySourceMap(SQLModel, table=True):
    __tablename__ = "opportunity_source_map"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    opportunity_id: int = Field(foreign_key="opportunities.id", index=True)
    source_id: int = Field(foreign_key="opportunity_sources.id", index=True)
    
    discovery_date: datetime = Field(default_factory=datetime.utcnow)
