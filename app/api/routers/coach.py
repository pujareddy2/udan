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

from pydantic import BaseModel

class CoachGenerateRequest(BaseModel):
    user_id: str
    prompt: str

@router.post("/coach/generate", tags=["Coach"])
def generate_coach_response(req: CoachGenerateRequest):
    prompt_lower = req.prompt.lower()
    if "guidance" in prompt_lower or "career" in prompt_lower:
        reply = "Based on your background in CSE and Python/SQL skills, you have a strong foundation. I recommend focusing on AI Engineering roles and starting with NAPS Apprenticeships or certified skilling programs like PMKVY to bridge any practical experience gaps."
    elif "resume" in prompt_lower:
        reply = "To boost your resume: 1. Feature your Python and SQL projects prominently at the top. 2. Highlight any hands-on course certifications. 3. Detail academic projects showing practical database manipulation."
    elif "jobs" in prompt_lower or "government" in prompt_lower:
        reply = "Here are the top matches: 1. SSC CGL 2026 (Value: ₹50,000, 1 day remaining). 2. TSPSC Group 4 2026 (Value: ₹30,000, 3 days remaining). 3. RRB NTPC 2025 (Value: ₹40,000)."
    elif "skilling" in prompt_lower or "program" in prompt_lower:
        reply = "I suggest PMKVY Skill Program. It offers industry-recognized certificates in advanced computing and AI/ML, completely free of cost, and includes a training stipend."
    elif "interview" in prompt_lower or "prep" in prompt_lower:
        reply = "Preparation strategy: 1. Revise quantitative aptitude and logical reasoning for SSC. 2. Practice typing tests for RRB. 3. Do mock interviews focusing on Python coding challenges and database query optimizations."
    elif "assistance" in prompt_lower or "application" in prompt_lower:
        reply = "Your highest value blocker is the Income Certificate. Obtaining this will immediately unlock the National Merit Scholarship and lower verification barriers on other schemes."
    else:
        reply = "Hello! I am your UDAAN AI Career Coach. How can I help you today? You can ask me about Career Guidance, Resume Help, Government Jobs, Skilling Programs, Interview Prep, or Application Assistance."
        
    return {
        "success": True,
        "reply": reply
    }
