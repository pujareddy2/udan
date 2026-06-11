from typing import Dict, Any, List, Tuple
from app.models.domain import (
    StudentProfile, FarmerProfile, JobSeekerProfile, 
    EntrepreneurProfile, WomenEntrepreneurProfile, 
    StartupProfile, SeniorCitizenProfile
)

def get_profile_status(percentage: int) -> str:
    if percentage <= 25: return "Incomplete"
    elif percentage <= 50: return "Basic Profile"
    elif percentage <= 75: return "Good Profile"
    elif percentage <= 90: return "Strong Profile"
    else: return "Opportunity Ready"

def analyze_profile(profile: Any, role: str) -> Dict[str, Any]:
    """
    Returns completion percentage, missing fields, and dynamic follow-up questions
    based on the specific role profile.
    """
    if not profile:
        return {
            "completion_percentage": 0,
            "status": "Incomplete",
            "missing_fields": [], # Handled by the router to specify everything is missing
            "followup_questions": []
        }
        
    profile_dict = profile.dict(exclude={"id", "user_id", "created_at"})
    total_fields = len(profile_dict)
    filled_fields = sum(1 for v in profile_dict.values() if v is not None and v != "")
    
    completion_percentage = int((filled_fields / total_fields) * 100) if total_fields > 0 else 0
    missing_fields = [k for k, v in profile_dict.items() if v is None or v == ""]
    
    followup_questions = generate_followup_questions(profile, role)
    
    return {
        "completion_percentage": completion_percentage,
        "status": get_profile_status(completion_percentage),
        "missing_fields": missing_fields,
        "followup_questions": followup_questions
    }

def generate_followup_questions(profile: Any, role: str) -> List[str]:
    questions = []
    
    if role == "student":
        if getattr(profile, "cgpa", None) is not None:
            questions.append("Do you have any backlogs?")
        if getattr(profile, "current_course", None) is not None:
            questions.append("Have you completed internships?")
            questions.append("Have you published any research?")
        if getattr(profile, "education_level", "") == "UG":
            questions.append("Have you appeared for GATE?")
            
    elif role == "farmer":
        if getattr(profile, "land_size_acres", None) is not None:
            questions.append("Is the land formally registered in your name?")
            questions.append("Do you use modern irrigation systems?")
        if getattr(profile, "pm_kisan_id", None) is None:
            questions.append("Would you like help applying for a PM-Kisan ID?")
            
    elif role == "jobseeker":
        if getattr(profile, "qualification", None) is not None:
            questions.append("Are you currently unemployed?")
            questions.append("Do you have any professional certifications?")
        if getattr(profile, "preferred_job_role", None) is not None:
            questions.append("Are you willing to relocate?")
            questions.append("Are you primarily targeting Government jobs or Private sector?")
            
    elif role == "entrepreneur":
        if getattr(profile, "business_type", None) is not None:
            questions.append("Is your business GST Registered?")
        if getattr(profile, "msme_udyam_number", None) is None:
            questions.append("Do you need assistance getting UDYAM registered?")
            
    elif role == "women_entrepreneur":
        if getattr(profile, "percentage_women_ownership", 0) > 0:
            questions.append("Are you a member of a Self Help Group (SHG)?")
            
    elif role == "startup":
        if getattr(profile, "funding_stage", None) is not None:
            questions.append("Have you generated revenue yet?")
            questions.append("Is your MVP available?")
        if getattr(profile, "dpiit_recognized", False):
            questions.append("Have you joined any government-recognized incubators?")
            
    elif role == "senior_citizen":
        if getattr(profile, "pension_status", None) == "Not Receiving":
            questions.append("Are you looking to apply for Widow or Old Age Pension?")
        if getattr(profile, "is_disabled", False):
            questions.append("Do you have an official Disability Certificate?")

    return questions
