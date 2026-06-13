from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime

from app.core.db import get_session
from app.models.domain import User, UserProfile
from app.models.telegram_db import TelegramConnection, TelegramBotLog
from app.services.telegram_service import TelegramAPI, UdaanTelegramFormatter
from app.services.telegram_bot import (
    handle_update, push_opportunity_alert, push_deadline_alert,
    push_doc_missing, push_doc_recovery, push_approval, push_status_update,
    push_value_unlock
)

router = APIRouter(prefix="/telegram", tags=["Telegram Bot"])
tg_api = TelegramAPI()
formatter = UdaanTelegramFormatter()

# ─────────────────────────────────────────────────────────────
# REQUEST SCHEMAS
# ─────────────────────────────────────────────────────────────

class ConnectRequest(BaseModel):
    user_id: int
    telegram_chat_id: str
    telegram_username: Optional[str] = None
    language: Optional[str] = "en"

class TestMessageRequest(BaseModel):
    user_id: int
    message: str

class SendAlertRequest(BaseModel):
    user_id: int
    alert_type: str  # "opportunity", "deadline", "doc_missing", "doc_recovery", "approval", "status", "value_unlock"
    data: Dict[str, Any]


# ─────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────

@router.post("/connect")
def connect_telegram(req: ConnectRequest, session: Session = Depends(get_session)):
    """API endpoint to programmatically link a User to a Telegram chat ID."""
    user = session.get(User, req.user_id)
    if not user:
        raise HTTPException(status_code=442, detail="User not found")

    conn = session.exec(
        select(TelegramConnection).where(TelegramConnection.user_id == req.user_id)
    ).first()

    if conn:
        conn.telegram_chat_id = req.telegram_chat_id
        conn.telegram_username = req.telegram_username
        conn.language = req.language or conn.language
        conn.is_active = True
        conn.last_interaction = datetime.utcnow()
    else:
        conn = TelegramConnection(
            user_id=req.user_id,
            telegram_chat_id=req.telegram_chat_id,
            telegram_username=req.telegram_username,
            language=req.language or "en",
            last_interaction=datetime.utcnow()
        )
    session.add(conn)

    # Log connection event
    log = TelegramBotLog(
        user_id=req.user_id,
        telegram_chat_id=req.telegram_chat_id,
        direction="outbound",
        message_type="command",
        content=f"Connected account to Telegram chat_id={req.telegram_chat_id}",
        command="/connect"
    )
    session.add(log)
    session.commit()

    # Send confirmation message
    uprof = session.exec(select(UserProfile).where(UserProfile.user_id == req.user_id)).first()
    name = uprof.full_name if uprof else "User"
    welcome_text = formatter.welcome(name, conn.language)
    tg_api.send_message(req.telegram_chat_id, welcome_text)

    return {"status": "success", "message": "Telegram connection established", "telegram_username": req.telegram_username}


@router.get("/status/{user_id}")
def connection_status(user_id: int, session: Session = Depends(get_session)):
    """Check if a User has a linked Telegram bot connection."""
    conn = session.exec(
        select(TelegramConnection).where(TelegramConnection.user_id == user_id, TelegramConnection.is_active == True)
    ).first()
    if conn:
        return {
            "connected": True,
            "telegram_username": conn.telegram_username,
            "telegram_chat_id": conn.telegram_chat_id,
            "language": conn.language
        }
    return {"connected": False}


@router.post("/test")
def send_test_message(req: TestMessageRequest, session: Session = Depends(get_session)):
    """Send a custom test message to a connected user's Telegram."""
    conn = session.exec(
        select(TelegramConnection).where(TelegramConnection.user_id == req.user_id, TelegramConnection.is_active == True)
    ).first()
    if not conn:
        raise HTTPException(status_code=400, detail="Telegram connection not found or inactive for user")

    res = tg_api.send_message(conn.telegram_chat_id, req.message)
    
    # Log outbound
    log = TelegramBotLog(
        user_id=req.user_id,
        telegram_chat_id=conn.telegram_chat_id,
        direction="outbound",
        message_type="text",
        content=req.message
    )
    session.add(log)
    session.commit()

    return {"status": "success", "telegram_api_response": res}


@router.post("/send")
def send_alert(req: SendAlertRequest, session: Session = Depends(get_session)):
    """
    Manually push one of the 7 personalized alert types to the connected user.
    Types: opportunity, deadline, doc_missing, doc_recovery, approval, status, value_unlock
    """
    conn = session.exec(
        select(TelegramConnection).where(TelegramConnection.user_id == req.user_id, TelegramConnection.is_active == True)
    ).first()
    if not conn:
        raise HTTPException(status_code=400, detail="Telegram connection not found or inactive for user")

    chat_id = conn.telegram_chat_id
    lang = conn.language
    a_type = req.alert_type.lower()
    d = req.data

    try:
        if a_type == "opportunity":
            push_opportunity_alert(chat_id, d, lang)
        elif a_type == "deadline":
            push_deadline_alert(chat_id, d, lang)
        elif a_type == "doc_missing":
            push_doc_missing(chat_id, d.get("document", "Document"), d.get("blocked_count", 0), d.get("locked_value", 0.0), lang)
        elif a_type == "doc_recovery":
            push_doc_recovery(chat_id, d.get("document", "Document"), d.get("unlocks", 0), d.get("total_value", 0.0), lang)
        elif a_type == "approval":
            push_approval(chat_id, d.get("scheme", "Scheme"), d.get("benefit", "—"), lang)
        elif a_type == "status":
            push_status_update(chat_id, d.get("scheme", "Scheme"), d.get("status", "Under Review"), lang)
        elif a_type == "value_unlock":
            push_value_unlock(chat_id, d.get("old_value", 0.0), d.get("new_value", 0.0), lang)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported alert_type: {req.alert_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to dispatch alert: {e}")

    # Log notification sending
    log = TelegramBotLog(
        user_id=req.user_id,
        telegram_chat_id=chat_id,
        direction="outbound",
        message_type="alert",
        content=f"Sent alert type: {a_type} with data: {d}"
    )
    session.add(log)
    session.commit()

    return {"status": "success", "alert_type": a_type}


@router.get("/history/{user_id}")
def telegram_history(user_id: int, session: Session = Depends(get_session)):
    """Fetch audit history of Telegram messages for the user."""
    logs = session.exec(
        select(TelegramBotLog)
        .where(TelegramBotLog.user_id == user_id)
        .order_by(TelegramBotLog.created_at.desc())
        .limit(50)
    ).all()
    
    return {
        "history": [
            {
                "id": l.id,
                "direction": l.direction,
                "message_type": l.message_type,
                "content": l.content,
                "command": l.command,
                "created_at": l.created_at.isoformat()
            } for l in logs
        ]
    }


@router.post("/webhook")
def telegram_webhook(update: Dict[str, Any], background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    """
    Webhook target for Telegram bot updates.
    Processes updates asynchronously using BackgroundTasks.
    """
    background_tasks.add_task(handle_update, update, session)
    return {"ok": True}
