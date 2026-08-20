import os
import pandas as pd
import json
from datetime import datetime
from sqlmodel import Session
from app.core.db import engine, init_db
from app.models.domain import Opportunity

def parse_date(date_string):
    if not date_string or pd.isna(date_string):
        return None
    try:
        return datetime.strptime(str(date_string).strip(), "%Y-%m-%d").date()
    except ValueError:
        return None

def load_opportunities_from_csv(file_path: str, module_type: str, db: Session):
    if not os.path.exists(file_path):
        print(f"Skipping {file_path}: File not found.")
        return

    df = pd.read_csv(file_path)
    # Convert all NaN to empty string for easier parsing, except where we want explicit None checks
    df = df.where(pd.notnull(df), None)
    
    loaded_count = 0
    for _, row in df.iterrows():
        # 1. Map Deterministic Eligibility Rules
        eligibility_rules = {
            "min_age": row.get('min_age'),
            "max_age": row.get('max_age'),
            "age_relaxation": row.get('age_relaxation'),
            "income_max": row.get('income_max'),
            "income_min": row.get('income_min'),
            "state": row.get('state'),
            "district": row.get('district'),
            "category": row.get('category'),
            "gender": row.get('gender'),
            "qualification": row.get('qualification'),
            "cgpa_required": row.get('cgpa_required'),
            "experience_required": row.get('experience_required'),
            "business_stage": row.get('business_stage'),
            "startup_registered": row.get('startup_registered'),
            "land_size_min": row.get('land_size_min'),
            "land_size_max": row.get('land_size_max'),
            "crop_type": row.get('crop_type'),
            "land_required": row.get('land_required'),
            "land_owner_required": row.get('land_owner_required'),
            "required_skills": row.get('required_skills'),
        }
        # Clean out None/empty/NaN values to keep JSON minimal
        eligibility_rules = {k: v for k, v in eligibility_rules.items() if pd.notna(v) and v not in (None, "", "NaN", "nan")}

        # 2. Map Benefits
        benefits = {
            "benefit_amount": row.get('benefit_amount'),
            "benefit_type": row.get('benefit_type'),
            "renewal_frequency": row.get('renewal_frequency'),
        }
        benefits = {k: v for k, v in benefits.items() if pd.notna(v) and v not in (None, "", "NaN", "nan")}

        # 3. Map Metadata
        metadata_info = {
            "opportunity_type": row.get('opportunity_type'),
            "source_type": row.get('source_type'),
            "required_followup_questions": [q.strip() for q in str(row.get('required_followup_questions', '')).split(',') if q.strip() and str(q).lower() != 'nan'],
            "readiness_score_formula": row.get('readiness_score_formula'),
            "eligibility_explanation": row.get('eligibility_explanation'),
            "notification_trigger": row.get('notification_trigger')
        }
        def is_valid(v):
            """Return True if value is safe to store (not None/NaN/empty)."""
            if v is None:
                return False
            if isinstance(v, list):
                return len(v) > 0
            try:
                return pd.notna(v) and str(v) not in ("", "NaN", "nan", "None")
            except Exception:
                return False

        metadata_info = {k: v for k, v in metadata_info.items() if is_valid(v)}

        # 4. Map required documents
        req_docs_str = row.get('required_documents')
        required_documents = [doc.strip() for doc in str(req_docs_str).split(',')] if req_docs_str and pd.notna(req_docs_str) else []

        # Boolean conversion for verification
        verif_status = str(row.get('verification_status', 'Verified')).lower()
        is_active = verif_status in ['verified', 'true', '1', 'active', 'yes']

        try:
            p_score = int(float(str(row.get('priority_score', 0))))
        except (ValueError, TypeError):
            p_score = 0

        opp = Opportunity(
            title=row.get('title', 'Unknown Opportunity'),
            module=module_type,
            module_type=module_type,
            provider=row.get('source_name', 'Unknown Provider'),
            description=row.get('description', ''),
            eligibility_rules=eligibility_rules,
            benefits=benefits,
            metadata_info=metadata_info,
            required_documents=required_documents,
            url=row.get('official_link'),
            deadline=parse_date(row.get('deadline')),
            priority_score=p_score,
            is_active=is_active
        )
        # Duplicate Prevention
        from sqlmodel import select
        existing_opp = db.exec(select(Opportunity).where(
            Opportunity.title == opp.title,
            Opportunity.module_type == opp.module_type
        )).first()
        
        if not existing_opp:
            db.add(opp)
            loaded_count += 1
        else:
            safe_title = str(opp.title).encode('ascii', 'replace').decode('ascii')
            print(f"Skipping duplicate: {safe_title}")
    
    db.commit()
    print(f"Loaded {loaded_count} opportunities for {module_type} module from {file_path}")

def run_ingestion():
    init_db()
    
    data_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join(data_dir, "raw_csvs")
    
    module_files = {
        "students.csv": "Student",
        "farmers.csv": "Farmer",
        "jobseekers.csv": "Job Seeker",
        "entrepreneurs.csv": "Entrepreneur",
        "women_entrepreneurs.csv": "Women Entrepreneur",
        "startups.csv": "Startup",
        "senior_citizens.csv": "Senior Citizen",
    }
    
    with Session(engine) as db:
        for filename, module_type in module_files.items():
            file_path = os.path.join(raw_dir, filename)
            load_opportunities_from_csv(file_path, module_type, db)

if __name__ == "__main__":
    run_ingestion()
    print("Ingestion pipeline completed.")
