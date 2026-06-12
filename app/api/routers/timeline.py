from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/timeline", tags=["Timeline"])
def get_timeline():
    return {
        "success": True,
        "message": "Timeline retrieved successfully",
        "events": [
            {
                "title": "PM Kisan Unlocked",
                "timestamp": datetime.now().isoformat()
            }
        ]
    }
