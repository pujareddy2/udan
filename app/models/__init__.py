# Expose all models so that SQLModel.metadata.create_all(engine) registers them.
from app.models.user import User, UserProfile
from app.models.opportunity import Opportunity
from app.models.wallet import OpportunityWallet
from app.models.document import Document
from app.models.notification import Notification

__all__ = [
    "User",
    "UserProfile",
    "Opportunity",
    "OpportunityWallet",
    "Document",
    "Notification"
]
