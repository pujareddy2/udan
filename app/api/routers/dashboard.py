from fastapi import APIRouter

router = APIRouter()

@router.get("/dashboard", tags=["Dashboard"])
def get_dashboard_summary():
    """Mega Endpoint: Aggregates Wallet, Notifications, Readiness, Value, and Opportunities."""
    return {
        "wallet": {
            "eligible_and_ready": [{"id": 1, "title": "NSP Central Sector"}],
            "blocked_by_documents": [{"id": 5, "title": "PM-KISAN"}]
        },
        "notifications": {
            "unread_count": 1,
            "latest": "Your Aadhaar Card expires in 30 days."
        },
        "readiness": {
            "score": 82
        },
        "value": {
            "eligible_value": 50000,
            "potential_value": 120000
        },
        "opportunities": [
            {"id": 1, "title": "NSP Central Sector"},
            {"id": 5, "title": "PM-KISAN"}
        ]
    }
