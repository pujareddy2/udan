import sqlite3
import json
from datetime import datetime, timedelta

def seed():
    conn = sqlite3.connect('udaan_v2.db')
    c = conn.cursor()

    # Clear existing tables to avoid duplicate key issues or conflicts
    tables_to_clear = [
        "document_master",
        "opportunities",
        "opportunity_deadlines",
        "opportunity_categories",
        "user_profiles",
        "jobseeker_profiles",
        "documents",
        "missed_opportunities",
        "applications",
        "timeline_events"
    ]
    
    for table in tables_to_clear:
        try:
            c.execute(f"DELETE FROM {table}")
        except Exception as e:
            print(f"Error clearing {table}: {e}")

    # Reset SQLite autoincrement sequences
    try:
        c.execute("DELETE FROM sqlite_sequence")
    except Exception as e:
        pass

    # 1. Seed Document Master
    documents_master = [
        (1, "Aadhaar Identity Card", "Identity", "Official government unique identification document", "UIDAI", "https://uidai.gov.in/", "Lifetime", 0, "[]", "7 Days"),
        (2, "Graduation Certificate (B.Tech)", "Academic", "Degree certificate issued by a recognized university", "UGC Recognized University", None, "Lifetime", 0, "[]", "30 Days"),
        (3, "Caste Certificate (OBC)", "Identity", "Official certificate verifying category status", "Tehsildar Office", "https://serviceonline.gov.in/", "Lifetime", 0, '["Aadhaar Identity Card"]', "15 Days"),
        (4, "Income Certificate", "Financial", "Official document verifying family annual income", "Tehsildar Office", "https://serviceonline.gov.in/", "1 Year", 1, '["Aadhaar Identity Card"]', "15 Days")
    ]
    
    c.executemany("""
        INSERT INTO document_master (id, document_name, document_type, description, issuing_authority, official_apply_link, validity_period, renewal_required, required_supporting_documents, processing_time, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    """, documents_master)

    # 2. Seed Opportunities
    # Required documents:
    # SSC CGL: Aadhaar, Graduation
    # RRB NTPC: Aadhaar, Graduation, Caste Certificate
    # NATS: Aadhaar, Graduation
    # PMKVY: Aadhaar
    # National Merit Scholarship: Aadhaar, Caste Certificate
    opps = [
        (1, "SSC CGL 2026", "jobseeker", 44900.0, "government", "central", '{"min_education": "graduate"}', '["Aadhaar Identity Card", "Graduation Certificate (B.Tech)"]', '["Quantitative Aptitude"]'),
        (2, "RRB NTPC – Railway Commercial Clerk", "jobseeker", 21700.0, "government", "central", '{"min_education": "graduate"}', '["Aadhaar Identity Card", "Graduation Certificate (B.Tech)", "Caste Certificate (OBC)"]', '["Typing Speed"]'),
        (3, "NATS Technical Apprenticeship", "jobseeker", 12000.0, "government", "central", '{"min_education": "graduate"}', '["Aadhaar Identity Card", "Graduation Certificate (B.Tech)"]', '["Basic IT"]'),
        (4, "PMKVY Java Developer Certification", "jobseeker", 8000.0, "government", "central", '{}', '["Aadhaar Identity Card"]', '["Java Programming"]'),
        (5, "National Merit Scholarship 2025", "jobseeker", 12000.0, "government", "central", '{"max_family_income": 250000}', '["Aadhaar Identity Card", "Caste Certificate (OBC)"]', '[]')
    ]
    
    for id, title, module, benefit, provider, state, rules, docs, skills in opps:
        c.execute("""
            INSERT INTO opportunities (id, title, module, benefit_value, provider_type, state_target, eligibility_rules, required_documents, followup_questions, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (id, title, module, benefit, provider, state, rules, docs, skills))

    # 3. Seed Deadlines
    deadlines = [
        (1, (datetime.now() + timedelta(days=37)).strftime('%Y-%m-%d %H:%M:%S'), "CGL Cycle 2026"),
        (2, (datetime.now() + timedelta(days=22)).strftime('%Y-%m-%d %H:%M:%S'), "RRB NTPC 2025"),
        (3, (datetime.now() + timedelta(days=79)).strftime('%Y-%m-%d %H:%M:%S'), "NATS Cycle 2026"),
        (4, (datetime.now() + timedelta(days=32)).strftime('%Y-%m-%d %H:%M:%S'), "PMKVY Java 2026")
    ]
    
    c.executemany("""
        INSERT INTO opportunity_deadlines (opportunity_id, deadline_date, cycle_name)
        VALUES (?, ?, ?)
    """, deadlines)

    # 4. Seed Categories/Tags
    categories = [
        (1, "Government Jobs"),
        (2, "Government Jobs"),
        (3, "Apprenticeships"),
        (4, "Skill Development"),
        (5, "Scholarships")
    ]
    
    c.executemany("""
        INSERT INTO opportunity_categories (opportunity_id, tag)
        VALUES (?, ?)
    """, categories)

    # 5. Seed user 5 UserProfile
    c.execute("""
        INSERT INTO user_profiles (user_id, full_name, mobile_number, age, gender, state, district, category, preferred_language, profile_data, created_at, updated_at)
        VALUES (5, 'Aanya Kumar', '9999999999', 22, 'Female', 'telangana', 'hyderabad', 'OBC', 'en', '{}', datetime('now'), datetime('now'))
    """)

    # 6. Seed jobseeker profile for user 5
    # Skills are Python, SQL, HTML, CSS (Java is missing!)
    c.execute("""
        INSERT INTO jobseeker_profiles (user_id, education_level, skills, employment_status, years_of_experience, preferred_job_role, is_disabled, created_at)
        VALUES (5, 'B.Tech In Computer Science', '["Python", "SQL", "HTML", "CSS"]', 'Unemployed', 1.0, 'Junior Software Engineer', 0, datetime('now'))
    """)

    # 7. Seed documents for user 5
    # Aadhaar Identity Card -> Verified
    # Graduation Certificate (B.Tech) -> Verified
    # Caste Certificate (OBC) -> Missing
    # Income Certificate -> not uploaded (Optional)
    user_docs = [
        (5, 1, 'Verified', 'https://s3.amazonaws.com/udaan/aadhaar.pdf'),
        (5, 2, 'Verified', 'https://s3.amazonaws.com/udaan/degree.pdf')
    ]
    
    for uid, doc_m_id, status, url in user_docs:
        c.execute("""
            INSERT INTO documents (user_id, doc_master_id, status, file_url, uploaded_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (uid, doc_m_id, status, url))

    # 8. Seed missed opportunities for user 5
    # National Merit Scholarship 2025 is missed because Caste Certificate (OBC) was not verified in time
    c.execute("""
        INSERT INTO missed_opportunities (user_id, opportunity_id, missed_value, root_cause, future_value_at_risk, recovery_score, missed_at)
        VALUES (5, 5, 12000.0, 'Caste Certificate was not verified in time', 0.0, 80, '2026-01-31 23:59:59')
    """)

    # 9. Seed applications for user 5 (NATS/SSC status trackers)
    # Let's seed applied for SSC CGL 2026 status
    c.execute("""
        INSERT INTO applications (user_id, opportunity_id, current_status, created_at, last_updated)
        VALUES (5, 1, 'Applied', datetime('now'), datetime('now'))
    """)

    # 10. Seed timeline events
    timeline_events = [
        (5, 'PROFILE', 'COMPLETED', 'Profile Completed', 0.0, datetime.now() - timedelta(days=5)),
        (5, 'DOCUMENT', 'VERIFIED', 'Aadhaar Identity Card Verified', 0.0, datetime.now() - timedelta(days=4)),
        (5, 'DOCUMENT', 'VERIFIED', 'Graduation Certificate (B.Tech) Verified', 0.0, datetime.now() - timedelta(days=3))
    ]
    
    for uid, cat, sub, text, val_gained, dt in timeline_events:
        c.execute("""
            INSERT INTO timeline_events (user_id, category, sub_type, story_text, value_gained, readiness_gain, importance, created_at)
            VALUES (?, ?, ?, ?, ?, 0.0, 'Low', ?)
        """, (uid, cat, sub, text, val_gained, dt.strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    conn.close()
    print("Database seeded with V2 jobseeker data successfully!")

if __name__ == "__main__":
    seed()
