"""
Telegram Service — UDAAN AI
============================
Handles all communication with the Telegram Bot API.

Responsibilities:
  - Send any message to a chat_id
  - Format all alert types (opportunity, deadline, document, approval, etc.)
  - Multilingual message generation (EN / HI / TE)
  - Pull live personalised data from existing UDAAN engines
"""

import requests
import json
from typing import Optional, Dict, Any, List
from app.core.config import settings


# ─────────────────────────────────────────────────────────────
# TELEGRAM API WRAPPER
# ─────────────────────────────────────────────────────────────

class TelegramAPI:
    """Thin wrapper around the Telegram Bot API."""

    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.parse_mode = settings.TELEGRAM_PARSE_MODE or "HTML"

    def _post(self, method: str, payload: dict) -> dict:
        if not self.token:
            return {"ok": False, "error": "TELEGRAM_BOT_TOKEN not configured"}
        url = f"{self.base_url}/{method}"
        try:
            r = requests.post(url, json=payload, timeout=10)
            return r.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def send_message(self, chat_id: str, text: str,
                     reply_markup: Optional[dict] = None,
                     parse_mode: Optional[str] = None) -> dict:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode or self.parse_mode,
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self._post("sendMessage", payload)

    def answer_callback_query(self, callback_query_id: str, text: str = "") -> dict:
        return self._post("answerCallbackQuery", {
            "callback_query_id": callback_query_id,
            "text": text
        })

    def set_webhook(self, url: str) -> dict:
        return self._post("setWebhook", {"url": url})

    def delete_webhook(self) -> dict:
        return self._post("deleteWebhook", {})

    def get_updates(self, offset: int = 0) -> dict:
        return self._post("getUpdates", {"offset": offset, "timeout": 30})


# ─────────────────────────────────────────────────────────────
# MULTILINGUAL STRING HELPERS
# ─────────────────────────────────────────────────────────────

_LANG = {
    "greeting": {
        "en": "Hello",
        "hi": "नमस्ते",
        "te": "నమస్కారం",
    },
    "no_profile": {
        "en": "⚠️ Please complete your profile on the Udaan AI app first.",
        "hi": "⚠️ कृपया पहले Udaan AI ऐप पर अपना प्रोफ़ाइल पूरा करें।",
        "te": "⚠️ దయచేసి ముందుగా Udaan AI యాప్‌లో మీ ప్రొఫైల్ పూర్తి చేయండి.",
    },
    "connected": {
        "en": "✅ Your Telegram account is now connected to Udaan AI!",
        "hi": "✅ आपका Telegram खाता Udaan AI से जुड़ गया है!",
        "te": "✅ మీ Telegram ఖాతా Udaan AI తో అనుసంధానించబడింది!",
    },
}

def _t(key: str, lang: str) -> str:
    return _LANG.get(key, {}).get(lang, _LANG.get(key, {}).get("en", key))


# ─────────────────────────────────────────────────────────────
# DETECT LANGUAGE FROM MESSAGE TEXT
# ─────────────────────────────────────────────────────────────

def detect_language(text: str) -> str:
    """
    Heuristic language detector.
    Returns "te" for Telugu, "hi" for Hindi, "en" otherwise.
    """
    if not text:
        return "en"
    te_chars = range(0x0C00, 0x0C7F)  # Telugu Unicode block
    hi_chars = range(0x0900, 0x097F)  # Devanagari block
    te_count = sum(1 for c in text if ord(c) in te_chars)
    hi_count = sum(1 for c in text if ord(c) in hi_chars)
    if te_count > 2:
        return "te"
    if hi_count > 2:
        return "hi"
    return "en"


# ─────────────────────────────────────────────────────────────
# ALERT FORMATTERS
# ─────────────────────────────────────────────────────────────

class UdaanTelegramFormatter:
    """
    Converts engine data into beautifully formatted Telegram HTML messages.
    Every formatter returns (text, optional_inline_keyboard).
    """

    @staticmethod
    def welcome(user_name: str, lang: str = "en") -> str:
        lines = {
            "en": (
                f"🚀 <b>Welcome to UDAAN AI, {user_name}!</b>\n\n"
                "I am your personal Opportunity Assistant. I will help you:\n"
                "• 🎓 Discover scholarships, schemes & jobs you qualify for\n"
                "• 📄 Track missing documents\n"
                "• ⏰ Alert you before deadlines\n"
                "• 💰 Unlock hidden financial value\n\n"
                "Type /help to see all commands."
            ),
            "hi": (
                f"🚀 <b>Udaan AI में आपका स्वागत है, {user_name}!</b>\n\n"
                "मैं आपका व्यक्तिगत अवसर सहायक हूँ।\n"
                "• 🎓 योजनाएँ और छात्रवृत्तियाँ खोजें\n"
                "• 📄 गुम दस्तावेज़ ट्रैक करें\n"
                "• ⏰ समय सीमा से पहले अलर्ट पाएं\n\n"
                "/help टाइप करें।"
            ),
            "te": (
                f"🚀 <b>Udaan AI లో స్వాగతం, {user_name}!</b>\n\n"
                "నేను మీ వ్యక్తిగత అవకాశ సహాయకుడిని.\n"
                "• 🎓 మీకు అర్హమైన పథకాలు కనుగొనండి\n"
                "• 📄 పత్రాలు ట్రాక్ చేయండి\n"
                "• ⏰ గడువుకు ముందు హెచ్చరికలు పొందండి\n\n"
                "/help అని టైప్ చేయండి."
            ),
        }
        return lines.get(lang, lines["en"])

    @staticmethod
    def help_menu(lang: str = "en") -> str:
        lines = {
            "en": (
                "📋 <b>UDAAN AI Commands</b>\n\n"
                "/profile — Your profile summary\n"
                "/opportunities — Matched opportunities\n"
                "/wallet — Opportunity wallet status\n"
                "/documents — Missing documents\n"
                "/readiness — Readiness score\n"
                "/value — Financial value summary\n"
                "/deadlines — Upcoming deadlines\n"
                "/recovery — Unlock blocked opportunities\n"
                "/coach — Ask AI anything\n"
                "/help — Show this menu"
            ),
            "hi": (
                "📋 <b>UDAAN AI कमांड</b>\n\n"
                "/profile — प्रोफ़ाइल सारांश\n"
                "/opportunities — मिलान अवसर\n"
                "/wallet — वॉलेट स्थिति\n"
                "/documents — गुम दस्तावेज़\n"
                "/readiness — तत्परता स्कोर\n"
                "/value — वित्तीय मूल्य\n"
                "/deadlines — आगामी समय सीमाएँ\n"
                "/recovery — अवरुद्ध अवसर अनलॉक करें\n"
                "/coach — AI से पूछें"
            ),
            "te": (
                "📋 <b>UDAAN AI కమాండ్‌లు</b>\n\n"
                "/profile — ప్రొఫైల్ సారాంశం\n"
                "/opportunities — మ్యాచ్ అయిన అవకాశాలు\n"
                "/wallet — వాలెట్ స్థితి\n"
                "/documents — మిస్సింగ్ డాక్యుమెంట్లు\n"
                "/readiness — రెడీనెస్ స్కోరు\n"
                "/value — ఆర్థిక విలువ\n"
                "/deadlines — రాబోయే గడువులు\n"
                "/recovery — బ్లాక్ అయిన అవకాశాలు అన్‌లాక్ చేయండి\n"
                "/coach — AI తో మాట్లాడండి"
            ),
        }
        return lines.get(lang, lines["en"])

    @staticmethod
    def profile_summary(profile: Dict[str, Any], lang: str = "en") -> str:
        name = profile.get("user_name") or profile.get("farmer_name") or "User"
        completion = profile.get("profile_completion", 0)
        readiness = profile.get("readiness_score", 0)
        eligible = profile.get("eligible_opportunities", 0)
        value = profile.get("potential_value", 0)
        val_str = f"₹{int(value):,}" if value else "—"

        return (
            f"👤 <b>Profile Summary</b>\n\n"
            f"Name: <b>{name}</b>\n"
            f"Profile Completion: <b>{completion}%</b>\n"
            f"Readiness Score: <b>{readiness}%</b>\n"
            f"Eligible Opportunities: <b>{eligible}</b>\n"
            f"Potential Value: <b>{val_str}</b>"
        )

    @staticmethod
    def opportunity_alert(opp: Dict[str, Any], lang: str = "en") -> tuple:
        """New opportunity discovered. Returns (text, inline_keyboard)."""
        name = opp.get("title", "Unknown Opportunity")
        benefit = opp.get("benefit", "—")
        score = opp.get("eligibility_score", 0)
        deadline = opp.get("deadline", "Open")
        link = opp.get("apply_link", "https://www.myscheme.gov.in/")

        text = (
            f"🎉 <b>New Opportunity Found!</b>\n\n"
            f"📌 <b>{name}</b>\n\n"
            f"💰 Benefit: <b>{benefit}</b>\n"
            f"🎯 Match Score: <b>{score}%</b>\n"
            f"📅 Deadline: <b>{deadline}</b>\n\n"
            f"<a href='{link}'>👉 Apply on Official Portal</a>"
        )
        keyboard = {
            "inline_keyboard": [[
                {"text": "📋 DETAILS", "callback_data": f"details_{opp.get('id', 'opp')}"},
                {"text": "✅ Apply Now", "url": link}
            ]]
        }
        return text, keyboard

    @staticmethod
    def deadline_alert(deadline: Dict[str, Any], lang: str = "en") -> tuple:
        scheme = deadline.get("scheme", "—")
        days = deadline.get("days_remaining", 0)
        value = deadline.get("value", 0)
        link = deadline.get("link", "https://www.myscheme.gov.in/")
        val_str = f"₹{int(value):,}" if value else ""

        emoji = "🚨" if days <= 1 else ("⚠️" if days <= 3 else "📅")
        urgency = "TODAY" if days <= 1 else f"{days} Days Left"

        text = (
            f"{emoji} <b>Deadline Alert!</b>\n\n"
            f"📌 <b>{scheme}</b>\n\n"
            f"⏰ Time Remaining: <b>{urgency}</b>\n"
        )
        if val_str:
            text += f"💰 Potential Value: <b>{val_str}</b>\n"
        text += f"\n<a href='{link}'>👉 Apply Now</a>"

        keyboard = {
            "inline_keyboard": [[
                {"text": "✅ Apply Now", "url": link}
            ]]
        }
        return text, keyboard

    @staticmethod
    def doc_missing_alert(doc: str, blocked_count: int, locked_value: float, lang: str = "en") -> tuple:
        val_str = f"₹{int(locked_value):,}" if locked_value else "multiple opportunities"
        text = (
            f"📄 <b>Missing Document Alert</b>\n\n"
            f"Document: <b>{doc}</b>\n\n"
            f"Without this document:\n"
            f"• <b>{blocked_count}</b> opportunities remain blocked\n"
            f"• Potential Value Locked: <b>{val_str}</b>\n\n"
            f"Reply with /coach to get step-by-step recovery instructions."
        )
        keyboard = {
            "inline_keyboard": [[
                {"text": "📋 HOW TO GET", "callback_data": f"howtoget_{doc.replace(' ', '_')}"}
            ]]
        }
        return text, keyboard

    @staticmethod
    def doc_recovery_alert(doc: str, unlocks: int, total_value: float, lang: str = "en") -> tuple:
        val_str = f"₹{int(total_value):,}" if total_value else "significant value"
        text = (
            f"🔓 <b>Opportunity Unlock Available!</b>\n\n"
            f"<b>{doc}</b> can unlock:\n"
            f"• <b>{unlocks}</b> blocked opportunities\n"
            f"• Total Value: <b>{val_str}</b>\n\n"
            f"Get this document and claim what is yours!"
        )
        keyboard = {
            "inline_keyboard": [[
                {"text": "🔄 RECOVER", "callback_data": f"recover_{doc.replace(' ', '_')}"}
            ]]
        }
        return text, keyboard

    @staticmethod
    def approval_alert(scheme: str, benefit: str, lang: str = "en") -> str:
        return (
            f"🎉 <b>Congratulations!</b>\n\n"
            f"✅ <b>Application Approved</b>\n\n"
            f"Scheme: <b>{scheme}</b>\n"
            f"Benefit: <b>{benefit}</b>\n\n"
            f"Your hard work paid off! Check your application portal for disbursement details."
        )

    @staticmethod
    def status_alert(scheme: str, status: str, lang: str = "en") -> str:
        emoji = {"Under Review": "🔍", "Selected": "🏆", "Rejected": "❌"}.get(status, "📢")
        return (
            f"{emoji} <b>Application Update</b>\n\n"
            f"Scheme: <b>{scheme}</b>\n"
            f"Status: <b>{status}</b>\n\n"
            f"Use /wallet to track all your applications."
        )

    @staticmethod
    def value_unlock_alert(old_value: float, new_value: float, lang: str = "en") -> str:
        old_str = f"₹{int(old_value):,}"
        new_str = f"₹{int(new_value):,}"
        return (
            f"💰 <b>New Value Unlocked!</b>\n\n"
            f"Your Potential Opportunity Value just increased:\n\n"
            f"{old_str} → <b>{new_str}</b>\n\n"
            f"Use /opportunities to see new matches."
        )

    @staticmethod
    def wallet_summary(wallet: Dict[str, Any], lang: str = "en") -> str:
        ready = wallet.get("ready", 0)
        blocked = wallet.get("blocked", 0)
        applied = wallet.get("applied", 0)
        review = wallet.get("under_review", 0)
        won = wallet.get("approved", wallet.get("won", 0))
        return (
            f"💼 <b>Opportunity Wallet</b>\n\n"
            f"✅ Ready to Apply: <b>{ready}</b>\n"
            f"🔴 Blocked: <b>{blocked}</b>\n"
            f"📬 Applied: <b>{applied}</b>\n"
            f"🔍 Under Review: <b>{review}</b>\n"
            f"🏆 Won/Selected: <b>{won}</b>\n\n"
            f"Use /opportunities to see details."
        )

    @staticmethod
    def opportunities_list(opps: List[Dict[str, Any]], lang: str = "en") -> str:
        if not opps:
            return "❌ No matched opportunities yet. Complete your profile to unlock them."
        lines = ["🎯 <b>Your Matched Opportunities</b>\n"]
        for i, op in enumerate(opps[:6], 1):
            score = op.get("eligibility_score", op.get("match_score", 0))
            prob = op.get("approval_probability", 0)
            deadline = op.get("deadline", "Open")
            missing = op.get("missing_requirement", "")
            status = "⚠️ Missing docs" if (missing and missing != "None") else "✅ Ready"
            lines.append(
                f"{i}. <b>{op.get('title', op.get('name', 'Opportunity'))}</b>\n"
                f"   💰 {op.get('benefit', '—')} | 🎯 Match: {score}% | 📅 {deadline}\n"
                f"   {status}"
            )
        return "\n\n".join(lines)

    @staticmethod
    def readiness_summary(readi: Dict[str, Any], lang: str = "en") -> str:
        score = readi.get("overall_score", readi.get("overall_readiness", 0))
        profile = readi.get("profile_readiness", readi.get("breakdown", {}).get("profile", 0))
        docs = readi.get("document_readiness", readi.get("breakdown", {}).get("documents", 0))
        academic = readi.get("academic_readiness", readi.get("breakdown", {}).get("academic", 0))
        skills = readi.get("skills_readiness", readi.get("breakdown", {}).get("skills", 0))
        missing = readi.get("missing_documents", [])

        text = (
            f"📊 <b>Readiness Report</b>\n\n"
            f"Overall Score: <b>{score}%</b>\n\n"
            f"Profile: {profile}%\n"
            f"Documents: {docs}%\n"
        )
        if academic:
            text += f"Academic: {academic}%\n"
        if skills:
            text += f"Skills: {skills}%\n"
        if missing:
            text += f"\n📄 Missing: {', '.join(missing[:3])}"
        return text

    @staticmethod
    def documents_list(missing: List[str], lang: str = "en") -> str:
        if not missing:
            return "✅ All required documents are in order!"
        lines = ["📄 <b>Missing Documents</b>\n"]
        for doc in missing:
            lines.append(f"❌ {doc}")
        lines.append("\nUse /coach to get step-by-step instructions for each document.")
        return "\n".join(lines)

    @staticmethod
    def value_summary(val: Dict[str, Any], lang: str = "en") -> str:
        def fmt(v): return f"₹{int(v):,}" if v else "—"
        return (
            f"💰 <b>Financial Value Summary</b>\n\n"
            f"✅ Eligible Value: <b>{fmt(val.get('eligible_value'))}</b>\n"
            f"⭐ Potential Value: <b>{fmt(val.get('potential_value'))}</b>\n"
            f"🔴 Blocked Value: <b>{fmt(val.get('blocked_value'))}</b>\n"
            f"🔓 Recovery Value: <b>{fmt(val.get('recovery_value'))}</b>\n\n"
            f"Use /documents to unlock blocked value."
        )

    @staticmethod
    def deadlines_list(deadlines: List[Dict[str, Any]], lang: str = "en") -> str:
        if not deadlines:
            return "✅ No urgent deadlines right now."
        lines = ["⏰ <b>Upcoming Deadlines</b>\n"]
        for d in deadlines[:5]:
            days = d.get("days_remaining", d.get("days", "?"))
            scheme = d.get("scheme", d.get("name", "Opportunity"))
            emoji = "🚨" if (isinstance(days, int) and days <= 3) else "⚠️"
            lines.append(f"{emoji} <b>{scheme}</b> — {days} days left")
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# GROQ-POWERED AI CHAT
# ─────────────────────────────────────────────────────────────

def ask_ai_coach(user_message: str, user_context: str, lang: str = "en") -> str:
    """
    Call Groq LLM to answer user query in Telegram text mode.
    Uses the same Groq key as voice_agent.
    """
    system_prompt = (
        f"You are the UDAAN AI Telegram Bot — a personalized opportunity assistant for Indian citizens.\n"
        f"The user speaks in language code: {lang}. Reply ONLY in that language.\n"
        f"Keep replies concise (under 200 words). Use plain text, no markdown.\n"
        f"Focus on: government schemes, eligibility, missing documents, application steps.\n"
        f"Do NOT give generic advice. Use the user profile context below.\n\n"
        f"User Context:\n{user_context}"
    )
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "max_tokens": 300,
            },
            timeout=15,
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        pass

    # Fallback
    fallback = {
        "en": "I can help you find eligible schemes, missing documents, and application steps. What would you like to know?",
        "hi": "मैं आपको पात्र योजनाओं, गुम दस्तावेज़ों और आवेदन चरणों में मदद कर सकता हूँ।",
        "te": "నేను మీకు అర్హమైన పథకాలు, తప్పిపోయిన పత్రాలు మరియు దరఖాస్తు దశలలో సహాయం చేయగలను.",
    }
    return fallback.get(lang, fallback["en"])
