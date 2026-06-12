from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class CoachRequest(BaseModel):
    opportunity_id: int

@router.post("/coach/generate", tags=["Application Coach"])
def generate_coach_guidance(req: CoachRequest):
    """Generate AI coaching steps for a specific application."""
    return {
        "why_eligible": "Your income is below 2.5L and you have >60% in 12th.",
        "approval_probability": 87,
        "next_steps": [
            "Gather your Income Certificate and Aadhaar.",
            "Visit the portal and click 'New Registration'.",
            "Fill the form and upload documents."
        ]
    }
