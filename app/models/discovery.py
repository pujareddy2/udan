from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy.types import JSON
from typing import Optional, List, Dict, Any
from datetime import datetime

# ==========================================
# PART 1: OPPORTUNITY SOURCES
# ==========================================
class OpportunitySource(SQLModel, table=True):
    __tablename__ = "opportunity_sources"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    source_url: str = Field(unique=True, index=True)
    domain: str = Field(index=True)
    source_type: str = Field(default="Scraper") # Scraper, API, Manual
    is_official: bool = Field(default=False, index=True)
    
    trust_score: float = Field(default=0.5) # 0.0 to 1.0
    last_crawled: Optional[datetime] = Field(default=None)
    crawl_frequency: str = Field(default="daily") # daily, weekly, hourly
    status: str = Field(default="Active", index=True) # Active, Blocked
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    discovered_opportunities: List["DiscoveredOpportunity"] = Relationship(back_populates="source")

# ==========================================
# PART 2: DISCOVERED OPPORTUNITIES
# ==========================================
class DiscoveredOpportunity(SQLModel, table=True):
    __tablename__ = "discovered_opportunities"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    module_type: str = Field(index=True) # e.g., "Student", "Farmer"
    description: str
    opportunity_type: str = Field(index=True) # e.g., "Scholarship", "Subsidy"
    
    source_id: int = Field(foreign_key="opportunity_sources.id", index=True)
    source_url: str = Field(index=True)
    official_url: Optional[str] = Field(default=None)
    provider_name: str = Field(index=True)
    
    benefit_value: float = Field(default=0.0)
    deadline: Optional[datetime] = Field(default=None, index=True)
    
    # JSON Fields for flexibility before normalization
    eligibility_summary: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    required_documents: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    required_skills: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    application_link: Optional[str] = Field(default=None)
    state: str = Field(default="Central", index=True)
    district: Optional[str] = Field(default=None, index=True)
    
    status: str = Field(default="Raw", index=True) # Raw, Validated, Rejected, Processed
    discovery_confidence: float = Field(default=0.0)
    validation_confidence: float = Field(default=0.0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    source: Optional[OpportunitySource] = Relationship(back_populates="discovered_opportunities")
    validations: List["OpportunityValidation"] = Relationship(back_populates="discovered_opportunity")
    scores: List["OpportunityScore"] = Relationship(back_populates="discovered_opportunity")

# ==========================================
# PART 3: OPPORTUNITY VALIDATION & SCORES
# ==========================================
class OpportunityValidation(SQLModel, table=True):
    __tablename__ = "opportunity_validation"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    opportunity_id: int = Field(foreign_key="discovered_opportunities.id", index=True)
    
    source_validation_score: float = Field(default=0.0)
    deadline_validation_score: float = Field(default=0.0)
    eligibility_validation_score: float = Field(default=0.0)
    benefit_validation_score: float = Field(default=0.0)
    duplicate_validation_score: float = Field(default=0.0)
    document_score: float = Field(default=0.0)
    completeness_score: float = Field(default=0.0)
    consistency_score: float = Field(default=0.0)
    trust_score: float = Field(default=0.0)
    quality_score: float = Field(default=0.0)
    validation_confidence: float = Field(default=0.0)
    
    overall_validation_score: float = Field(default=0.0, index=True)
    
    validation_status: str = Field(default="Pending", index=True) # Pending, Passed, Failed
    validation_reason: Optional[str] = Field(default=None)
    
    validated_at: Optional[datetime] = Field(default=None)

    discovered_opportunity: Optional[DiscoveredOpportunity] = Relationship(back_populates="validations")

class OpportunityScore(SQLModel, table=True):
    __tablename__ = "opportunity_scores"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    opportunity_id: int = Field(foreign_key="discovered_opportunities.id", index=True)
    
    relevance_score: float = Field(default=0.0)
    value_score: float = Field(default=0.0)
    urgency_score: float = Field(default=0.0)
    readiness_score: float = Field(default=0.0)
    confidence_score: float = Field(default=0.0)
    priority_score: float = Field(default=0.0)
    
    final_score: float = Field(default=0.0, index=True)
    scored_at: datetime = Field(default_factory=datetime.utcnow)

    discovered_opportunity: Optional[DiscoveredOpportunity] = Relationship(back_populates="scores")

# ==========================================
# PART 4: AI DISCOVERY ARTIFACTS
# ==========================================
class OpportunitySearchHistory(SQLModel, table=True):
    __tablename__ = "opportunity_search_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    module_type: str = Field(index=True)
    persona: str = Field(default="Generic")
    
    generated_query: str
    query_type: str = Field(default="Type 1") # Type 1 to Type 6
    final_score: float = Field(default=0.0)
    search_frequency: str = Field(default="Monthly") # Daily, Weekly, Monthly
    search_depth: str = Field(default="Level 1") # Level 1, 2, 3
    source_targets: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    query_context: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    search_provider: str = Field(index=True) # e.g., "Google Custom Search", "Bing"
    
    execution_status: str = Field(default="Pending", index=True)
    search_timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    results_found: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DynamicFollowupQuestion(SQLModel, table=True):
    __tablename__ = "dynamic_followup_questions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    opportunity_id: int = Field(foreign_key="discovered_opportunities.id", index=True)
    module_type: str = Field(index=True)
    
    question: str
    question_type: str = Field(default="boolean") # boolean, multiple_choice, text
    importance: str = Field(default="high") # high, medium, low
    confidence_gain: float = Field(default=0.0)
    display_order: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AIRecommendation(SQLModel, table=True):
    __tablename__ = "ai_recommendations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    opportunity_id: int = Field(foreign_key="opportunities.id", index=True)
    
    recommendation_reason: str
    confidence_score: float = Field(index=True)
    
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None, index=True)

class OpportunityExplanation(SQLModel, table=True):
    __tablename__ = "opportunity_explanations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    opportunity_id: int = Field(foreign_key="opportunities.id", unique=True, index=True)
    
    explanation: str
    eligibility_explanation: str
    application_guidance: str
    benefit_summary: str
    
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
