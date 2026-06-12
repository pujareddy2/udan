from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ProfileContextRequest(BaseModel):
    user_id: int

@router.post("/profile-context/generate", tags=["Profile Context"])
def generate_profile_context(req: ProfileContextRequest):
    """Generate the AI persona and context from the user's profile."""
    return {"message": "Profile context generated successfully."}

@router.get("/profile-context/{user_id}", tags=["Profile Context"])
def get_profile_context(user_id: int):
    """Get the AI persona and context for a user."""
    return {
        "persona": "Small Farmer",
        "keywords": ["agriculture", "subsidy", "irrigation"],
        "categories": ["Farmer", "Rural", "Financial Support"]
    }
