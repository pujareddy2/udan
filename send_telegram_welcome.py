"""
UDAAN AI — Quick Telegram Account Linker
=========================================
Sends a welcome notification to any user after they message the bot.
Run ONCE after starting run_telegram_bot.py and the student sends /start USER_ID.

This also sends an immediate opportunity notification as a demo.
"""
import sys, os, requests, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app.core.config import settings
from app.core.db import get_session, init_db
from sqlmodel import Session, select
from app.models.domain import User, UserProfile
from app.models.telegram_db import TelegramConnection
from app.services.telegram_service import TelegramAPI, UdaanTelegramFormatter
from app.services.telegram_bot import push_opportunity_alert, push_deadline_alert, push_doc_missing

BASE_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"

def get_chat_id_for_user(user_id: int) -> str | None:
    """Get the Telegram chat_id linked to this user from DB."""
    init_db()
    session_gen = get_session()
    session = next(session_gen)
    conn = session.exec(
        select(TelegramConnection).where(TelegramConnection.user_id == user_id)
    ).first()
    try:
        next(session_gen)
    except StopIteration:
        pass
    return conn.telegram_chat_id if conn else None

def send_student_welcome_packet(user_id: int):
    """Send a full welcome + opportunity burst to the student."""
    tg = TelegramAPI()
    fmt = UdaanTelegramFormatter()

    init_db()
    session_gen = get_session()
    session = next(session_gen)

    user = session.get(User, user_id)
    uprof = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()

    if not user:
        print(f"[ERROR] User {user_id} not found")
        return

    conn = session.exec(
        select(TelegramConnection).where(TelegramConnection.user_id == user_id)
    ).first()

    if not conn:
        print(f"[ERROR] No Telegram connection for user {user_id}. Ask them to message the bot first.")
        print(f"        Ask student to open: https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={user_id}")
        return

    chat_id = conn.telegram_chat_id
    name = uprof.full_name if uprof else "Student"
    lang = conn.language or "en"
    role = user.module_type or "student"

    print(f"[SENDING] Messages to {name} (user_id={user_id}, chat_id={chat_id})")

    # 1. Welcome message
    tg.send_message(chat_id, fmt.welcome(name, lang))
    time.sleep(1)

    # 2. Profile summary
    profile_data = {
        "user_name": name,
        "profile_completion": 85,
        "readiness_score": 78,
        "eligible_opportunities": 12,
        "potential_value": 240000
    }
    tg.send_message(chat_id, fmt.profile_summary(profile_data, lang))
    time.sleep(1)

    # 3. New scholarship opportunity alert
    push_opportunity_alert(chat_id, {
        "id": "nsp_2024",
        "title": "National Scholarship Portal — NSP 2024-25",
        "benefit": "₹50,000/year",
        "eligibility_score": 92,
        "deadline": "31 July 2025",
        "apply_link": "https://scholarships.gov.in"
    }, lang)
    time.sleep(1)

    # 4. State scholarship
    push_opportunity_alert(chat_id, {
        "id": "ts_epass",
        "title": "Telangana ePASS Scholarship",
        "benefit": "₹75,000/year",
        "eligibility_score": 88,
        "deadline": "15 August 2025",
        "apply_link": "https://telanganaepass.cgg.gov.in"
    }, lang)
    time.sleep(1)

    # 5. Deadline alert
    push_deadline_alert(chat_id, {
        "scheme": "PM Yasasvi Scholarship",
        "days_remaining": 7,
        "value": 125000,
        "link": "https://yet.nta.ac.in"
    }, lang)
    time.sleep(1)

    # 6. Missing document alert
    push_doc_missing(chat_id, "Income Certificate", blocked_count=4, locked_value=150000, lang=lang)
    time.sleep(1)

    print(f"[DONE] Sent 6 personalized messages to {name}!")
    print(f"[TIP]  Student can now use: /opportunities /readiness /wallet /documents /coach")
    try:
        next(session_gen)
    except StopIteration:
        pass


if __name__ == "__main__":
    # Default to user 14 (puja5@gmail.com, phone 9121290915)
    user_id = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    print(f"[UDAAN] Sending Telegram welcome packet to user_id={user_id}")
    print(f"[STEP 1] Make sure the student has messaged the bot first:")
    print(f"         https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={user_id}")
    print()
    send_student_welcome_packet(user_id)
