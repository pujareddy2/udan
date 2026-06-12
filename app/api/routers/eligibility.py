from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class AnswersRequest(BaseModel):
    answers: dict

@router.post("/eligibility/run", tags=["Eligibility"])
def run_eligibility():
    """Trigger the eligibility calculation engine manually."""
    return {"status": "Eligibility engine triggered successfully."}

@router.get("/eligibility/{user_id}", tags=["Eligibility"])
def get_eligibility(user_id: int):
    """Get the calculated eligibility score for the user."""
    return {
        "eligible": True,
        "score": 92,
        "missing_documents": []
    }

@router.get("/eligibility/questions", tags=["Eligibility"])
def get_eligibility_questions():
    """Dynamic Eligibility: Get follow-up questions from the AI engine."""
    return {
        "questions": [
            "Do you own the land?",
            "Which crop do you cultivate?"
        ]
    }

@router.post("/eligibility/answers", tags=["Eligibility"])
def submit_eligibility_answers(req: AnswersRequest):
    """Dynamic Eligibility: Submit answers to follow-up questions."""
    return {"message": "Answers received, eligibility updated."}
