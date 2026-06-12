from fastapi import APIRouter

router = APIRouter()

def _get_mock_dashboard(role: str, user_id: str):
    return {
        "success": True,
        "message": f"{role.capitalize()} dashboard retrieved successfully",
        "user_name": "Puja",
        "completion_percentage": 84,
        "readiness_score": 82,
        "eligible_opportunities": 12,
        "potential_opportunities": 5,
        "documents_missing": 2,
        "eligible_value": 50000,
        "potential_value": 120000,
        "approval_probability": 89,
        "top_opportunity": "PM Kisan" if role == "farmer" else "NSP Scholarship"
    }

@router.get("/dashboard/student/{user_id}", tags=["Dashboard"])
def get_student_dashboard(user_id: str):
    return _get_mock_dashboard("student", user_id)

@router.get("/dashboard/farmer/{user_id}", tags=["Dashboard"])
def get_farmer_dashboard(user_id: str):
    return _get_mock_dashboard("farmer", user_id)

@router.get("/dashboard/jobseeker/{user_id}", tags=["Dashboard"])
def get_jobseeker_dashboard(user_id: str):
    return _get_mock_dashboard("jobseeker", user_id)

@router.get("/dashboard/entrepreneur/{user_id}", tags=["Dashboard"])
def get_entrepreneur_dashboard(user_id: str):
    return _get_mock_dashboard("entrepreneur", user_id)

@router.get("/dashboard/women-entrepreneur/{user_id}", tags=["Dashboard"])
def get_women_entrepreneur_dashboard(user_id: str):
    return _get_mock_dashboard("women_entrepreneur", user_id)

@router.get("/dashboard/startup/{user_id}", tags=["Dashboard"])
def get_startup_dashboard(user_id: str):
    return _get_mock_dashboard("startup", user_id)

@router.get("/dashboard/senior-citizen/{user_id}", tags=["Dashboard"])
def get_senior_citizen_dashboard(user_id: str):
    return _get_mock_dashboard("senior_citizen", user_id)
