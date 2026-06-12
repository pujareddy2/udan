from fastapi import APIRouter

router = APIRouter()

@router.get("/notifications", tags=["Notifications"])
def get_notifications():
    return {
        "notifications": []
    }

@router.get("/notifications/summary", tags=["Notifications"])
def get_notifications_summary():
    return {
        "unread": 5,
        "deadlines": 2,
        "new_opportunities": 3
    }

@router.put("/notifications/{id}/read", tags=["Notifications"])
def mark_notification_read(id: str):
    return {
        "success": True,
        "message": "Notification marked as read"
    }
