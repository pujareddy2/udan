from fastapi import APIRouter

router = APIRouter()

@router.get("/approval", tags=["Intelligence"])
def get_approval_intelligence():
    """Get overall approval intelligence and probability."""
    return {
        "probability": 87,
        "level": "High"
    }

@router.get("/opportunity-health/{opportunity_id}", tags=["Intelligence"])
def get_opportunity_health(opportunity_id: int):
    """Get health score and status for an opportunity."""
    return {
        "opportunity_id": opportunity_id,
        "health_score": 95,
        "status": "Apply Immediately"
    }

@router.get("/trust/{opportunity_id}", tags=["Intelligence"])
def get_trust_score(opportunity_id: int):
    """Get trust verification score for an opportunity."""
    return {
        "opportunity_id": opportunity_id,
        "trust_score": 98,
        "trust_level": "Verified"
    }
