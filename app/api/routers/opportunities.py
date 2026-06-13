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

@router.get("/opportunities/categories", tags=["Opportunities"])
def get_opportunity_categories(user_id: int = None):
    categories = [
        {"name": "Scholarships", "available": 1240, "matched": 14, "eligible": 8, "icon": "award", "note": "Merit & means-based"},
        {"name": "Internships", "available": 860, "matched": 12, "eligible": 6, "icon": "briefcase", "note": "Govt & corporate"},
        {"name": "Fellowships", "available": 95, "matched": 5, "eligible": 2, "icon": "star", "note": "Research & policy"},
        {"name": "Research Programs", "available": 310, "matched": 6, "eligible": 3, "icon": "flask", "note": "Funded projects"},
        {"name": "Hackathons", "available": 42, "matched": 4, "eligible": 2, "icon": "code", "note": "Build · win · get hired"},
        {"name": "Jobs", "available": 5600, "matched": 25, "eligible": 15, "icon": "building", "note": "Full-time & part-time careers"},
        {"name": "Competitions", "available": 150, "matched": 8, "eligible": 4, "icon": "trophy", "note": "National & global contests"},
        {"name": "Conferences", "available": 75, "matched": 5, "eligible": 3, "icon": "globe", "note": "Academic & tech summits"},
        {"name": "Training Programs", "available": 320, "matched": 18, "eligible": 10, "icon": "book", "note": "Skill certifications"}
    ]
    return {"categories": categories}

