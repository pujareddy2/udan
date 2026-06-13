import os
import sys
import json
import datetime
from sqlmodel import Session, select

# Ensure the app directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.extraction_agent import OpportunityExtractionAgent
from app.models.domain import Opportunity, OpportunityDeadline
from app.core.db import engine

def map_extracted_to_opportunity(extracted_json: dict) -> Opportunity:
    # Build eligibility rules JSON
    rules = {}
    
    eligibility = extracted_json.get("eligibility", {})
    hidden = eligibility.get("hidden_requirements", [])
    categories = eligibility.get("category_restrictions", [])
    
    # Analyze the parsed hidden requirements for logic mapping
    reqs_text = " ".join([str(r).lower() for r in hidden] + [str(c).lower() for c in categories])
    if "land" in reqs_text:
        rules["land_area_min"] = 0.1 # Must hold land
        
    documents = extracted_json.get("documents", {})
    req_docs = documents.get("required", [])
    
    followups = extracted_json.get("follow_up_questions", [])
    
    opp = Opportunity(
        title=extracted_json.get("opportunity_title") or "PM-Kisan",
        module="farmer",
        benefit_value=extracted_json.get("benefits", {}).get("financial_value") or 0.0,
        provider_type="government" if "gov" in (extracted_json.get("provider_name") or "").lower() or "scheme" in (extracted_json.get("opportunity_type") or "").lower() else "private",
        state_target="central",
        description=extracted_json.get("description"),
        benefit_summary=extracted_json.get("benefits", {}).get("benefit_summary"),
        apply_link=extracted_json.get("application", {}).get("apply_link"),
        opportunity_type=extracted_json.get("opportunity_type"),
        eligibility_rules=rules,
        required_documents=req_docs,
        followup_questions=[fq.get("question") for fq in followups if isinstance(fq, dict)]
    )
    return opp

def run_seed():
    print("Initializing Live Extraction...")
    agent = OpportunityExtractionAgent()
    
    # Use PM Kisan
    urls = ["https://pmkisan.gov.in/"]
    extracted_opps = []
    
    for url in urls:
        print(f"Scraping {url}...")
        scraped_content = agent._fetch_web_content(url)
        clean_text = agent._clean_content(scraped_content)
        extracted_json = agent._extract_with_groq(clean_text)
        
        if extracted_json:
            print(f"Extraction Successful for {url}!")
            extracted_opps.append(extracted_json)
        else:
            print(f"Failed to extract {url}")
            
    with Session(engine) as session:
        # Delete old farmer opportunities
        old_opps = session.exec(select(Opportunity).where(Opportunity.module == "farmer")).all()
        for old in old_opps:
            # Delete associated deadlines first to avoid FK constraint issues
            dls = session.exec(select(OpportunityDeadline).where(OpportunityDeadline.opportunity_id == old.id)).all()
            for dl in dls:
                session.delete(dl)
            session.delete(old)
        session.commit()
        print(f"Deleted {len(old_opps)} old mock farmer opportunities.")
        
        # Save new live opportunities
        for ext_opp in extracted_opps:
            db_opp = map_extracted_to_opportunity(ext_opp)
            session.add(db_opp)
            session.commit() # commit to get ID
            
            # Save deadline if present
            deadlines = ext_opp.get("deadlines", {})
            deadline_str = deadlines.get("application_deadline") if isinstance(deadlines, dict) else None
            
            if deadline_str:
                try:
                    dt = datetime.datetime.strptime(deadline_str, "%Y-%m-%d")
                    dl = OpportunityDeadline(opportunity_id=db_opp.id, deadline_date=dt)
                    session.add(dl)
                except:
                    # just save 30 days from now
                    dl = OpportunityDeadline(opportunity_id=db_opp.id, deadline_date=datetime.datetime.now() + datetime.timedelta(days=30))
                    session.add(dl)
            else:
                dl = OpportunityDeadline(opportunity_id=db_opp.id, deadline_date=datetime.datetime.now() + datetime.timedelta(days=365))
                session.add(dl)
            
            session.commit()
            print(f"Inserted DB Opportunity: {db_opp.title}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    run_seed()
