import json
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy.types import JSON
from typing import Optional, List, Dict, Any
from datetime import datetime

# ==========================================
# PART 3: USERS DOMAIN
# ==========================================
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    is_active: bool = Field(default=True)
    last_login: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    profile: Optional["UserProfile"] = Relationship(back_populates="user")
    roles: List["UserRole"] = Relationship(back_populates="user")
    documents: List["Document"] = Relationship(back_populates="user")
    applications: List["Application"] = Relationship(back_populates="user")
    timeline_events: List["TimelineEvent"] = Relationship(back_populates="user")
    notifications: List["NotificationQueue"] = Relationship(back_populates="user")
    missed_opportunities: List["MissedOpportunity"] = Relationship(back_populates="user")
    snapshots_readiness: List["ReadinessSnapshot"] = Relationship(back_populates="user")
    snapshots_eligibility: List["EligibilitySnapshot"] = Relationship(back_populates="user")
    snapshots_value: List["ValueSnapshot"] = Relationship(back_populates="user")

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
    
    # Optional JSON for module-specific extensions
    profile_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="profile")

from pydantic import validator

class UserRole(SQLModel, table=True):
    __tablename__ = "user_roles"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    role: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="roles")
    
    @validator("role")
    def validate_role(cls, v):
        allowed_roles = ['student', 'farmer', 'jobseeker', 'entrepreneur', 'women_entrepreneur', 'startup', 'senior_citizen']
        if v not in allowed_roles:
            raise ValueError(f"Role must be one of: {allowed_roles}")
        return v

# ==========================================
# PART 4: OPPORTUNITIES DOMAIN
# ==========================================
class Opportunity(SQLModel, table=True):
    __tablename__ = "opportunities"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    module: str = Field(index=True)
    benefit_value: float = Field(default=0.0)
    provider_type: str = Field(default="government") # government, private
    state_target: str = Field(default="central", index=True)
    
    # JSON for dynamic rules
    eligibility_rules: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    required_documents: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    followup_questions: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    deadlines: List["OpportunityDeadline"] = Relationship(back_populates="opportunity")
    categories: List["OpportunityCategory"] = Relationship(back_populates="opportunity")
    applications: List["Application"] = Relationship(back_populates="opportunity")

class OpportunityDeadline(SQLModel, table=True):
    __tablename__ = "opportunity_deadlines"
    id: Optional[int] = Field(default=None, primary_key=True)
    opportunity_id: int = Field(foreign_key="opportunities.id", index=True)
    deadline_date: datetime = Field(index=True)
    cycle_name: str = Field(default="Current Cycle") # e.g. "NSP 2026-27"
    
    opportunity: Optional[Opportunity] = Relationship(back_populates="deadlines")

class OpportunityCategory(SQLModel, table=True):
    __tablename__ = "opportunity_categories"
    id: Optional[int] = Field(default=None, primary_key=True)
    opportunity_id: int = Field(foreign_key="opportunities.id", index=True)
    tag: str = Field(index=True) # e.g. "Minority", "Seed Fund"
    
    opportunity: Optional[Opportunity] = Relationship(back_populates="categories")

# ==========================================
# PART 5: DOCUMENT INTELLIGENCE DOMAIN
# ==========================================
class DocumentMaster(SQLModel, table=True):
    __tablename__ = "document_master"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    document_name: str = Field(unique=True, index=True)
    document_type: str = Field(default="General", index=True) # Identity, Financial, Property, Academic
    description: str
    
    issuing_authority: str = Field(index=True)
    official_apply_link: Optional[str] = Field(default=None)
    sample_image_url: Optional[str] = Field(default=None)
    
    validity_period: str = Field(default="Lifetime") # Lifetime, 1 Year, 6 Months
    renewal_required: bool = Field(default=False)
    
    required_supporting_documents: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    processing_time: str = Field(default="14 Days")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    resources: List["DocumentResource"] = Relationship(back_populates="document_master")
    user_documents: List["Document"] = Relationship(back_populates="document_master")
    recovery_guides: List["DocumentRecoveryGuide"] = Relationship(back_populates="document_master")

class DocumentResource(SQLModel, table=True):
    __tablename__ = "document_resources"
    id: Optional[int] = Field(default=None, primary_key=True)
    doc_master_id: int = Field(foreign_key="document_master.id", index=True)
    resource_type: str = Field(index=True) # SampleImage, SamplePDF, Template
    s3_url: str # Cloud URL Storage Strategy
    description: str
    
    document_master: Optional[DocumentMaster] = Relationship(back_populates="resources")

class Document(SQLModel, table=True):
    __tablename__ = "documents"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    doc_master_id: int = Field(foreign_key="document_master.id", index=True)
    
    status: str = Field(default="Pending") # Verified, Pending, Expired
    file_url: Optional[str] = Field(default=None) # S3 Storage Reference
    expiry_date: Optional[datetime] = Field(default=None, index=True)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="documents")
    document_master: Optional[DocumentMaster] = Relationship(back_populates="user_documents")

# ==========================================
# PART 6, 7, 8: SNAPSHOT DOMAINS
# ==========================================
class EligibilitySnapshot(SQLModel, table=True):
    __tablename__ = "eligibility_snapshots"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    opportunity_id: int = Field(foreign_key="opportunities.id", index=True)
    is_eligible: bool = Field(default=False)
    missing_fields: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="snapshots_eligibility")

class ReadinessSnapshot(SQLModel, table=True):
    __tablename__ = "readiness_snapshots"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    overall_score: float = Field(default=0.0)
    document_score: float = Field(default=0.0)
    primary_blocker: Optional[str] = Field(default=None)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="snapshots_readiness")

class ValueSnapshot(SQLModel, table=True):
    __tablename__ = "value_snapshots"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    total_available_value: float = Field(default=0.0)
    total_missed_value: float = Field(default=0.0)
    total_protected_value: float = Field(default=0.0)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="snapshots_value")

# ==========================================
# PART 9: APPLICATION TRACKING DOMAIN
# ==========================================
class Application(SQLModel, table=True):
    __tablename__ = "applications"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    opportunity_id: int = Field(foreign_key="opportunities.id", index=True)
    current_status: str = Field(default="Started", index=True) # Started, Pending, Approved, Rejected
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="applications")
    opportunity: Optional[Opportunity] = Relationship(back_populates="applications")
    status_history: List["ApplicationStatusHistory"] = Relationship(back_populates="application")

class ApplicationStatusHistory(SQLModel, table=True):
    __tablename__ = "application_status_history"
    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="applications.id", index=True)
    previous_status: str
    new_status: str
    changed_at: datetime = Field(default_factory=datetime.utcnow)
    
    application: Optional[Application] = Relationship(back_populates="status_history")

# ==========================================
# PART 10: NOTIFICATION & DIGEST DOMAIN
# ==========================================
class NotificationQueue(SQLModel, table=True):
    __tablename__ = "notification_queue"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    payload: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    priority_tier: str = Field(index=True) # CRITICAL, HIGH, MEDIUM, LOW
    status: str = Field(default="Pending", index=True) # Pending, Sent, Digested
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="notifications")

class NotificationHistory(SQLModel, table=True):
    __tablename__ = "notification_history"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    notification_type: str = Field(index=True)
    delivered_at: datetime = Field(default_factory=datetime.utcnow)
    action_taken: bool = Field(default=False)

class DigestHistory(SQLModel, table=True):
    __tablename__ = "digest_history"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    digest_type: str = Field(index=True) # Daily, Weekly
    total_value_summarized: float = Field(default=0.0)
    sent_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationPreferences(SQLModel, table=True):
    __tablename__ = "notification_preferences"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True, index=True)
    daily_digest_enabled: bool = Field(default=True)
    sms_enabled: bool = Field(default=False)
    whatsapp_enabled: bool = Field(default=False)

# ==========================================
# PART 11 & 12: MISSED OPPORTUNITY & TIMELINE DOMAIN
# ==========================================
class MissedOpportunity(SQLModel, table=True):
    __tablename__ = "missed_opportunities"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    opportunity_id: int = Field(foreign_key="opportunities.id", index=True)
    missed_value: float = Field(default=0.0)
    root_cause: str
    future_value_at_risk: float = Field(default=0.0)
    recovery_score: int = Field(default=0)
    missed_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="missed_opportunities")

class TimelineEvent(SQLModel, table=True):
    __tablename__ = "timeline_events"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    event_type: str = Field(index=True) # APPLIED, RECOVERED, MISSED, PROFILE_UPDATED
    title: str
    impact_value: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    user: Optional[User] = Relationship(back_populates="timeline_events")

# ==========================================
# PART 13: RESOURCE KNOWLEDGE BASE
# ==========================================
class ResourceMaster(SQLModel, table=True):
    __tablename__ = "resource_master"
    id: Optional[int] = Field(default=None, primary_key=True)
    target_entity_type: str = Field(index=True) # Document, Opportunity
    target_entity_id: int = Field(index=True)
    official_apply_link: str
    official_info_link: str
    government_department: str
    office_address: str
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ==========================================
# PART 14: SPECIFIC MODULE PROFILES
# ==========================================

class StudentProfile(SQLModel, table=True):
    __tablename__ = "student_profiles"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, unique=True)
    
    education_level: str
    current_course: str
    institution_type: str
    annual_family_income: float
    previous_year_marks_percentage: float
    is_orphan: bool = Field(default=False)
    is_disabled: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FarmerProfile(SQLModel, table=True):
    __tablename__ = "farmer_profiles"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, unique=True)
    
    land_size_acres: float
    land_type: str
    primary_crop: str
    pm_kisan_id: Optional[str] = Field(default=None)
    has_kisan_credit_card: bool = Field(default=False)
    annual_income: float
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class JobSeekerProfile(SQLModel, table=True):
    __tablename__ = "jobseeker_profiles"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, unique=True)
    
    education_level: str
    skills: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    employment_status: str
    years_of_experience: float = Field(default=0.0)
    preferred_job_role: str
    is_disabled: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EntrepreneurProfile(SQLModel, table=True):
    __tablename__ = "entrepreneur_profiles"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, unique=True)
    
    business_type: str
    industry_sector: str
    annual_turnover: float
    years_in_operation: float
    msme_udyam_number: Optional[str] = Field(default=None)
    number_of_employees: int = Field(default=1)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WomenEntrepreneurProfile(SQLModel, table=True):
    __tablename__ = "women_entrepreneur_profiles"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, unique=True)
    
    business_type: str
    industry_sector: str
    annual_turnover: float
    percentage_women_ownership: float
    msme_udyam_number: Optional[str] = Field(default=None)
    marital_status: str
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class StartupProfile(SQLModel, table=True):
    __tablename__ = "startup_profiles"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, unique=True)
    
    dpiit_recognized: bool = Field(default=False)
    startup_india_id: Optional[str] = Field(default=None)
    funding_stage: str
    patent_count: int = Field(default=0)
    incubator_attached: bool = Field(default=False)
    annual_turnover: float
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SeniorCitizenProfile(SQLModel, table=True):
    __tablename__ = "senior_citizen_profiles"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, unique=True)
    
    marital_status: str
    living_arrangement: str
    pension_status: str
    health_conditions: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    annual_income: float
    is_disabled: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
