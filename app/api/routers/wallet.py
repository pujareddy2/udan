from fastapi import APIRouter, Depends
from typing import Dict, Any
from app.api.schemas.common import WalletDashboardResponse, DocumentDashboardResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/wallet", tags=["Opportunity & Document Wallets"])

@router.get("/opportunities", response_model=WalletDashboardResponse)
def get_opportunity_wallet(user_id: int = Depends(get_current_user)):
    """
    Returns the massive Swiggy-style dashboard state categorizing all opportunities into actionable buckets.
    """
    return {
        "wallet_status": "OK",
        "total_value_unlocked": 0.0,
        "eligible_and_ready": [],
        "blocked_by_documents": [],
        "expiring_soon": [],
        "under_review": []
    }

@router.post("/opportunities/{opp_id}/apply")
def start_application(opp_id: int, user_id: int = Depends(get_current_user)):
    """
    Marks an opportunity as 'Started' in the user's application tracker.
    """
    return {"message": "Application started successfully."}

@router.get("/documents", response_model=DocumentDashboardResponse)
def get_document_wallet(user_id: int = Depends(get_current_user)):
    """
    Returns the master state of the user's document inventory.
    """
    return {
        "wallet_status": "OK",
        "verified_documents": [],
        "missing_documents": [],
        "expiring_documents": []
    }
