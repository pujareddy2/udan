"""
T10 — End-to-End Demo Integration Flow
======================================
This script demonstrates the entire flow:
1. Voice/Text query -> parse_profile() -> profile dict
2. Load opportunities CSV (jobseekers.csv)
3. Run eligibility engine on all opportunities
4. Identify eligible, partially eligible, and missed opportunities
5. Run explain() on a partially eligible opportunity to get reasons in Telugu
6. Identify free training schemes for any missing skills (T5)
7. Display deadline alerts for active opportunities (T6)

If GROQ_API_KEY is not set or the LLM call fails, the script automatically
falls back to mock LLM responses so the demo flow can be verified.
"""

import os
import csv
import json
import sys
from unittest.mock import patch

# Configure stdout encoding for Windows to display Telugu characters properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to python path if not present
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.integrations.profile_agent import parse_profile
from backend.integrations.explain import explain
from backend.logic.eligibility import check_eligibility
from backend.logic.missed_and_alerts import missed, alerts
from backend.logic.skill_to_scheme import free_fix


def load_jobseekers_csv() -> list:
    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "backend", "data", "jobseekers.csv"
    )
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def run_demo():
    print("==================================================================")
    print("                    UDAAN AI — DEMO INTEGRATION                   ")
    print("==================================================================")

    # 1. Text input representing a user talking to the system
    user_text = (
        "నా పేరు శ్రీ. నేను 25 సంవత్సరాల OBC మహిళను, తెలంగాణ నుండి. "
        "నేను డిగ్రీ పూర్తి చేసాను. నాకు కొద్దిగా ఎక్సెల్ తెలుసు, కానీ నాకు "
        "టైపింగ్ మరియు క్వాంటిటేటివ్ ఆప్టిట్యూడ్ రాదు."
    )
    print(f"User Transcribed Voice Input:\n{user_text}\n")

    # Fallback mock responses in case LLM is offline / no API key
    mock_profile_json = """
    {
        "name": "Sree",
        "age": 25,
        "gender": "female",
        "category": "obc",
        "state": "Telangana",
        "qualification": "graduate",
        "income": 180000,
        "skills": ["excel", "typing", "computer_basics", "data_entry"],
        "documents": ["12th_marksheet", "aadhaar", "caste_certificate", "dob_proof"],
        "interests": ["reading"]
    }
    """

    mock_explain_json = """
    [
        "వయస్సు, రాష్ట్రం, విద్యార్హత మొదలైన ప్రాథమిక అర్హతలు సరిపోయాయి.",
        "టైపింగ్ అనే నైపుణ్యం అవసరం.",
        "క్వాంటిటేటివ్ ఆప్టిట్యూడ్ అనే నైపుణ్యం అవసరం.",
        "డిగ్రీ సర్టిఫికేట్ సమర్పించాలి.",
        "ఆధార్ కార్డ్ సమర్పించాలి.",
        "కులం ధృవీకరణ పత్రం సమర్పించాలి.",
        "పుట్టిన తేదీ రుజువు సమర్పించాలి."
    ]
    """

    # We patch call_gemini to ensure the demo always runs cleanly even if no API key is set
    has_api_key = bool(os.getenv("GROQ_API_KEY"))
    
    def dummy_call_gemini(prompt: str) -> str:
        if "extract a user profile" in prompt:
            return mock_profile_json
        elif "rewrite each sentence" in prompt:
            return mock_explain_json
        return "[]"

    # Decide whether to patch based on key presence
    patcher = None
    if not has_api_key:
        print("ℹ️  GROQ_API_KEY not set. Running with local high-fidelity simulated LLM response...")
        patcher = patch("backend.integrations.profile_agent.call_gemini", side_effect=dummy_call_gemini)
        patcher.start()
        # Also patch explain call_gemini
        patcher_explain = patch("backend.integrations.explain.call_gemini", side_effect=dummy_call_gemini)
        patcher_explain.start()
    else:
        print("Using Groq API Key found in environment.")

    try:
        # Step 1: Parse profile
        profile = parse_profile(user_text, "jobseeker", lang="te")
        if not profile:
            print("❌ Error: Profile parsing failed.")
            return

        print("------------------------------------------------------------------")
        print("Step 1: Extracted User Profile")
        print("------------------------------------------------------------------")
        print(json.dumps(profile, indent=4))
        print()

        # Step 2: Load Opportunities
        opportunities = load_jobseekers_csv()
        print(f"Loaded {len(opportunities)} job seeker opportunities from data/jobseekers.csv.\n")

        # Step 3: Run Eligibility Engine & Missed Opportunities Detector
        eligible_list = []
        partial_list = []
        not_eligible_list = []

        for opp in opportunities:
            res = check_eligibility(profile, opp)
            opp_with_res = dict(opp)
            opp_with_res["_eligibility"] = res
            
            verdict = res["verdict"]
            if verdict == "eligible":
                eligible_list.append(opp_with_res)
            elif verdict == "partial":
                partial_list.append(opp_with_res)
            else:
                not_eligible_list.append(opp_with_res)

        # Step 4: Display Missed Opportunities (Regret Hook)
        missed_opps = missed(profile, opportunities, check_eligibility)

        print("------------------------------------------------------------------")
        print("Step 2: Missed Opportunities (Emotional Regret Hook)")
        print("------------------------------------------------------------------")
        if missed_opps:
            for opp in missed_opps:
                print(f"❌ You missed '{opp['title']}' (Closed on: {opp['close_date']}).")
                print(f"   Reason: You were fully eligible, but the application window is now closed.")
                print(f"   Potential Value: {opp['amount']}")
        else:
            print("No missed opportunities found.")
        print()

        # Step 5: Process a Partially Eligible Scheme (SSC CGL)
        target_opp = None
        for opp in partial_list:
            if "SSC CGL" in opp["title"]:
                target_opp = opp
                break
        
        if not target_opp and partial_list:
            target_opp = partial_list[0]

        if target_opp:
            print("------------------------------------------------------------------")
            print(f"Step 3: Eligibility & Multilingual Explanations for '{target_opp['title']}'")
            print("------------------------------------------------------------------")
            
            # Run the explain layer to translate the reasons to Telugu
            telugu_explanation = explain(target_opp["_eligibility"], language="te")

            print(f"Verdict: {telugu_explanation['verdict'].upper()}")
            print(f"Readiness Score: {telugu_explanation['readiness']}%")
            print("\nDetailed Reasons (in Telugu):")
            for reason in telugu_explanation["reasons_plain"]:
                print(f"  • {reason}")

            # Step 6: Offer Skill Upgrades (Free Skilling Schemes map)
            missing_skills = telugu_explanation["missing_skills"]
            print(f"\nMissing Skills: {missing_skills}")
            
            scheme_fixes = free_fix(missing_skills)
            if scheme_fixes:
                print("\n💡 Actionable Upgrades (Free Government Training Schemes):")
                for fix in scheme_fixes:
                    print(f"  • For '{fix['skill']}': Train via '{fix['scheme']}'")
                    print(f"    Official Link: {fix['url']}")
            
            print(f"\nRequired Documents to Gather: {telugu_explanation['missing_documents']}")
            print()

        # Step 7: Deadline Alert Center
        print("------------------------------------------------------------------")
        print("Step 4: Active Application Alerts")
        print("------------------------------------------------------------------")
        active_alerts = alerts(profile, opportunities, within_days=180) # wider window for demo
        if active_alerts:
            for alert in active_alerts:
                print(alert["message"])
        else:
            print("No upcoming deadlines in the alert window.")

    finally:
        if patcher:
            patcher.stop()
            # Stop explain patcher as well
            try:
                patcher_explain.stop()
            except Exception:
                pass

    print("==================================================================")
    print("                        DEMO RUN COMPLETE                         ")
    print("==================================================================")


if __name__ == "__main__":
    run_demo()
