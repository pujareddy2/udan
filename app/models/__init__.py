# Expose all models so that SQLModel.metadata.create_all(engine) registers them.
from app.models.domain import (
    User,
    UserProfile,
    UserRole,
    Opportunity,
    OpportunityDeadline,
    OpportunityCategory,
    DocumentMaster,
    DocumentResource,
    Document,
    EligibilitySnapshot,
    ReadinessSnapshot,
    ValueSnapshot,
    Application,
    ApplicationStatusHistory,
    NotificationQueue,
    NotificationHistory,
    DigestHistory,
    NotificationPreferences,
    MissedOpportunity,
    ResourceMaster,
    StudentProfile,
    FarmerProfile,
    JobSeekerProfile,
    EntrepreneurProfile,
    WomenEntrepreneurProfile,
    StartupProfile,
    SeniorCitizenProfile,
)

from app.models.discovery import (
    DiscoveredOpportunity,
    OpportunitySource,
    OpportunitySearchHistory,
    OpportunityValidation,
    OpportunityScore,
    DynamicFollowupQuestion,
    AIRecommendation,
    OpportunityExplanation,
)

from app.models.context import (
    ProfileContext,
    ContextHistory,
)

from app.models.fusion import (
    OpportunityAlias,
    OpportunityVersion,
    OpportunityChangeLog,
    OpportunitySourceMap,
)

from app.models.eligibility_db import (
    UserOpportunityEligibility,
)

from app.models.dynamic_db import (
    DynamicQuestionBank,
    UserQuestionAnswer,
    QuestionConfidenceHistory,
)

from app.models.readiness_db import (
    UserReadiness,
    ReadinessBreakdown,
    ReadinessRecommendation,
)

from app.models.recovery_db import (
    DocumentRecoveryGuide,
    DocumentStateProcess,
    DocumentSubstitute,
    UserRecoveryHistory,
)

from app.models.value_db import (
    UserValueSummary,
    OpportunityValueScore,
    DocumentValueImpact,
    ValueForecast,
)

from app.models.coach_db import (
    ApplicationCoaching,
    ApplicationRiskAnalysis,
    ApplicationStrategy,
    ApplicationActionPlan,
)

from app.models.wallet_db import (
    OpportunityWallet,
    WalletSnapshot,
    WalletInsight,
)

from app.models.recovery_engine_db import (
    MissedOpportunityAnalysis,
    BehaviorAnalytics,
    UserRecoveryAction,
)

from app.models.notification_db import (
    Notification,
    NotificationBehavior,
    NotificationDigest,
)

from app.models.timeline_db import (
    TimelineEvent,
    TimelineMilestone,
    TimelineAchievement,
    TimelinePrediction,
    TimelineAnalytics,
)

from app.models.intelligence_db import (
    OpportunityTrustScore,
    ApprovalPrediction,
    OpportunityHealthScore,
)

__all__ = [
    "User",
    "UserProfile",
    "UserRole",
    "Opportunity",
    "OpportunityDeadline",
    "OpportunityCategory",
    "DocumentMaster",
    "DocumentResource",
    "Document",
    "EligibilitySnapshot",
    "ReadinessSnapshot",
    "ValueSnapshot",
    "Application",
    "ApplicationStatusHistory",
    "NotificationQueue",
    "NotificationHistory",
    "DigestHistory",
    "NotificationPreferences",
    "MissedOpportunity",
    "ResourceMaster",
    "StudentProfile",
    "FarmerProfile",
    "JobSeekerProfile",
    "EntrepreneurProfile",
    "WomenEntrepreneurProfile",
    "StartupProfile",
    "SeniorCitizenProfile",
    "DiscoveredOpportunity",
    "OpportunitySource",
    "OpportunitySearchHistory",
    "OpportunityValidation",
    "OpportunityScore",
    "DynamicFollowupQuestion",
    "AIRecommendation",
    "OpportunityExplanation",
    "ProfileContext",
    "ContextHistory",
    "OpportunityAlias",
    "OpportunityVersion",
    "OpportunityChangeLog",
    "OpportunitySourceMap",
    "UserOpportunityEligibility",
    "DynamicQuestionBank",
    "UserQuestionAnswer",
    "QuestionConfidenceHistory",
    "UserReadiness",
    "ReadinessBreakdown",
    "ReadinessRecommendation",
    "DocumentRecoveryGuide",
    "DocumentStateProcess",
    "DocumentSubstitute",
    "UserRecoveryHistory",
    "UserValueSummary",
    "OpportunityValueScore",
    "DocumentValueImpact",
    "ValueForecast",
    "ApplicationCoaching",
    "ApplicationRiskAnalysis",
    "ApplicationStrategy",
    "ApplicationActionPlan",
    "OpportunityWallet",
    "WalletSnapshot",
    "WalletInsight",
    "MissedOpportunityAnalysis",
    "BehaviorAnalytics",
    "UserRecoveryAction",
    "Notification",
    "NotificationBehavior",
    "NotificationDigest",
    "TimelineEvent",
    "TimelineMilestone",
    "TimelineAchievement",
    "TimelinePrediction",
    "TimelineAnalytics",
    "OpportunityTrustScore",
    "ApprovalPrediction",
    "OpportunityHealthScore",
]
