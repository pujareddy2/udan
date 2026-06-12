from fastapi import APIRouter

router = APIRouter()

@router.get("/value", tags=["Value Engine"])
def get_value():
    """Calculate unlocked, potential, and missed monetary value."""
    return {
        "eligible_value": 50000,
        "potential_value": 120000,
        "missed_value": 30000
    }
