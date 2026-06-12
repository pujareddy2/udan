from fastapi import APIRouter

router = APIRouter()

@router.get("/notifications", tags=["Notifications"])
def get_notifications():
    """Get all notifications for the user."""
    return {
        "notifications": [
            {"id": 1, "message": "Your Aadhaar Card expires in 30 days.", "read": False},
            {"id": 2, "message": "New PM-KISAN installment is available.", "read": True}
        ]
    }

@router.put("/notifications/{id}/read", tags=["Notifications"])
def mark_notification_read(id: int):
    """Mark a specific notification as read."""
    return {"message": f"Notification {id} marked as read."}

@router.get("/notifications/unread-count", tags=["Notifications"])
def get_unread_count():
    """Get the count of unread notifications."""
    return {"count": 1}
