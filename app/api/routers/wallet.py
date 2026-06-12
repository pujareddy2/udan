from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/wallet/opportunities", tags=["Wallet"])
def get_wallet_opportunities():
    """Get full opportunity wallet dashboard state."""
    return {
        "wallet_status": "OK",
        "total_value_unlocked": 36000.0,
        "eligible_and_ready": [
            {
                "id": 1,
                "title": "NSP Central Sector",
                "benefit_value": 12000.0,
                "deadline": "2025-03-31"
            }
        ],
        "blocked_by_documents": [
            {
                "id": 5,
                "title": "PM-KISAN",
                "benefit_value": 6000.0
            }
        ],
        "expiring_soon": [
            {
                "id": 8,
                "title": "State Scholarship",
                "benefit_value": 5000.0,
                "deadline": "2024-05-01"
            }
        ],
        "under_review": []
    }

@router.post("/wallet/opportunities/{opp_id}/apply", tags=["Wallet"])
def apply_opportunity(opp_id: int):
    """Start application for an opportunity."""
    return {"message": "Application started successfully."}

@router.get("/wallet/documents", tags=["Wallet"])
def get_wallet_documents():
    """Get full document inventory dashboard state."""
    return {
        "wallet_status": "OK",
        "verified_documents": ["Aadhaar Card", "Income Certificate"],
        "missing_documents": ["Caste Certificate", "Bank Passbook"],
        "expiring_documents": ["Domicile Certificate (expires in 15 days)"]
    }
