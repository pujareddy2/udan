"""
UDAAN AI - Telegram Bot Polling Runner
=======================================
Run this script to start the bot in long-polling mode.
The bot will receive messages from Telegram and process them.

Usage: python run_telegram_bot.py
"""

import time
import sys
import os
import threading
import requests

# Force UTF-8 on Windows console (prevents emoji encoding crash)
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load env
from dotenv import load_dotenv
load_dotenv()

from app.core.config import settings
from app.core.db import get_session, init_db
from app.services.telegram_bot import handle_update

BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_updates(offset: int = 0) -> list:
    try:
        r = requests.get(
            f"{BASE_URL}/getUpdates",
            params={"offset": offset, "timeout": 30, "allowed_updates": ["message", "callback_query"]},
            timeout=40
        )
        data = r.json()
        if data.get("ok"):
            return data.get("result", [])
    except Exception as e:
        print(f"[POLL ERROR] {e}")
    return []

def delete_webhook():
    """Remove any existing webhook so polling works."""
    try:
        r = requests.post(f"{BASE_URL}/deleteWebhook", json={}, timeout=10)
        print(f"[WEBHOOK] Deleted: {r.json()}")
    except Exception as e:
        print(f"[WEBHOOK ERROR] {e}")

def get_bot_info():
    try:
        r = requests.get(f"{BASE_URL}/getMe", timeout=10)
        info = r.json()
        if info.get("ok"):
            bot = info["result"]
            print(f"[BOT] @{bot['username']} (id={bot['id']}) -- READY")
            return bot
        else:
            print(f"[BOT INFO FAIL] {info}")
    except Exception as e:
        print(f"[BOT INFO ERROR] {e}")
    return None


def poll_loop():
    offset = 0
    init_db()
    print("[UDAAN BOT] Starting polling loop...")
    while True:
        updates = get_updates(offset)
        for update in updates:
            update_id = update["update_id"]
            offset = update_id + 1
            try:
                # Each update gets its own DB session
                session_gen = get_session()
                session = next(session_gen)
                try:
                    handle_update(update, session)
                finally:
                    try:
                        next(session_gen)
                    except StopIteration:
                        pass
            except Exception as e:
                print(f"[UPDATE ERROR] {e}")
        if not updates:
            time.sleep(1)


if __name__ == "__main__":
    print("=" * 50)
    print("  UDAAN AI - Telegram Bot")
    print("=" * 50)

    if not BOT_TOKEN:
        print("[ERROR] TELEGRAM_BOT_TOKEN not set in .env")
        sys.exit(1)

    bot = get_bot_info()
    if not bot:
        print("[ERROR] Could not connect to Telegram. Check your bot token.")
        sys.exit(1)

    delete_webhook()
    print(f"\n[LINK] Share this link with students to connect their account:")
    print(f"       https://t.me/{bot['username']}?start=USER_ID")
    print(f"\n[LINK] Example for user 14 (puja5@gmail.com):")
    print(f"       https://t.me/{bot['username']}?start=14")
    print(f"\n[LISTENING] Waiting for messages...\n")
    poll_loop()
