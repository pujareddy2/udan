"""
T6 — Missed-Opportunity Detector & Alert Center
=================================================
Two functions:

1. missed(profile, opportunities, check_eligibility) → list
   - Finds opportunities the user *could have* claimed but missed.
   - Criteria: is_active == False  AND  check_eligibility(profile, opp)['verdict'] == 'eligible'
   - This is the emotional "regret hook" in the demo beat.

2. alerts(profile, opportunities, within_days=30) → list
   - Finds *active* opportunities whose close_date is within `within_days` from today.
   - Returns [{title, close_date, days_left, message}]
   - In-app alerts only — no Telegram, no email.

Both functions are pure / side-effect-free so they are easy to unit-test.

Opportunity dict shape (matches data/jobseekers.csv columns):
    {
        "title":          str,
        "is_active":      bool | "true"/"false" (normalised internally),
        "close_date":     str "YYYY-MM-DD" or None/"" if no deadline,
        ...  # any extra keys are ignored
    }

check_eligibility signature expected:
    check_eligibility(profile: dict, opportunity: dict) -> {"verdict": str, ...}
    verdict values: "eligible" | "partial" | "not_eligible"
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Callable, Dict, List, Optional


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_active(opp: dict) -> bool:
    """Normalise is_active field — tolerates bool or string."""
    val = opp.get("is_active", True)
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() not in ("false", "0", "no", "inactive")


def _parse_date(date_str: Optional[str]) -> Optional[date]:
    """Parse YYYY-MM-DD string into a date object. Returns None on failure."""
    if not date_str or str(date_str).strip() in ("", "None", "nan"):
        return None
    try:
        return datetime.strptime(str(date_str).strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# missed() — regret hook
# ---------------------------------------------------------------------------

def missed(
    profile: dict,
    opportunities: List[dict],
    check_eligibility: Callable[[dict, dict], dict],
) -> List[dict]:
    """
    Returns a list of INACTIVE opportunities the user was/is eligible for.

    These represent opportunities they could have claimed but missed — the
    emotional "regret hook" in the demo: "You missed ₹X because of Y."

    Args:
        profile:           User profile dict (from parse_profile / profile_from_form).
        opportunities:     List of opportunity dicts loaded from data/*.csv.
        check_eligibility: Function(profile, opportunity) → {"verdict": str, ...}
                           (Puja's engine function).

    Returns:
        List of opportunity dicts (with eligibility result merged in as
        "_eligibility") where is_active is False AND verdict == "eligible".
    """
    missed_opps = []

    for opp in opportunities:
        # Only consider INACTIVE / past-deadline opportunities
        if _is_active(opp):
            continue

        try:
            eligibility = check_eligibility(profile, opp)
        except Exception:
            # If the engine raises for any reason, skip this opportunity
            continue

        if eligibility.get("verdict") == "eligible":
            entry = dict(opp)
            entry["_eligibility"] = eligibility
            missed_opps.append(entry)

    return missed_opps


# ---------------------------------------------------------------------------
# alerts() — deadline alert center
# ---------------------------------------------------------------------------

def alerts(
    profile: dict,
    opportunities: List[dict],
    within_days: int = 30,
) -> List[dict]:
    """
    Returns a list of ACTIVE opportunities whose close_date is within
    `within_days` days from today (inclusive).

    Each result is:
        {
            "title":      str,
            "close_date": "YYYY-MM-DD",
            "days_left":  int,
            "message":    str   # human-readable alert text
        }

    Opportunities without a close_date (open-ended) are skipped.
    Already-expired opportunities (close_date < today) are skipped.

    Args:
        profile:       User profile dict (not used for filtering here, but
                       available for future personalisation of the message).
        opportunities: List of opportunity dicts.
        within_days:   Alert window in days (default 30).

    Returns:
        List of alert dicts, sorted by days_left ascending (soonest first).
    """
    today = date.today()
    cutoff = today + timedelta(days=within_days)
    alert_list = []

    for opp in opportunities:
        # Only active opportunities
        if not _is_active(opp):
            continue

        close = _parse_date(opp.get("close_date"))
        if close is None:
            continue  # No deadline — skip

        # Skip already expired
        if close < today:
            continue

        # Within the alert window?
        if close <= cutoff:
            days_left = (close - today).days
            title = opp.get("title", "Opportunity")

            if days_left == 0:
                urgency = "closing TODAY"
            elif days_left == 1:
                urgency = "closing TOMORROW"
            else:
                urgency = f"closing in {days_left} days"

            message = (
                f"⚠️ '{title}' is {urgency} ({close.strftime('%d %b %Y')}). "
                f"Don't miss it — apply now!"
            )

            alert_list.append({
                "title":      title,
                "close_date": close.isoformat(),
                "days_left":  days_left,
                "message":    message,
            })

    # Sort: soonest deadline first
    alert_list.sort(key=lambda a: a["days_left"])
    return alert_list
