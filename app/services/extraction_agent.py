import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ValidationError

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
    Uses Gemini to scrape raw HTML into deterministic Pydantic objects.
    """
    
    def process_extraction_queue(self, raw_opportunities: List[Dict[str, Any]]) -> List[ExtractedOpportunity]:
        """
        Takes raw DB row dictionaries, fetches text, extracts JSON, and prepares DB updates.
        """
        extracted_results = []
        
        for raw_opp in raw_opportunities:
            # Step 1: Mock content fetching (in reality, an HTTP GET/Puppeteer scrape)
            scraped_content = self._fetch_web_content(raw_opp.get("source_url", ""))
            
            # Step 2: Clean content
            clean_text = self._clean_content(scraped_content)
            
            # Step 3 & 4: Call Gemini & Validate Schema
            extracted_json = self._extract_with_gemini(clean_text)
            
            if not extracted_json:
                # Handle total LLM failure
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
                    pass
                    
            except ValidationError as e:
                # In production, trigger a Retry Prompt here
                print(f"Pydantic Validation Error: {e}")
                
        return extracted_results

    def _fetch_web_content(self, url: str) -> str:
        """Simulates an HTTP fetch."""
        return "Apply for the TS State Farmer Scheme. Must be resident of Telangana. 10000 rupees subsidy."

    def _clean_content(self, text: str) -> str:
        """Truncates string to 15k characters to prevent token explosion."""
        return text[:15000]

    def _extract_with_gemini(self, clean_text: str) -> Optional[Dict[str, Any]]:
        """
        Mock implementation of the Gemini API call using Structured Outputs.
        """
        system_prompt = """
        You are an expert Government Scheme Extractor. Your task is to analyze the provided web text and extract the scheme's details into STRICT JSON. 
        You must accurately identify hidden eligibility constraints (e.g., "Only for SC/ST", "Only for Telangana residents").

        If a field is completely missing from the text, return null. Do NOT hallucinate.
        """
        # In production: google-genai structured output call.
        
        return {
            "opportunity_title": "Telangana State Farmer Subsidy",
            "scheme_name": "TS Farmer Scheme",
            "provider_name": "Government of Telangana",
            "description": "Financial assistance to farmers.",
            "opportunity_type": "Subsidy",
            "benefits": {
                "financial_value": 10000.0,
                "benefit_summary": "10000 rupees subsidy"
            },
            "eligibility": {
                "age_requirements": None,
                "income_limits": None,
                "category_restrictions": [],
                "location_requirements": ["Telangana"],
                "hidden_requirements": ["Must be registered farmer"]
            },
            "documents": {
                "required": ["Aadhaar", "Land Passbook"],
                "optional": []
            },
            "deadlines": {
                "application_deadline": "2026-12-31",
                "is_active": "true"
            },
            "application": {
                "apply_link": "https://agricoop.telangana.gov.in/apply",
                "offline_process": None
            },
            "contact": {
                "phone": "1800-111-222",
                "email": None
            },
            "confidence_metrics": {
                "overall_confidence": 95.0,
                "missing_critical_fields": []
            },
            "follow_up_questions": [
                {
                    "question": "Do you possess a valid Land Passbook?",
                    "targets_field": "documents"
                }
            ]
        }

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
