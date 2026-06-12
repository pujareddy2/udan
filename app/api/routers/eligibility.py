from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class EligibilityRequest(BaseModel):
    user_id: str

@router.post("/eligibility/run", tags=["Eligibility Engine"])
def run_eligibility(req: EligibilityRequest):
    return {
        "success": True,
        "message": "Eligibility check complete",
        "eligible": 7,
        "potential": 5,
        "not_eligible": 3,
        "confidence": 91,
        "top_matches": [
            {
                "scheme": "NSP Scholarship",
                "match_score": 96
            },
            {
                "scheme": "AICTE Scholarship",
                "match_score": 91
            }
        ]
    }

@router.post("/eligibility/questions", tags=["Eligibility Engine"])
def get_eligibility_questions():
    return {
        "success": True,
        "message": "Questions retrieved successfully",
        "questions": [
            {
                "id": "q1",
                "question": "Do you own the land?"
            }
        ]
    }
