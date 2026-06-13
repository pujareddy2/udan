"""
Telegram Bot Handler — UDAAN AI
================================
Receives webhook updates from Telegram and dispatches to the right command handler.
Each command pulls live data from the existing UDAAN backend engines.
"""

from sqlmodel import Session, select
from typing import Optional, Dict, Any

from app.models.domain import User, UserProfile, FarmerProfile, StudentProfile as StudentProfileDB
from app.models.telegram_db import TelegramConnection, TelegramBotLog
from app.services.telegram_service import (
    TelegramAPI, UdaanTelegramFormatter, detect_language, ask_ai_coach
)
from app.core.config import settings

import requests

tg = TelegramAPI()
fmt = UdaanTelegramFormatter()


# ─────────────────────────────────────────────────────────────
# PROFILE CONTEXT BUILDER
# ─────────────────────────────────────────────────────────────

def _build_user_context(user_id: int, session: Session) -> str:
    """Build a plain-text profile summary for AI chat context."""
    try:
        uprof = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
        user = session.get(User, user_id)
        if not uprof:
            return "No profile found."
        parts = [
            f"Name: {uprof.full_name}",
            f"State: {uprof.state}",
            f"Category: {uprof.category}",
            f"Role: {user.module_type if user else 'unknown'}",
        ]
        pd = uprof.profile_data or {}
        if pd.get("degree"):
            parts.append(f"Degree: {pd['degree']} - {pd.get('branch', '')}")
        if pd.get("cgpa"):
            parts.append(f"CGPA: {pd['cgpa']}")
        if pd.get("annual_family_income"):
            parts.append(f"Annual Income: ₹{pd['annual_family_income']}")
        if pd.get("skills"):
            parts.append(f"Skills: {', '.join(pd['skills'][:5])}")
        if pd.get("documents"):
            parts.append(f"Documents: {', '.join(pd['documents'])}")
        return "\n".join(parts)
    except Exception as e:
        return f"Profile fetch error: {e}"


def _get_backend_json(path: str, user_id: int) -> Optional[Dict]:
    """Call the local FastAPI backend and return parsed JSON."""
    try:
        base = "http://localhost:8000/api/v1"
        r = requests.get(f"{base}{path}", params={"user_id": user_id}, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def _log(session: Session, user_id: Optional[int], chat_id: str,
         direction: str, msg_type: str, content: str, command: Optional[str] = None):
    log = TelegramBotLog(
        user_id=user_id,
        telegram_chat_id=chat_id,
        direction=direction,
        message_type=msg_type,
        content=content[:2000],
        command=command,
    )
    session.add(log)
    session.commit()


# ─────────────────────────────────────────────────────────────
# MAIN DISPATCHER
# ─────────────────────────────────────────────────────────────

def handle_update(update: dict, session: Session):
    """Entry point. Routes incoming Telegram updates to the correct handler."""

    # ── Handle callback queries (button presses) ──
    if "callback_query" in update:
        return _handle_callback(update["callback_query"], session)

    message = update.get("message") or update.get("edited_message")
    if not message:
        return

    chat_id = str(message["chat"]["id"])
    text = (message.get("text") or "").strip()
    tg_username = message.get("from", {}).get("username")

    # Find linked UDAAN user
    conn = session.exec(
        select(TelegramConnection).where(TelegramConnection.telegram_chat_id == chat_id)
    ).first()
    user_id = conn.user_id if conn else None

    # Language detection
    lang = conn.language if conn else detect_language(text)

    # Log inbound
    _log(session, user_id, chat_id, "inbound", "text", text,
         command=text.split()[0] if text.startswith("/") else None)

    # ── Command routing ──
    if text.startswith("/start"):
        _cmd_start(chat_id, text, tg_username, session, lang)
    elif text == "/help":
        _cmd_help(chat_id, lang)
    elif text == "/profile":
        _cmd_profile(chat_id, user_id, session, lang)
    elif text == "/opportunities":
        _cmd_opportunities(chat_id, user_id, lang)
    elif text == "/wallet":
        _cmd_wallet(chat_id, user_id, lang)
    elif text == "/documents":
        _cmd_documents(chat_id, user_id, lang)
    elif text == "/readiness":
        _cmd_readiness(chat_id, user_id, lang)
    elif text == "/value":
        _cmd_value(chat_id, user_id, lang)
    elif text == "/deadlines":
        _cmd_deadlines(chat_id, user_id, lang)
    elif text == "/recovery":
        _cmd_recovery(chat_id, user_id, lang)
    elif text == "/coach":
        _cmd_coach_intro(chat_id, lang)
    elif text and not text.startswith("/"):
        # Free text → AI chat
        _cmd_free_chat(chat_id, text, user_id, session, lang)
    else:
        tg.send_message(chat_id, "❓ Unknown command. Use /help to see all commands.")


# ─────────────────────────────────────────────────────────────
# COMMAND HANDLERS
# ─────────────────────────────────────────────────────────────

def _cmd_start(chat_id: str, text: str, tg_username: Optional[str],
               session: Session, lang: str):
    """
    /start [user_id]
    Connects the Telegram account to a UDAAN user account.
    Deep-link: t.me/udaan_ai_bot?start=USER_ID
    """
    parts = text.split(maxsplit=1)
    payload = parts[1].strip() if len(parts) > 1 else ""

    # Try to extract user_id from deep-link payload
    linked_user_id = None
    if payload.isdigit():
        linked_user_id = int(payload)

    if linked_user_id:
        user = session.get(User, linked_user_id)
        if not user:
            tg.send_message(chat_id, "❌ User not found. Please register on the Udaan AI app first.")
            return

        # Upsert connection
        existing = session.exec(
            select(TelegramConnection).where(TelegramConnection.user_id == linked_user_id)
        ).first()
        if existing:
            existing.telegram_chat_id = chat_id
            existing.telegram_username = tg_username
            existing.is_active = True
            session.add(existing)
        else:
            conn = TelegramConnection(
                user_id=linked_user_id,
                telegram_chat_id=chat_id,
                telegram_username=tg_username,
                language=lang,
            )
            session.add(conn)
        session.commit()

        # Fetch name from profile
        uprof = session.exec(
            select(UserProfile).where(UserProfile.user_id == linked_user_id)
        ).first()
        name = uprof.full_name if uprof else "there"
        tg.send_message(chat_id, fmt.welcome(name, lang))
    else:
        # No payload → ask user to connect via app
        tg.send_message(
            chat_id,
            (
                "👋 <b>Welcome to UDAAN AI Bot!</b>\n\n"
                "To connect your account, please visit the Udaan AI dashboard and click "
                "<b>Connect Telegram</b> in the Telegram section.\n\n"
                "Or paste your User ID after /start:\n"
                "<code>/start 123</code>"
            )
        )


def _cmd_help(chat_id: str, lang: str):
    tg.send_message(chat_id, fmt.help_menu(lang))


def _cmd_profile(chat_id: str, user_id: Optional[int], session: Session, lang: str):
    if not user_id:
        tg.send_message(chat_id, "🔗 Please connect your account first. Use /start to begin.")
        return
    data = _get_backend_json(f"/dashboard/student/{user_id}", user_id) or \
           _get_backend_json(f"/dashboard/farmer/{user_id}", user_id)
    if data:
        tg.send_message(chat_id, fmt.profile_summary(data, lang))
    else:
        tg.send_message(chat_id, "⚠️ Could not fetch your profile. Please try again later.")


def _cmd_opportunities(chat_id: str, user_id: Optional[int], lang: str):
    if not user_id:
        tg.send_message(chat_id, "🔗 Please connect your account first.")
        return
    data = _get_backend_json("/wallet/opportunities", user_id)
    opps = (data or {}).get("opportunities", [])
    tg.send_message(chat_id, fmt.opportunities_list(opps, lang))


def _cmd_wallet(chat_id: str, user_id: Optional[int], lang: str):
    if not user_id:
        tg.send_message(chat_id, "🔗 Please connect your account first.")
        return
    data = _get_backend_json("/wallet/summary", user_id)
    if data:
        tg.send_message(chat_id, fmt.wallet_summary(data, lang))
    else:
        tg.send_message(chat_id, "⚠️ Could not fetch wallet data.")


def _cmd_documents(chat_id: str, user_id: Optional[int], lang: str):
    if not user_id:
        tg.send_message(chat_id, "🔗 Please connect your account first.")
        return
    data = _get_backend_json("/readiness", user_id)
    missing = (data or {}).get("missing_documents", [])
    tg.send_message(chat_id, fmt.documents_list(missing, lang))


def _cmd_readiness(chat_id: str, user_id: Optional[int], lang: str):
    if not user_id:
        tg.send_message(chat_id, "🔗 Please connect your account first.")
        return
    data = _get_backend_json("/readiness", user_id)
    if data:
        tg.send_message(chat_id, fmt.readiness_summary(data, lang))
    else:
        tg.send_message(chat_id, "⚠️ Could not fetch readiness data.")


def _cmd_value(chat_id: str, user_id: Optional[int], lang: str):
    if not user_id:
        tg.send_message(chat_id, "🔗 Please connect your account first.")
        return
    data = _get_backend_json("/value", user_id)
    if data:
        tg.send_message(chat_id, fmt.value_summary(data, lang))
    else:
        tg.send_message(chat_id, "⚠️ Could not fetch value data.")


def _cmd_deadlines(chat_id: str, user_id: Optional[int], lang: str):
    if not user_id:
        tg.send_message(chat_id, "🔗 Please connect your account first.")
        return
    data = _get_backend_json("/deadlines/upcoming", user_id)
    deadlines = (data or {}).get("deadlines", [])
    tg.send_message(chat_id, fmt.deadlines_list(deadlines, lang))


def _cmd_recovery(chat_id: str, user_id: Optional[int], lang: str):
    if not user_id:
        tg.send_message(chat_id, "🔗 Please connect your account first.")
        return
    data = _get_backend_json("/readiness", user_id)
    missing = (data or {}).get("missing_documents", [])
    if not missing:
        tg.send_message(chat_id, "✅ No blocked opportunities. Your profile looks complete!")
        return
    # For each missing doc, show a recovery alert
    for doc in missing[:3]:
        text, keyboard = fmt.doc_recovery_alert(doc, unlocks=2, total_value=50000, lang=lang)
        tg.send_message(chat_id, text, reply_markup=keyboard)


def _cmd_coach_intro(chat_id: str, lang: str):
    msgs = {
        "en": (
            "🤖 <b>UDAAN AI Coach</b>\n\n"
            "I am your personal AI assistant. Ask me anything:\n"
            "• Which scholarships can I get?\n"
            "• How to apply for PM Kisan?\n"
            "• How to get Income Certificate?\n"
            "• What documents am I missing?\n"
            "• What is my readiness score?\n\n"
            "Just type your question in any language!"
        ),
        "hi": (
            "🤖 <b>UDAAN AI कोच</b>\n\n"
            "मैं आपका AI सहायक हूँ। मुझसे कुछ भी पूछें!\n"
            "बस अपना सवाल टाइप करें।"
        ),
        "te": (
            "🤖 <b>UDAAN AI కోచ్</b>\n\n"
            "నేను మీ AI సహాయకుడిని. ఏమైనా అడగండి!\n"
            "మీ భాషలో మీ ప్రశ్న టైప్ చేయండి."
        ),
    }
    tg.send_message(chat_id, msgs.get(lang, msgs["en"]))


def _cmd_free_chat(chat_id: str, text: str, user_id: Optional[int],
                   session: Session, lang: str):
    """Free-text AI conversation using Groq."""
    # Update language from detected script
    detected = detect_language(text)
    if detected != "en":
        lang = detected

    context = _build_user_context(user_id, session) if user_id else "No profile linked."
    reply = ask_ai_coach(text, context, lang)
    tg.send_message(chat_id, reply)


# ─────────────────────────────────────────────────────────────
# CALLBACK HANDLER (inline keyboard buttons)
# ─────────────────────────────────────────────────────────────

def _handle_callback(cb: dict, session: Session):
    chat_id = str(cb["message"]["chat"]["id"])
    data = cb.get("data", "")
    cb_id = cb["id"]

    conn = session.exec(
        select(TelegramConnection).where(TelegramConnection.telegram_chat_id == chat_id)
    ).first()
    lang = conn.language if conn else "en"
    user_id = conn.user_id if conn else None

    tg.answer_callback_query(cb_id)

    if data.startswith("howtoget_") or data.startswith("recover_"):
        doc_name = data.split("_", 1)[1].replace("_", " ")
        # Fetch from backend recovery guide endpoint
        try:
            r = requests.get(
                f"http://localhost:8000/api/v1/documents/{requests.utils.quote(doc_name)}/recovery-guide",
                timeout=10
            )
            if r.status_code == 200:
                guide = r.json()
                steps = guide.get("steps", [])
                steps_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps[:5]))
                link = guide.get("apply_link", "https://www.meeseva.gov.in/")
                text = (
                    f"📋 <b>How to Get: {doc_name}</b>\n\n"
                    f"{steps_text}\n\n"
                    f"<a href='{link}'>👉 Apply / Get Official Link</a>"
                )
                tg.send_message(chat_id, text)
                return
        except Exception:
            pass
        tg.send_message(
            chat_id,
            f"📋 <b>Getting {doc_name}</b>\n\n"
            "1. Visit your nearest government office or MeeSeva centre\n"
            "2. Carry Aadhaar card and a recent passport photo\n"
            "3. Apply online at meeseva.gov.in\n\n"
            "Use /coach for personalised step-by-step guidance."
        )

    elif data.startswith("details_"):
        opp_id = data.split("_", 1)[1]
        if user_id:
            opps_data = _get_backend_json("/wallet/opportunities", user_id)
            opps = (opps_data or {}).get("opportunities", [])
            opp = next((o for o in opps if str(o.get("id")) == opp_id), None)
            if opp:
                text = (
                    f"📌 <b>{opp.get('title', 'Opportunity')}</b>\n\n"
                    f"💰 Benefit: {opp.get('benefit', '—')}\n"
                    f"🎯 Match Score: {opp.get('eligibility_score', 0)}%\n"
                    f"✅ Approval Probability: {opp.get('approval_probability', 0)}%\n"
                    f"📅 Deadline: {opp.get('deadline', 'Open')}\n"
                    f"⚠️ Missing: {opp.get('missing_requirement', 'None')}\n\n"
                    f"<a href='{opp.get('apply_link', 'https://www.myscheme.gov.in/')}'>Apply Now ↗</a>"
                )
                tg.send_message(chat_id, text)
                return
        tg.send_message(chat_id, "Use /opportunities to see your full list.")


# ─────────────────────────────────────────────────────────────
# PUSH NOTIFICATION HELPERS (called by backend events)
# ─────────────────────────────────────────────────────────────

def push_opportunity_alert(chat_id: str, opp: dict, lang: str = "en"):
    text, keyboard = fmt.opportunity_alert(opp, lang)
    tg.send_message(chat_id, text, reply_markup=keyboard)


def push_deadline_alert(chat_id: str, deadline: dict, lang: str = "en"):
    text, keyboard = fmt.deadline_alert(deadline, lang)
    tg.send_message(chat_id, text, reply_markup=keyboard)


def push_doc_missing(chat_id: str, doc: str, blocked: int, value: float, lang: str = "en"):
    text, keyboard = fmt.doc_missing_alert(doc, blocked, value, lang)
    tg.send_message(chat_id, text, reply_markup=keyboard)


def push_doc_recovery(chat_id: str, doc: str, unlocks: int, value: float, lang: str = "en"):
    text, keyboard = fmt.doc_recovery_alert(doc, unlocks, value, lang)
    tg.send_message(chat_id, text, reply_markup=keyboard)


def push_approval(chat_id: str, scheme: str, benefit: str, lang: str = "en"):
    tg.send_message(chat_id, fmt.approval_alert(scheme, benefit, lang))


def push_status_update(chat_id: str, scheme: str, status: str, lang: str = "en"):
    tg.send_message(chat_id, fmt.status_alert(scheme, status, lang))


def push_value_unlock(chat_id: str, old_val: float, new_val: float, lang: str = "en"):
    tg.send_message(chat_id, fmt.value_unlock_alert(old_val, new_val, lang))
