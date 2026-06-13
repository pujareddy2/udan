import json
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ValidationError
from app.core.config import settings

# ==========================================
# 1. OUTPUT SCHEMAS
# ==========================================
class EligibilityExtraction(BaseModel):
    age_requirements: Optional[str] = None
    income_limits: Optional[float] = None
    category_restrictions: List[str] = []
    location_requirements: List[str] = []
    hidden_requirements: List[str] = []

class BenefitExtraction(BaseModel):
    financial_value: Optional[float] = None
    benefit_summary: str

class FollowUpQuestion(BaseModel):
    question: str
    targets_field: str

class ExtractedOpportunity(BaseModel):
    opportunity_title: str
    scheme_name: str
    provider_name: str
    description: str
    opportunity_type: str
    benefits: BenefitExtraction
    eligibility: EligibilityExtraction
    documents: Dict[str, List[str]] # "required", "optional"
    deadlines: Dict[str, Optional[str]] # "application_deadline", "is_active"
    application: Dict[str, Optional[str]] # "apply_link", "offline_process"
    contact: Dict[str, Optional[str]] # "phone", "email"
    confidence_metrics: Dict[str, Any] # "overall_confidence", "missing_critical_fields"
    follow_up_questions: List[FollowUpQuestion] = []

# ==========================================
# 2. EXTRACTION AGENT
# ==========================================
class OpportunityExtractionAgent:
    """
    STAGE 6: Opportunity Extraction Agent
    Uses HTTP scraping and Groq API to extract raw HTML into deterministic Pydantic objects.
    """
    
    def process_extraction_queue(self, raw_opportunities: List[Dict[str, Any]]) -> List[ExtractedOpportunity]:
        """
        Takes raw DB row dictionaries, fetches text, extracts JSON, and prepares DB updates.
        """
        extracted_results = []
        
        for raw_opp in raw_opportunities:
            source_url = raw_opp.get("source_url", "")
            if not source_url:
                continue

            # Step 1: Live content fetching
            scraped_content = self._fetch_web_content(source_url)
            if not scraped_content:
                print(f"Skipping {source_url} due to scrape failure.")
                continue
            
            # Step 2: Clean content
            clean_text = self._clean_content(scraped_content)
            
            # Step 3 & 4: Call Groq API & Validate Schema
            extracted_json = self._extract_with_groq(clean_text)
            
            if not extracted_json:
                # Handle total LLM failure
                print(f"Skipping {source_url} due to LLM extraction failure.")
                continue
                
            try:
                # Step 5: Pydantic Enforcement
                opportunity = ExtractedOpportunity(**extracted_json)
                
                # Step 6: Recalculate Confidence
                opportunity = self._recalculate_confidence(opportunity)
                
                # Step 7 & 8: Output for Database mapping
                if opportunity.confidence_metrics["overall_confidence"] >= 50.0:
                    extracted_results.append(opportunity)
                else:
                    # Log to manual review queue
                    print(f"Opportunity {source_url} requires manual review (Confidence: {opportunity.confidence_metrics['overall_confidence']})")
                    
            except ValidationError as e:
                # In production, trigger a Retry Prompt here
                print(f"Pydantic Validation Error for {source_url}: {e}")
                
        return extracted_results

    def _fetch_web_content(self, url: str) -> str:
        """Fetches HTTP content from the given URL using Playwright headless browser to bypass JS checks."""
        try:
            from playwright.sync_api import sync_playwright
            from playwright_stealth import Stealth
            
            html_content = ""
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                
                # Apply stealth mode
                stealth = Stealth()
                stealth.apply_stealth_sync(page)
                
                # Navigate and wait for network to be idle to ensure JS framework loading
                page.goto(url, wait_until="networkidle", timeout=30000)
                
                html_content = page.content()
                browser.close()
            
            # Parse HTML and extract text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.extract()
                
            text = soup.get_text(separator=' ', strip=True)
            return text
        except Exception as e:
            print(f"Failed to fetch content from {url} with Playwright: {e}")
            return ""

    def _clean_content(self, text: str) -> str:
        """Truncates string to 15k characters to prevent context length issues."""
        return text[:15000]

    def _extract_with_groq(self, clean_text: str) -> Optional[Dict[str, Any]]:
        """
        Calls the live Groq Chat Completions API with structured JSON output.
        """
        api_key = settings.GROQ_API_KEY
        if not api_key:
            print("GROQ_API_KEY not found in settings")
            return None

        # Describe the schema clearly
        schema_instruction = """
        You must output EXACTLY a JSON object matching this schema. Do NOT wrap it in markdown. Do NOT hallucinate.
        {
            "opportunity_title": "string",
            "scheme_name": "string",
            "provider_name": "string",
            "description": "string",
            "opportunity_type": "string",
            "benefits": {
                "financial_value": float or null,
                "benefit_summary": "string"
            },
            "eligibility": {
                "age_requirements": "string" or null,
                "income_limits": float or null,
                "category_restrictions": ["string"],
                "location_requirements": ["string"],
                "hidden_requirements": ["string"]
            },
            "documents": {
                "required": ["string"],
                "optional": ["string"]
            },
            "deadlines": {
                "application_deadline": "string" or null,
                "is_active": "string" or null
            },
            "application": {
                "apply_link": "string" or null,
                "offline_process": "string" or null
            },
            "contact": {
                "phone": "string" or null,
                "email": "string" or null
            },
            "confidence_metrics": {
                "overall_confidence": float (0.0 to 100.0),
                "missing_critical_fields": ["string"]
            },
            "follow_up_questions": [
                {
                    "question": "string",
                    "targets_field": "string"
                }
            ]
        }
        """

        system_prompt = f"""
        You are an expert Government Scheme Extractor. Your task is to analyze the provided web text and extract the scheme's details into STRICT JSON. 
        You must accurately identify hidden eligibility constraints (e.g., "Only for SC/ST", "Only for Telangana residents").
        If a field is completely missing from the text, return null (for strings/floats) or an empty array (for lists). 

        {schema_instruction}
        """

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract the following web text:\n\n{clean_text}"}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.0
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code != 200:
                print(f"Groq API Error {resp.status_code}: {resp.text}")
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)
        except Exception as e:
            print(f"Groq Extraction API failed: {e}")
            return None

    def _recalculate_confidence(self, opp: ExtractedOpportunity) -> ExtractedOpportunity:
        """Applies mathematical penalties to the LLM's raw confidence score."""
        current_conf = float(opp.confidence_metrics.get("overall_confidence", 80.0))
        penalties = 0.0
        missing = []

        # Check Benefits
        if not opp.benefits.benefit_summary and opp.benefits.financial_value is None:
            penalties += 30.0
            missing.append("benefits")

        # Check Eligibility
        if not opp.eligibility.location_requirements and not opp.eligibility.category_restrictions and opp.eligibility.income_limits is None:
             penalties += 20.0
             missing.append("eligibility")

        # Check App Link
        if not opp.application.get("apply_link") and not opp.application.get("offline_process"):
             penalties += 15.0
             missing.append("application_link")

        # Check Deadline
        if not opp.deadlines.get("application_deadline"):
             penalties += 10.0
             missing.append("deadline")

        final_conf = max(0.0, current_conf - penalties)
        
        opp.confidence_metrics["overall_confidence"] = final_conf
        opp.confidence_metrics["missing_critical_fields"] = missing
        
        return opp
