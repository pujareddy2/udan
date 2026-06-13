import os
import sys

# Ensure the app directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.extraction_agent import OpportunityExtractionAgent
from dotenv import load_dotenv

# Load .env explicitly for settings
load_dotenv()

def test_extraction():
    agent = OpportunityExtractionAgent()
    
    # We will use the original pmkisan.gov.in to test Playwright security bypass
    raw_opp = {
        "source_url": "https://pmkisan.gov.in/"
    }
    
    print("Starting extraction test on:", raw_opp["source_url"])
    print("Fetching and extracting data. Please wait (this can take 5-15 seconds for Groq)...")
    
    scraped_content = agent._fetch_web_content(raw_opp["source_url"])
    clean_text = agent._clean_content(scraped_content)
    extracted_json = agent._extract_with_groq(clean_text)
    
    if extracted_json:
        print("\n--- EXTRACTION SUCCESSFUL ---")
        import json
        print(json.dumps(extracted_json, indent=2))
    else:
        print("\n--- EXTRACTION FAILED OR RETURNED EMPTY ---")

if __name__ == "__main__":
    test_extraction()
