from fastapi import APIRouter

router = APIRouter()

@router.get("/value", tags=["Value Engine"])
def get_value(user_id: str):
    return {
        "eligible_value": 50000,
        "potential_value": 120000,
        "blocked_value": 70000,
        "recovery_value": 70000
    }
