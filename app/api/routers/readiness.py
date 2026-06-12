from fastapi import APIRouter

router = APIRouter()

@router.get("/readiness", tags=["Readiness Engine"])
def get_readiness(user_id: str):
    return {
        "overall_readiness": 82,
        "profile_readiness": 90,
        "document_readiness": 75,
        "academic_readiness": 88,
        "skill_readiness": 76,
        "missing_documents": [
            "Income Certificate"
        ],
        "missing_skills": [
            "Research"
        ]
    }
