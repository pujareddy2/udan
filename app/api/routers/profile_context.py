from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ProfileContextRequest(BaseModel):
    user_id: str

@router.post("/profile-context/generate", tags=["Profile Context Engine"])
def generate_profile_context(req: ProfileContextRequest):
    return {
        "persona": "Engineering Student",
        "intent": "Scholarships and Internships",
        "keywords": [
            "engineering scholarship",
            "internships",
            "hackathons"
        ],
        "opportunity_categories": [
            "Scholarships",
            "Internships",
            "Research Programs",
            "Hackathons"
        ]
    }
