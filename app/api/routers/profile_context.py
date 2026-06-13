from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select
from app.core.db import get_session
from app.models.domain import UserProfile

router = APIRouter()

class ProfileContextRequest(BaseModel):
    user_id: str

@router.post("/profile-context/generate", tags=["Profile Context Engine"])
def generate_profile_context(req: ProfileContextRequest, session: Session = Depends(get_session)):
    try:
        user_id = int(req.user_id)
        user_profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    except:
        user_profile = None
        
    persona = "Engineering Student"
    interests = ["Scholarships", "Internships", "Research Programs", "Hackathons"]
    
    if user_profile:
        role = user_profile.user.module_type if user_profile.user else "student"
        if role == "farmer" or role == "farmers":
            persona = "Rythu (Farmer)"
            interests = ["Subsidies", "Loans", "Insurance"]
        elif role == "student" or role == "students":
            branch = user_profile.profile_data.get("branch", "CSE") if user_profile.profile_data else "CSE"
            degree = user_profile.profile_data.get("degree", "BTech") if user_profile.profile_data else "BTech"
            persona = f"{degree} {branch} Student"
            interests = (user_profile.profile_data or {}).get("opportunity_interests", interests)
            
    categories = [i for i in interests]
    keywords_exact = [c for c in categories]
    # Replace "Research Programs" with "Research" if present to match the exact keywords spec
    if "Research Programs" in keywords_exact:
        idx = keywords_exact.index("Research Programs")
        keywords_exact[idx] = "Research"
        
    return {
        "persona": persona,
        "keywords": keywords_exact,
        "categories": categories,
        "opportunity_categories": categories
    }
