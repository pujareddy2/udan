from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.core.db import get_session
from app.models.domain import User

router = APIRouter()

@router.get("/timeline", tags=["Timeline"])
def get_timeline(user_id: int = None, session: Session = Depends(get_session)):
    is_student = False
    if user_id:
        user = session.get(User, user_id)
        if user and (user.module_type == "student" or user.module_type == "students"):
            is_student = True
            
    if is_student:
        return {
            "events": [
                {"date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"), "event": "Profile Created"},
                {"date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"), "event": "Profile Completed"},
                {"date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"), "event": "Eligibility Checked"},
                {"date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"), "event": "Applied"},
                {"date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"), "event": "Selected"}
            ]
        }
    else:
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
def get_upcoming_deadlines(user_id: int = None, session: Session = Depends(get_session)):
    is_student = False
    if user_id:
        user = session.get(User, user_id)
        if user and (user.module_type == "student" or user.module_type == "students"):
            is_student = True
            
    if is_student:
        return {
            "deadlines": [
                {
                    "scheme": "AICTE Internship",
                    "days_remaining": 3
                },
                {
                    "scheme": "INSPIRE",
                    "days_remaining": 5
                },
                {
                    "scheme": "SIH",
                    "days_remaining": 8
                }
            ]
        }
    else:
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

