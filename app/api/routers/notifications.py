from fastapi import APIRouter

router = APIRouter()

@router.get("/notifications", tags=["Notifications"])
def get_notifications():
    return {
        "success": True,
        "message": "Notifications retrieved successfully",
        "notifications": [
            {
                "id": "notif_1",
                "title": "Document Missing",
                "message": "Please upload your Income Certificate",
                "read": False
            }
        ]
    }

@router.put("/notifications/{id}/read", tags=["Notifications"])
def mark_notification_read(id: str):
    return {
        "success": True,
        "message": "Notification marked as read"
    }
