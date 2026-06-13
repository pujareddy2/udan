import requests
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from typing import Optional

from app.core.db import get_session
from app.models.domain import UserProfile, FarmerProfile
from app.core.config import settings

router = APIRouter()

class VoiceChatRequest(BaseModel):
    user_id: str
    module: str = "farmer"
    language: str = "en"
    message: str

@router.post("/voice/chat", tags=["Voice Agent"])
def voice_chat(req: VoiceChatRequest, session: Session = Depends(get_session)):
    # 1. Fetch user profile context
    user_context = ""
    try:
        uid = int(req.user_id)
        uprof = session.exec(select(UserProfile).where(UserProfile.user_id == uid)).first()
        fprof = session.exec(select(FarmerProfile).where(FarmerProfile.user_id == uid)).first()
        if uprof:
            user_context += f"User Profile: Name: {uprof.full_name}, State: {uprof.state}, District: {uprof.district}\n"
            if uprof.profile_data:
                user_context += f"Docs: {uprof.profile_data.get('documents')}\n"
        if fprof:
            user_context += f"Farmer Data: Land: {fprof.land_size_acres} acres ({fprof.land_type}), Crop: {fprof.primary_crop}\n"
    except:
        pass
        
    system_prompt = f"""You are the Udaan AI Farmer Voice Agent.
You must always output valid JSON in the exact format requested.
The user speaks in {req.language}. Your "reply" and "followup_questions" MUST be in {req.language}.
Do not provide generic advice. Focus on government schemes, eligibility, missing documents, and application steps.

User Context:
{user_context}

Output JSON Format:
{{
  "reply": "Your conversational response in {req.language}",
  "opportunities": [
    {{ "scheme": "Name", "benefit": "Amount", "eligibility_score": 90 }}
  ],
  "missing_documents": ["List of missing docs"],
  "application_link": "URL or null",
  "recovery_guide": "Instructions or null",
  "followup_questions": ["Question 1 in {req.language}"],
  "next_action": "Actionable step"
}}
"""

    api_key = settings.GROQ_API_KEY
    if api_key:
        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.message}
            ],
            "response_format": {"type": "json_object"}
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return json.loads(data['choices'][0]['message']['content'])
        except Exception as e:
            print("Groq failed, falling back to mock.", e)
            
    # Fallback to mock response
    reply = "మీరు పిఎం కిసాన్ పథకానికి అర్హులు కావచ్చు. మీకు భూమి పాస్ బుక్ ఉందా?" if req.language == "te" else "You might be eligible for PM Kisan. Do you have a land passbook?"
    return {
        "reply": reply,
        "opportunities": [
            {"scheme": "PM Kisan", "benefit": "₹6000", "eligibility_score": 94}
        ],
        "missing_documents": ["Land Passbook"],
        "followup_questions": ["Is the land registered in your name?"],
        "next_action": "Upload Land Passbook",
        "application_link": "https://pmkisan.gov.in",
        "recovery_guide": "Visit MeeSeva"
    }

@router.get("/voice/suggestions", tags=["Voice Agent"])
def voice_suggestions(module: str = "farmer"):
    return {
        "questions": [
            "Which schemes am I eligible for?",
            "What subsidy can I get for 2 acres?",
            "How to get an income certificate?",
            "How to apply for PM Kisan?",
            "What documents are missing?"
        ]
    }

@router.get("/voice/history/{user_id}", tags=["Voice Agent"])
def voice_history(user_id: str):
    return {
        "history": [
            {
                "question": "Which schemes am I qualify for?",
                "answer": "Based on your profile, you may qualify for PM Kisan."
            }
        ]
    }

@router.post("/voice/transcribe", tags=["Voice Agent"])
def voice_transcribe():
    return {
        "text": "నా దగ్గర 2 ఎకరాల భూమి ఉంది"
    }

@router.post("/voice/speak", tags=["Voice Agent"])
def voice_speak(payload: dict):
    return {
        "audio_url": "https://example.com/audio.mp3"
    }
