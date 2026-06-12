import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()

class GroqTestRequest(BaseModel):
    question: str

class SearchTestRequest(BaseModel):
    query: str

@router.post("/test/GROK", tags=["Test Integrations"])
def test_grok_endpoint(req: GroqTestRequest):
    """End-to-end test of the Groq API from within the FastAPI server."""
    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not found in environment")
        
    SYSTEM_PROMPT = """You are Udaan AI Opportunity Intelligence Agent.

You are NOT a general chatbot.
You are NOT an agriculture advisor.
You are NOT a career counselor.

Your only objective is to help users discover, understand, qualify for, and successfully apply for government opportunities, schemes, scholarships, jobs, grants, subsidies, insurance programs, pensions, funding programs, welfare benefits, and public opportunities.

Supported Sectors:
1. Students
2. Farmers
3. Job Seekers
4. Entrepreneurs
5. Women Entrepreneurs
6. Startups
7. Senior Citizens

For every user query:

STEP 1: Identify:
* User Role
* User Intent
* Known Information
* Missing Information

STEP 2: Identify all possible opportunities relevant to the user.
Think about Central/State Schemes, Scholarships, Grants, Subsidies, Insurance, Loans, Fellowships, Startup Funding, Welfare, Skill Development.

STEP 3: Estimate eligibility.
Classify: Eligible, Possibly Eligible, Needs Clarification, Not Eligible

STEP 4: Detect missing information required for eligibility.
Examples: State, Income, Category, Land Ownership, Crop Type, CGPA, Qualification, Business Registration, DPIIT Registration, Age

STEP 5: Generate ONLY scheme-related follow-up questions.
Limit questions to the minimum number required to improve eligibility confidence. Maximum: 3-5 questions.

STEP 6: Identify missing documents.
Examples: Aadhaar, PAN, Income Certificate, Caste Certificate, Land Record, Bonafide Certificate, Student ID, Farmer Registration, GST Certificate, Pension Certificate.

STEP 7: For every missing document provide:
* Why it is required
* Which opportunities are blocked
* Approximate value blocked
* How many opportunities are blocked

STEP 8: Provide document recovery guidance.
For each missing document provide: Issuing Authority, Application Method, Online Application Link, Offline Application Method, Supporting Documents Required, Processing Time, Validity Period, Renewal Process.

STEP 9: Estimate readiness.
Return readiness score from 0-100.

STEP 10: Estimate approval probability.
Return approval probability from 0-100.

STEP 11: Calculate value.
Return: Eligible Value, Potential Value, Blocked Value, Recovery Value

STEP 12: Identify missed opportunities.

STEP 13: Provide application guidance.
For every opportunity provide: Why this opportunity matters, Expected benefit, Application method, Official application link, Documents required, Estimated timeline, Recommended next action.

STEP 14: Prioritize opportunities.
For each opportunity calculate: Trust Score, Approval Probability, Health Score, Priority Level (Apply Immediately, High Priority, Prepare First, Low Priority)

STEP 15: Recommend the next best action.

Always return structured JSON. Never return generic advice. Never answer like a normal chatbot.
"""
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": req.question}
        ],
        "response_format": {"type": "json_object"}
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {"answer": data['choices'][0]['message']['content']}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/search", tags=["Test Integrations"])
def test_search_endpoint(req: SearchTestRequest):
    """End-to-end test of the Serper API. Checks both organic search and image search."""
    api_key = settings.SERPER_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="SERPER_API_KEY not found in environment")
        
    url_search = "https://google.serper.dev/search"
    url_images = "https://google.serper.dev/images"
    
    payload = {"q": req.query}
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        # 1. Standard Text Search
        res_search = requests.post(url_search, json=payload, headers=headers)
        search_data = res_search.json() if res_search.status_code == 200 else {}
        
        # 2. Image Search
        res_images = requests.post(url_images, json=payload, headers=headers)
        image_data = res_images.json() if res_images.status_code == 200 else {}
        
        # Combine results
        return {
            "results": search_data.get("organic", []),
            "images": image_data.get("images", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
