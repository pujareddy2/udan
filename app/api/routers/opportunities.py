from fastapi import APIRouter, Depends

router = APIRouter()

# Note: In a real app, these endpoints would be protected by a JWT auth dependency.
# For scaffolding, we will simulate it.

@router.get("/opportunities/eligible", tags=["Opportunities"])
def get_eligible_opportunities():
    """Get schemes user is currently eligible for."""
    return [
        {
            "id": 1,
            "title": "NSP Central Sector",
            "benefit_value": 12000.0,
            "deadline": "2025-03-31",
            "tags": ["Scholarship", "Student"]
        }
    ]

@router.get("/opportunities/recommended", tags=["Opportunities"])
def get_recommended_opportunities():
    """Get schemes user can unlock with more documents (Near Miss)."""
    return [
        {
            "id": 5,
            "title": "PM-KISAN",
            "benefit_value": 6000.0,
            "tags": ["Farmer", "Income Support"]
        }
    ]

@router.get("/opportunities/{opportunity_id}", tags=["Opportunities"])
def get_opportunity_details(opportunity_id: int):
    """Deep-dive details for a specific scheme."""
    return {
        "id": opportunity_id,
        "title": "NSP",
        "benefit_value": 12000.0,
        "tags": ["Scholarship"],
        "description": "National Scholarship Portal scheme...",
        "eligibility_rules": {"age": {"max": 25}, "income": {"max": 250000}},
        "required_documents": ["Aadhaar Card", "Income Certificate"],
        "followup_questions": ["What is your institution's AISHE code?"]
    }
