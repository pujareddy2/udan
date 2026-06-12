from fastapi import APIRouter

router = APIRouter()

@router.get("/wallet/opportunities", tags=["Wallet"])
def get_wallet_opportunities():
    return {
        "success": True,
        "message": "Wallet opportunities retrieved",
        "ready": [],
        "blocked": [],
        "needs_clarification": [],
        "applied": [],
        "under_review": [],
        "missed": [],
        "recovered": []
    }
