from typing import List, Dict

SKILL_TO_SCHEME = {
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
    "ms_office": (
        "PMKVY — IT-ITES Sector Skill Council Office tools course (free certification)",
        "https://pmkvyofficial.org"
    ),
    "tally": (
        "PMKVY — Accounts Executive using Tally course (BFSI sector, free)",
        "https://pmkvyofficial.org"
    ),
    "data_entry": (
        "PMKVY — Data Entry Operator course (IT-ITES sector, free)",
        "https://pmkvyofficial.org"
    ),
    "stitching": (
        "PMKVY — Apparel / Sewing Machine Operator (free, women-focused)",
        "https://pmkvyofficial.org"
    ),
    "driving": (
        "PMKVY — Driver cum Mechanic training",
        "https://pmkvyofficial.org"
    ),
    "electrician": (
        "ITI Electrician Trade — Government ITI (free/subsidised for SC/ST/OBC)",
        "https://dget.nic.in"
    )
}

def free_fix(missing_skills: List[str]) -> List[Dict[str, str]]:
    """
    Takes a list of missing skills, normalizes them, and returns matching free government schemes.
    """
    fixes = []
    
    for skill in missing_skills:
        # Normalize: lowercase and replace spaces/hyphens with underscores
        normalized_skill = skill.lower().replace(" ", "_").replace("-", "_")
        
        if normalized_skill in SKILL_TO_SCHEME:
            scheme_name, url = SKILL_TO_SCHEME[normalized_skill]
            fixes.append({
                "skill": skill, # Preserve original casing for display
                "scheme": scheme_name,
                "url": url
            })
            
    return fixes
