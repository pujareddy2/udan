from fastapi import APIRouter

router = APIRouter()

@router.get("/opportunities/{opportunity_id}/guidance", tags=["Coach"])
def get_opportunity_guidance(opportunity_id: str):
    return {
        "success": True,
        "message": "Guidance retrieved successfully",
        "why_apply": "High value scholarship",
        "approval_probability": 89,
        "documents_needed": [
            "Income Certificate",
            "Aadhaar Card"
        ],
        "estimated_time": "15 Minutes",
        "next_action": "Upload Income Certificate"
    }
