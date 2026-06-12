from fastapi import APIRouter

router = APIRouter()

@router.get("/readiness", tags=["Readiness"])
def get_readiness():
    """Get the aggregate readiness score."""
    return {"score": 82}

@router.get("/readiness/breakdown", tags=["Readiness"])
def get_readiness_breakdown():
    """Get the detailed breakdown of the readiness score."""
    return {
        "score": 82,
        "documents": 90,
        "skills": 70
    }
