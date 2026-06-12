from fastapi import APIRouter

router = APIRouter()

def _get_mock_opportunities(role: str):
    return {
        "success": True,
        "message": f"Opportunities summary for {role}",
        "total": 12,
        "eligible": 7,
        "potential": 3,
        "blocked": 2
    }

@router.get("/student/opportunities/summary", tags=["Opportunities"])
def get_student_opportunities():
    return _get_mock_opportunities("student")

@router.get("/farmer/opportunities/summary", tags=["Opportunities"])
def get_farmer_opportunities():
    return _get_mock_opportunities("farmer")

@router.get("/jobseeker/opportunities/summary", tags=["Opportunities"])
def get_jobseeker_opportunities():
    return _get_mock_opportunities("jobseeker")

@router.get("/entrepreneur/opportunities/summary", tags=["Opportunities"])
def get_entrepreneur_opportunities():
    return _get_mock_opportunities("entrepreneur")

@router.get("/women-entrepreneur/opportunities/summary", tags=["Opportunities"])
def get_women_entrepreneur_opportunities():
    return _get_mock_opportunities("women-entrepreneur")

@router.get("/startup/opportunities/summary", tags=["Opportunities"])
def get_startup_opportunities():
    return _get_mock_opportunities("startup")

@router.get("/senior-citizen/opportunities/summary", tags=["Opportunities"])
def get_senior_citizen_opportunities():
    return _get_mock_opportunities("senior-citizen")
