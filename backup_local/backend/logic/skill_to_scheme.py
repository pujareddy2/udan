"""
T5 — Skill → Free Government Scheme Map
========================================
Maps a missing skill (as identified by the eligibility engine) to a free
government training scheme that can help the user acquire it.

Each entry in SKILL_TO_SCHEME is:
    skill_key -> (scheme_name, scheme_url)

free_fix(missing_skills) returns a list of dicts for skills that have a mapping:
    [{"skill": ..., "scheme": ..., "url": ...}, ...]

Usage:
    >>> from backend.logic.skill_to_scheme import free_fix
    >>> free_fix(["typing"])
    [{"skill": "typing", "scheme": "PMKVY typing/CSC certification", "url": "https://pmkvyofficial.org"}]
"""

from typing import List, Dict

# ---------------------------------------------------------------------------
# Master mapping: skill_key → (scheme_name, official_url)
# ---------------------------------------------------------------------------
SKILL_TO_SCHEME: Dict[str, tuple] = {
    # ── Core skills listed in the checklist ────────────────────────────────
    "typing": (
        "PMKVY typing/CSC certification (Pradhan Mantri Kaushal Vikas Yojana)",
        "https://pmkvyofficial.org"
    ),
    "quantitative_aptitude": (
        "NIELIT 'O' Level Course — quantitative aptitude & IT skills (free for SC/ST)",
        "https://nielit.gov.in/content/o-level"
    ),
    "spoken_english": (
        "British Council / IGNOU free Spoken English programme",
        "https://www.ignou.ac.in"
    ),
    "open_source": (
        "NASSCOM FutureSkills Prime — open source & digital skills (subsidised)",
        "https://futureskillsprime.in"
    ),
    "computer_basics": (
        "PMGDISHA — Pradhan Mantri Gramin Digital Saksharta Abhiyan (free, rural focus)",
        "https://www.pmgdisha.in"
    ),

    # ── Additional skills common in the job-seeker context ─────────────────
    "ms_office": (
        "PMKVY — IT-ITES Sector Skill Council Office tools course (free certification)",
        "https://pmkvyofficial.org"
    ),
    "tally": (
        "PMKVY — Accounts Executive using Tally course (BFSI sector, free)",
        "https://pmkvyofficial.org"
    ),
    "data_entry": (
        "PMKVY — Data Entry Operator course (IT-ITES sector, free certification)",
        "https://pmkvyofficial.org"
    ),
    "communication": (
        "IGNOU Certificate in Business Communication (affordable distance learning)",
        "https://www.ignou.ac.in"
    ),
    "digital_literacy": (
        "PMGDISHA — free digital literacy for rural citizens",
        "https://www.pmgdisha.in"
    ),
    "coding": (
        "NASSCOM FutureSkills Prime — coding & software development (subsidised)",
        "https://futureskillsprime.in"
    ),
    "stitching": (
        "PMKVY — Apparel / Sewing Machine Operator course (free, women-focused)",
        "https://pmkvyofficial.org"
    ),
    "driving": (
        "PMKVY — Driver cum Mechanic / Commercial Vehicle Driver (free training)",
        "https://pmkvyofficial.org"
    ),
    "electrician": (
        "ITI Electrician Trade — Government ITI (free/subsidised for SC/ST/OBC)",
        "https://dget.nic.in"
    ),
    "plumbing": (
        "PMKVY — Plumber course (Construction sector, free certification)",
        "https://pmkvyofficial.org"
    ),
    "retail": (
        "PMKVY — Retail Trainee Associate course (free, entry-level)",
        "https://pmkvyofficial.org"
    ),
    "banking_finance": (
        "PMKVY — BFSI sector training (Banking, Financial Services & Insurance, free)",
        "https://pmkvyofficial.org"
    ),
    "gst": (
        "NACIN — National Academy of Customs, Indirect Taxes & Narcotics free e-learning",
        "https://nacin.gov.in"
    ),
    "agriculture": (
        "ATMA scheme — free agricultural skill training for farmers via Krishi Vigyan Kendra",
        "https://extensionreforms.dacnet.nic.in"
    ),
    "healthcare_basics": (
        "PMKVY — Healthcare Sector Skill Council courses (General Duty Assistant etc., free)",
        "https://pmkvyofficial.org"
    ),
    "beauty_wellness": (
        "PMKVY — Beauty Wellness Sector (Makeup Artist / Salon Manager, free for women)",
        "https://pmkvyofficial.org"
    ),
    "tailoring": (
        "PMKVY — Dress Designer / Fashion Designer course (free, women-focused)",
        "https://pmkvyofficial.org"
    ),
    "kondapalli_toys": (
        "Craft Development Institute / TSIDC — Kondapalli toy-making skill training (Telangana)",
        "https://www.tsidc.telangana.gov.in"
    ),
}

# ---------------------------------------------------------------------------
# free_fix — public function
# ---------------------------------------------------------------------------

def free_fix(missing_skills: List[str]) -> List[Dict[str, str]]:
    """
    Given a list of missing skills (strings), returns a list of free government
    scheme recommendations for each skill that has a known mapping.

    Args:
        missing_skills: list of skill keys (e.g. ["typing", "spoken_english"])

    Returns:
        list of dicts: [{"skill": ..., "scheme": ..., "url": ...}]
        Only skills present in SKILL_TO_SCHEME are included; unknown skills are skipped.

    Examples:
        >>> free_fix(["typing"])
        [{"skill": "typing",
          "scheme": "PMKVY typing/CSC certification ...",
          "url": "https://pmkvyofficial.org"}]

        >>> free_fix(["typing", "spoken_english", "unknown_skill"])
        # returns 2 entries (unknown_skill is silently skipped)
    """
    results = []
    for skill in missing_skills:
        # Normalise: lowercase, replace spaces/hyphens with underscores
        key = skill.strip().lower().replace(" ", "_").replace("-", "_")
        if key in SKILL_TO_SCHEME:
            scheme_name, url = SKILL_TO_SCHEME[key]
            results.append({
                "skill": skill,
                "scheme": scheme_name,
                "url": url,
            })
    return results
