from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class VoiceChatRequest(BaseModel):
    message: str
    language: str

@router.post("/voice/chat", tags=["Voice Agent"])
def voice_chat(req: VoiceChatRequest):
    # Mocking a response in the requested language
    if req.language.lower() == "telugu":
        reply = "మీరు ఏ రాష్ట్రంలో వ్యవసాయం చేస్తున్నారు?"
    elif req.language.lower() == "hindi":
        reply = "आप किस राज्य में खेती करते हैं?"
    else:
        reply = "Which state are you farming in?"
        
    return {
        "success": True,
        "message": "Voice response generated",
        "reply": reply
    }
