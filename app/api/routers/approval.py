from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.core.db import get_session
from app.models.domain import UserProfile, FarmerProfile

router = APIRouter()

def _compute_scheme_approvals(farmer_profile, user_profile):
    """Compute approval probability for each eligible scheme based on profile."""
    docs = []
    if user_profile and user_profile.profile_data:
        docs = user_profile.profile_data.get("documents", [])

    has_aadhaar = any("aadhaar" in d.lower() for d in docs)
    has_land = bool(farmer_profile and farmer_profile.land_size_acres and farmer_profile.land_size_acres > 0)
    has_bank = any("bank" in d.lower() for d in docs)
    doc_count = len(docs)

    schemes = []

    # PM Kisan — universal for farmers
    kisan_score = 60
    if has_aadhaar: kisan_score += 20
    if has_land: kisan_score += 10
    if has_bank: kisan_score += 10
    schemes.append({
        "name": "PM Kisan Samman Nidhi",
        "tag": "Income",
        "score": min(100, kisan_score),
        "amount": "₹6,000/yr",
        "link": "https://pmkisan.gov.in/",
        "required_docs": ["Aadhaar Card", "Land Passbook", "Bank Passbook"],
        "how_to_apply": [
            "Visit pmkisan.gov.in or nearest CSC centre",
            "Click 'Farmer Corner' → 'New Farmer Registration'",
            "Enter Aadhaar number and state",
            "Fill in land and bank details",
            "Submit and note the registration number"
        ],
        "eligibility_reason": "You are a small/marginal farmer eligible for ₹6,000/yr direct income support.",
        "youtube_link": "https://www.youtube.com/watch?v=1kzY1v4ESQM"
    })

    # Rythu Bandhu — Telangana land owners
    if has_land and farmer_profile:
        rb_score = 80
        if has_aadhaar: rb_score += 10
        if has_bank: rb_score += 10
        benefit = int(farmer_profile.land_size_acres or 1) * 10000
        schemes.append({
            "name": "Rythu Bandhu",
            "tag": "Income",
            "score": min(100, rb_score),
            "amount": f"₹{benefit:,}",
            "link": "http://rythubandhu.telangana.gov.in/",
            "required_docs": ["Pattadar Passbook", "Aadhaar Card", "Mobile Number"],
            "how_to_apply": [
                "Visit nearest agriculture office or MeeSeva center",
                "Carry Pattadar Passbook and Aadhaar",
                "Get Passbook updated with latest entry",
                "Amount is auto-credited before each crop season"
            ],
            "eligibility_reason": f"You own {farmer_profile.land_size_acres} acres of land — eligible for seasonal investment support.",
            "youtube_link": "https://www.youtube.com/watch?v=tsDr6kQ5zKs"
        })

    # Crop Insurance
    if has_land:
        ins_score = 65
        if has_aadhaar: ins_score += 15
        if doc_count >= 2: ins_score += 10
        schemes.append({
            "name": "PM Fasal Bima Yojana",
            "tag": "Insurance",
            "score": min(100, ins_score),
            "amount": "2% premium",
            "link": "https://pmfby.gov.in/",
            "required_docs": ["Aadhaar Card", "Bank Account", "Crop Sowing Certificate", "Land Records"],
            "how_to_apply": [
                "Contact nearest bank branch or insurance company",
                "Fill PMFBY application before crop sowing deadline",
                "Pay 2% (Kharif) or 1.5% (Rabi) of sum insured as premium",
                "Receive confirmation and policy document"
            ],
            "eligibility_reason": "You have cultivable land — eligible for subsidized crop loss insurance coverage.",
            "youtube_link": "https://www.youtube.com/watch?v=ywJAu_VWi5k"
        })

    # PM-KUSUM Solar Pump Subsidy
    if has_land:
        kusum_score = 60
        if has_aadhaar: kusum_score += 20
        if has_bank: kusum_score += 10
        if doc_count >= 3: kusum_score += 10
        schemes.append({
            "name": "PM-KUSUM Solar Pump Subsidy",
            "tag": "Subsidy",
            "score": min(100, kusum_score),
            "amount": "60% Subsidy",
            "link": "https://pmkusum.mnre.gov.in/",
            "required_docs": ["Aadhaar Card", "Land Passbook", "Bank Account", "Passport Photo"],
            "how_to_apply": [
                "Visit the official PM-KUSUM portal or state energy agency site",
                "Fill in the application form with Aadhaar and land details",
                "Select the required solar pump capacity (HP) and type",
                "Submit bank details for subsidy credit and pay the farmer's share",
                "Wait for site verification and pump installation"
            ],
            "eligibility_reason": "You own agricultural land — eligible for 60% government subsidy to install off-grid solar agricultural pumps.",
            "youtube_link": "https://www.youtube.com/watch?v=R_Q1C6Q0K4Q"
        })

    # Kisan Credit Card
    kcc_score = 55
    if has_aadhaar: kcc_score += 15
    if has_land: kcc_score += 15
    if has_bank: kcc_score += 10
    if doc_count >= 3: kcc_score += 5
    schemes.append({
        "name": "Kisan Credit Card",
        "tag": "Loan",
        "score": min(100, kcc_score),
        "amount": "Up to ₹3,00,000",
        "link": "https://www.nabard.org/content1.aspx?id=603",
        "required_docs": ["Aadhaar Card", "Land Passbook", "Bank Account", "Passport Photo", "Income Certificate"],
        "how_to_apply": [
            "Visit nearest bank branch (SBI, PNB, Cooperative Bank etc.)",
            "Request KCC application form",
            "Submit land records, Aadhaar, photos",
            "Bank verifies and sanctions credit limit",
            "Receive KCC card with revolving credit"
        ],
        "eligibility_reason": "Farmers with land ownership qualify for KCC @ 4% interest for crop/input financing.",
        "youtube_link": "https://www.youtube.com/watch?v=oR4zCYHe4TI"
    })

    return schemes


@router.get("/approval/farmer/{user_id}", tags=["Approval Engine"])
def get_farmer_approval(user_id: int, session: Session = Depends(get_session)):
    user_profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    farmer_profile = session.exec(select(FarmerProfile).where(FarmerProfile.user_id == user_id)).first()

    schemes = _compute_scheme_approvals(farmer_profile, user_profile)

    overall = int(sum(s["score"] for s in schemes) / len(schemes)) if schemes else 0

    return {
        "overall_approval_score": overall,
        "opportunities": [
            {"name": s["name"], "score": s["score"], "tag": s["tag"]}
            for s in schemes
        ],
        "schemes": schemes
    }

@router.get("/approval/student/{user_id}", tags=["Approval Engine"])
def get_student_approval(user_id: int, session: Session = Depends(get_session)):
    user_profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    
    # Check profile data to update scores dynamically
    docs = []
    if user_profile and user_profile.profile_data:
        docs = user_profile.profile_data.get("documents", [])
        
    has_income = "income_certificate" in docs or "Income Certificate" in docs
    has_bonafide = "bonafide" in docs or "Bonafide Certificate" in docs
    
    inspire_score = 89 if has_income else 75
    aicte_score = 83 if has_bonafide else 70
    
    schemes = [
        {
            "name": "National Means-cum-Merit Scholarship",
            "tag": "Scholarships",
            "score": 91,
            "amount": "₹12,000 / year",
            "link": "https://scholarships.gov.in/",
            "required_docs": ["Aadhaar Card", "Class 8 Marks Card", "Income Certificate"],
            "how_to_apply": [
                "Visit National Scholarship Portal (NSP)",
                "Register as a new student",
                "Select Means-cum-Merit Scholarship",
                "Fill academic and family income details",
                "Upload required documents and submit"
            ],
            "eligibility_reason": "You are a merit student with family income under ₹3.5 Lakh.",
            "youtube_link": "https://www.youtube.com/watch?v=nsp"
        },
        {
            "name": "INSPIRE Scholarship",
            "tag": "Scholarships",
            "score": inspire_score,
            "amount": "₹80,000 / year",
            "link": "https://online-inspire.gov.in/",
            "required_docs": ["Class 12 Marks Card", "Endorsement Certificate", "Aadhaar Card", "Income Certificate"],
            "how_to_apply": [
                "Register on the INSPIRE portal",
                "Fill in personal and academic information",
                "Upload Endorsement Certificate signed by your college head",
                "Submit and track status"
            ],
            "eligibility_reason": "You are within the top 1% of your Class 12 board exam and studying basic sciences.",
            "youtube_link": "https://www.youtube.com/watch?v=inspire"
        },
        {
            "name": "Smart India Hackathon 2026",
            "tag": "Hackathons",
            "score": 85,
            "amount": "₹1,00,000 prize",
            "link": "https://sih.gov.in/",
            "required_docs": ["College ID Card", "Consent Letter"],
            "how_to_apply": [
                "Form a team of 6 students (minimum 1 female)",
                "Select a problem statement from the SIH portal",
                "Submit your idea proposal abstract",
                "Get nominated by your college SPOC"
            ],
            "eligibility_reason": "You are a CSE/BTech student with strong programming skills.",
            "youtube_link": "https://www.youtube.com/watch?v=sih"
        },
        {
            "name": "AICTE Research Internship",
            "tag": "Internships",
            "score": aicte_score,
            "amount": "₹15,000 / month",
            "link": "https://internship.aicte-india.org/",
            "required_docs": ["Bonafide Certificate", "Resume", "Aadhaar Card"],
            "how_to_apply": [
                "Log in to the AICTE Internship portal",
                "Complete your profile profile",
                "Search for research internship listings",
                "Apply to a listing and submit your statement of purpose"
            ],
            "eligibility_reason": "You have over 8.5 CGPA and matching technical skills.",
            "youtube_link": "https://www.youtube.com/watch?v=aicte"
        }
    ]
    
    overall = int(sum(s["score"] for s in schemes) / len(schemes))
    
    return {
        "overall_approval_score": overall,
        "opportunities": [
            {"name": s["name"], "score": s["score"], "tag": s["tag"]}
            for s in schemes
        ],
        "schemes": schemes
    }

from app.models.domain import Document, Opportunity

@router.get("/approval", tags=["Approval Engine"])
def get_jobseeker_approval(user_id: int = 5, session: Session = Depends(get_session)):
    user_docs = session.exec(select(Document).where(Document.user_id == user_id)).all()
    verified_docs = {d.document_master.document_name for d in user_docs if d.status == "Verified" and d.document_master}
    
    # We want to check missing docs across jobseeker opportunities
    opps = session.exec(select(Opportunity).where(Opportunity.module == "jobseeker")).all()
    
    missing_all = set()
    for opp in opps:
        for rd in opp.required_documents or []:
            if rd not in verified_docs:
                missing_all.add(rd)
                
    missing_list = list(missing_all)
    if missing_list:
        prob = max(40, 91 - len(missing_list) * 15)
        reason = f"Missing required documents: {', '.join(missing_list)}"
    else:
        prob = 91
        reason = "All required documents present"
        
    return {
        "approval_probability": prob,
        "reason": reason,
        "missing": missing_list
    }
