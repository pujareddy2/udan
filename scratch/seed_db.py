import sqlite3
import json
from datetime import datetime, timedelta

def seed():
    conn = sqlite3.connect('udaan_v2.db')
    c = conn.cursor()

    # 1. Seed Document Master
    documents_master = [
        ("Aadhaar Card", "Identity", "Official government unique identification document", "UIDAI", "https://uidai.gov.in/", "Lifetime", 0, "[]", "7 Days"),
        ("Income Certificate", "Financial", "Official document verifying family annual income", "Tehsildar Office", "https://serviceonline.gov.in/", "1 Year", 1, '["Aadhaar Card", "Ration Card"]', "15 Days"),
        ("Domicile Certificate", "Residence", "Proof of residency in a particular state", "MRO Office", "https://serviceonline.gov.in/", "Lifetime", 0, '["Aadhaar Card"]', "10 Days"),
        ("Graduation Certificate", "Academic", "Degree certificate issued by a recognized university", "UGC Recognized University", None, "Lifetime", 0, "[]", "30 Days"),
        ("12th Certificate", "Academic", "Higher secondary board certificate", "State/Central Board", None, "Lifetime", 0, "[]", "15 Days"),
        ("10th Certificate", "Academic", "Secondary school certificate", "State/Central Board", None, "Lifetime", 0, "[]", "15 Days")
    ]
    
    c.executemany("""
        INSERT OR IGNORE INTO document_master (document_name, document_type, description, issuing_authority, official_apply_link, validity_period, renewal_required, required_supporting_documents, processing_time, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    """, documents_master)

    # 2. Seed Opportunities
    opps = [
        ("SSC CGL 2026", "jobseeker", 50000.0, "government", "central", '{"min_education": "graduate"}', '["Aadhaar Card", "Graduation Certificate"]', '["Quantitative Aptitude"]'),
        ("RRB NTPC 2025", "jobseeker", 40000.0, "government", "central", '{"min_education": "graduate"}', '["Aadhaar Card", "Graduation Certificate"]', '["Typing Speed"]'),
        ("NAPS Apprenticeship", "jobseeker", 10000.0, "government", "central", '{"min_education": "10th_pass"}', '["Aadhaar Card", "10th Certificate"]', '["Basic IT"]'),
        ("PMKVY Skill Program", "jobseeker", 8000.0, "government", "central", '{}', '["Aadhaar Card"]', '["Basic Computers"]'),
        ("TSPSC Group 4 2026", "jobseeker", 30000.0, "government", "telangana", '{"min_education": "12th_pass", "state": "telangana"}', '["Aadhaar Card", "Domicile Certificate", "12th Certificate"]', '["General Knowledge"]'),
        ("National Merit Scholarship", "jobseeker", 12000.0, "government", "central", '{"max_family_income": 250000}', '["Aadhaar Card", "Income Certificate"]', '[]')
    ]
    
    for title, module, benefit, provider, state, rules, docs, skills in opps:
        c.execute("""
            INSERT OR IGNORE INTO opportunities (title, module, benefit_value, provider_type, state_target, eligibility_rules, required_documents, followup_questions, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (title, module, benefit, provider, state, rules, docs, skills))

    # 3. Seed Deadlines
    c.execute("SELECT id, title FROM opportunities WHERE module='jobseeker'")
    opp_ids = {row[1]: row[0] for row in c.fetchall()}
    
    deadlines = [
        (opp_ids["SSC CGL 2026"], (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'), "CGL Cycle 2026"),
        (opp_ids["TSPSC Group 4 2026"], (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'), "TSPSC Cycle 2026"),
        (opp_ids["NAPS Apprenticeship"], (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'), "NAPS Cycle 2026"),
        (opp_ids["RRB NTPC 2025"], (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S'), "RRB NTPC 2025")
    ]
    
    c.executemany("""
        INSERT OR IGNORE INTO opportunity_deadlines (opportunity_id, deadline_date, cycle_name)
        VALUES (?, ?, ?)
    """, deadlines)

    # 4. Seed Categories/Tags
    categories = [
        (opp_ids["SSC CGL 2026"], "Government Jobs"),
        (opp_ids["RRB NTPC 2025"], "Government Jobs"),
        (opp_ids["NAPS Apprenticeship"], "Apprenticeships"),
        (opp_ids["PMKVY Skill Program"], "Skill Development"),
        (opp_ids["TSPSC Group 4 2026"], "Government Jobs"),
        (opp_ids["National Merit Scholarship"], "Scholarships")
    ]
    
    c.executemany("""
        INSERT OR IGNORE INTO opportunity_categories (opportunity_id, tag)
        VALUES (?, ?)
    """, categories)

    # 5. Seed user 5 user_profiles and documents if needed
    c.execute("SELECT id FROM user_profiles WHERE user_id=5")
    if not c.fetchone():
        c.execute("""
            INSERT INTO user_profiles (user_id, full_name, mobile_number, age, gender, state, district, category, preferred_language, profile_data, created_at, updated_at)
            VALUES (5, 'Puja', '9999999999', 22, 'Female', 'telangana', 'hyderabad', 'OBC', 'en', '{}', datetime('now'), datetime('now'))
        """)
    else:
        # Update user 5's profile name to Puja and state to telangana to match specifications
        c.execute("UPDATE user_profiles SET full_name='Puja', state='telangana', district='hyderabad', category='OBC' WHERE user_id=5")

    # 6. Seed jobseeker profile for user 5 if missing
    c.execute("SELECT id FROM jobseeker_profiles WHERE user_id=5")
    if not c.fetchone():
        c.execute("""
            INSERT INTO jobseeker_profiles (user_id, education_level, skills, employment_status, years_of_experience, preferred_job_role, is_disabled, created_at)
            VALUES (5, 'graduate', '["Python", "SQL"]', 'Unemployed', 0.0, 'AI Engineer', 0, datetime('now'))
        """)

    # 7. Seed documents for user 5
    # Let's seed Aadhaar Card and Graduation Certificate as verified, and Domicile Certificate as pending
    c.execute("SELECT id FROM document_master WHERE document_name='Aadhaar Card'")
    aadhaar_id = c.fetchone()[0]
    c.execute("SELECT id FROM document_master WHERE document_name='Graduation Certificate'")
    grad_id = c.fetchone()[0]
    c.execute("SELECT id FROM document_master WHERE document_name='Domicile Certificate'")
    domicile_id = c.fetchone()[0]
    
    user_docs = [
        (5, aadhaar_id, 'Verified', 'https://s3.amazonaws.com/udaan/aadhaar.pdf'),
        (5, grad_id, 'Verified', 'https://s3.amazonaws.com/udaan/degree.pdf'),
        (5, domicile_id, 'Pending', None)
    ]
    
    for uid, doc_m_id, status, url in user_docs:
        c.execute("SELECT id FROM documents WHERE user_id=? AND doc_master_id=?", (uid, doc_m_id))
        if not c.fetchone():
            c.execute("""
                INSERT INTO documents (user_id, doc_master_id, status, file_url, uploaded_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (uid, doc_m_id, status, url))

    # 8. Seed missed opportunities for user 5 (National Merit Scholarship is missed because of missing Income Certificate)
    c.execute("SELECT id FROM missed_opportunities WHERE user_id=5")
    if not c.fetchone():
        c.execute("""
            INSERT INTO missed_opportunities (user_id, opportunity_id, missed_value, root_cause, future_value_at_risk, recovery_score, missed_at)
            VALUES (5, ?, 12000.0, 'Missing Income Certificate', 0.0, 80, datetime('now'))
        """, (opp_ids["National Merit Scholarship"],))

    # 9. Seed applications for user 5
    # Let's seed an applied opportunity for SSC CGL 2026, TSPSC Group 4 2026 as started/needs review
    c.execute("SELECT id FROM applications WHERE user_id=5")
    if not c.fetchone():
        c.execute("""
            INSERT INTO applications (user_id, opportunity_id, current_status, created_at, last_updated)
            VALUES (5, ?, 'Applied', datetime('now'), datetime('now'))
        """, (opp_ids["SSC CGL 2026"],))
        c.execute("""
            INSERT INTO applications (user_id, opportunity_id, current_status, created_at, last_updated)
            VALUES (5, ?, 'Under Review', datetime('now'), datetime('now'))
        """, (opp_ids["TSPSC Group 4 2026"],))

    # 10. Seed timeline events
    timeline_events = [
        (5, 'PROFILE', 'COMPLETED', 'Profile Completed', 0.0, datetime.now() - timedelta(days=5)),
        (5, 'DOCUMENT', 'VERIFIED', 'Aadhaar Card Verified', 0.0, datetime.now() - timedelta(days=4)),
        (5, 'DOCUMENT', 'VERIFIED', 'Graduation Certificate Verified', 0.0, datetime.now() - timedelta(days=3)),
        (5, 'APPLICATION', 'APPLIED', 'Applied for SSC CGL 2026', 50000.0, datetime.now() - timedelta(days=2)),
        (5, 'APPLICATION', 'UNDER_REVIEW', 'TSPSC Group 4 Under Review', 30000.0, datetime.now() - timedelta(days=1))
    ]
    
    for uid, cat, sub, text, val_gained, dt in timeline_events:
        c.execute("SELECT id FROM timeline_events WHERE user_id=? AND story_text=?", (uid, text))
        if not c.fetchone():
            c.execute("""
                INSERT INTO timeline_events (user_id, category, sub_type, story_text, value_gained, readiness_gain, importance, created_at)
                VALUES (?, ?, ?, ?, ?, 0.0, 'Low', ?)
            """, (uid, cat, sub, text, val_gained, dt.strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    conn.close()
    print("Database seeded with jobseeker data successfully!")

if __name__ == "__main__":
    seed()
