from fastapi import APIRouter
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/timeline", tags=["Timeline"])
def get_timeline():
    return {
        "events": [
            {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "event": "Opportunity Discovered"
            },
            {
                "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "event": "Profile Created"
            }
        ]
    }

@router.get("/deadlines/upcoming", tags=["Timeline"])
def get_upcoming_deadlines():
    return {
        "deadlines": [
            {
                "scheme": "PM Kisan Application",
                "days_remaining": 3
            },
            {
                "scheme": "Crop Insurance Enrollment",
                "days_remaining": 5
            }
        ]
    }
