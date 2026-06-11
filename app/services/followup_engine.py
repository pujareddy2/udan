from typing import Dict, Any, List

# Follow-Up Question Database mapped exactly from the architecture blueprint
FOLLOWUP_DB = {
    "backlogs": {
        "question": "Do you currently have any backlogs?",
        "field_name": "backlogs",
        "importance": "critical",
        "confidence_gain": 20,
        "reason": "Critical for Merit Scholarships which require clear academic records."
    },
    "cgpa": {
        "question": "What is your latest CGPA?",
        "field_name": "cgpa",
        "importance": "high_value",
        "confidence_gain": 15,
        "reason": "Acts as a threshold for High-Value academic grants."
    },
    "single_girl_child": {
        "question": "Are you a single girl child?",
        "field_name": "single_girl_child",
        "importance": "advanced",
        "confidence_gain": 10,
        "reason": "Unlocks exclusive UGC schemes like Post-Graduate Indira Gandhi Scholarship."
    },
    "land_ownership_status": {
        "question": "Is the agricultural land registered strictly in your name?",
        "field_name": "land_ownership_status",
        "importance": "mandatory",
        "confidence_gain": 25,
        "reason": "Direct Benefit Transfers (PM-KISAN) require explicit land title verification."
    },
    "irrigation_type": {
        "question": "Do you have existing micro-irrigation facilities?",
        "field_name": "irrigation_type",
        "importance": "high_value",
        "confidence_gain": 15,
        "reason": "Unlocks PMKSY subsidy for advanced farming tools."
    },
    "unemployed_status": {
        "question": "Are you currently unemployed and registered on the NCS portal?",
        "field_name": "unemployed_status",
        "importance": "mandatory",
        "confidence_gain": 20,
        "reason": "Mandatory for state Unemployment Allowances."
    },
    "apprenticeship_status": {
        "question": "Have you completed any NATS/NAPS apprenticeship?",
        "field_name": "apprenticeship_status",
        "importance": "high_value",
        "confidence_gain": 15,
        "reason": "Unlocks advanced placements and skill grants."
    },
    "gst_registration": {
        "question": "Is your business GST registered?",
        "field_name": "gst_registration",
        "importance": "critical",
        "confidence_gain": 20,
        "reason": "Critical for formal sector enterprise benefits."
    },
    "women_ownership": {
        "question": "Do women own more than 51% of the enterprise?",
        "field_name": "women_ownership",
        "importance": "mandatory",
        "confidence_gain": 25,
        "reason": "Mandatory for Standup India and exclusive MSME women schemes."
    },
    "dpiit_recognized": {
        "question": "Is your startup officially DPIIT recognized?",
        "field_name": "dpiit_recognized",
        "importance": "mandatory",
        "confidence_gain": 25,
        "reason": "Mandatory for 80IAC Tax Exemption and IPR fast-tracking."
    },
    "working_mvp": {
        "question": "Do you have a working Minimum Viable Product (MVP)?",
        "field_name": "working_mvp",
        "importance": "high_value",
        "confidence_gain": 15,
        "reason": "Threshold for Seed Fund Scheme."
    },
    "receiving_pension": {
        "question": "Are you currently receiving any state or central pension?",
        "field_name": "receiving_pension",
        "importance": "critical",
        "confidence_gain": 20,
        "reason": "Filters mutually exclusive senior citizen schemes."
    },
    "pwd_status": {
        "question": "Do you possess a valid UDID/Disability certificate?",
        "field_name": "pwd_status",
        "importance": "high_value",
        "confidence_gain": 15,
        "reason": "Unlocks enhanced maintenance and specific disability pensions."
    }
}

def calculate_followup_readiness(unanswered_critical: int, unanswered_high_value: int, missing_verifications: int) -> float:
    """
    Calculates the Follow-up Readiness Score (Layer 4).
    """
    score = 100.0 - (unanswered_critical * 15) - (unanswered_high_value * 10) - (missing_verifications * 5)
    return max(0.0, score)

def generate_followup_questions(missing_fields: List[str], opps_unlocked_map: Dict[str, int], benefit_val_map: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Dynamically generates the follow-up questions for missing fields.
    """
    questions = []
    
    for field in missing_fields:
        if field in FOLLOWUP_DB:
            q_data = FOLLOWUP_DB[field]
            unlocked = opps_unlocked_map.get(field, 1)
            val = benefit_val_map.get(field, 0.0)
            
            questions.append({
                "question": q_data["question"],
                "field_name": q_data["field_name"],
                "importance": q_data["importance"],
                "confidence_gain": q_data["confidence_gain"],
                "opportunities_unlocked": unlocked,
                "estimated_benefit_value": val,
                "reason": q_data["reason"]
            })
            
    # Sort by importance and confidence gain
    def sort_key(q):
        val = 0
        if q["importance"] in ["mandatory", "critical"]: val = 100
        elif q["importance"] == "high_value": val = 50
        return val + q["confidence_gain"]
        
    questions.sort(key=sort_key, reverse=True)
    return questions
