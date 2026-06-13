"""
Udaan AI — Flask API Backend
============================
Serves the backend endpoints for voice transcript profile parsing,
eligibility engine matches, scam checking, and training scheme fixes.
"""

import os
import csv
import json
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure stdout to use UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.integrations.profile_agent import parse_profile, profile_from_form
from backend.integrations.explain import explain
from backend.logic.eligibility import check_eligibility
from backend.logic.scam_shield import check_scam
from backend.logic.skill_to_scheme import free_fix
from backend.logic.missed_and_alerts import missed, alerts

app = Flask(__name__)
# Enable CORS for all routes so the standalone HTML client can access it
CORS(app)


def _load_csv(filename: str) -> list:
    """Helper to load opportunities from a specified CSV file in data/ and strip out any None keys."""
    csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data",
        filename
    )
    if not os.path.exists(csv_path):
        return []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            clean_row = {k: v for k, v in r.items() if k is not None}
            rows.append(clean_row)
        return rows


@app.route("/api/ping", methods=["GET"])
def ping():
    return jsonify({"status": "healthy", "service": "udaan-backend"})


@app.route("/docs", methods=["GET"])
def docs():
    """
    Serves the interactive API explorer and documentation page.
    """
    docs_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "docs.html"
    )
    if not os.path.exists(docs_path):
        return "Documentation page not found.", 404
    with open(docs_path, "r", encoding="utf-8") as f:
        return f.read()


@app.route("/api/profile/parse", methods=["POST"])
def api_parse_profile():
    """
    Parses a free-text/voice transcript into a structured user profile.
    """
    data = request.json or {}
    text = data.get("text", "")
    module = data.get("module", "jobseeker")
    lang = data.get("lang", "en")

    if not text:
        return jsonify({"error": "No voice transcript text provided."}), 400

    profile = parse_profile(text, module, lang)
    if not profile:
        return jsonify({"error": "Failed to extract profile. Please try using the manual form."}), 422

    return jsonify(profile)


@app.route("/api/profile/form", methods=["POST"])
def api_profile_from_form():
    """
    Validates and constructs a structured profile from a manual form dictionary.
    """
    data = request.json or {}
    form_data = data.get("form", {})
    module = data.get("module", "jobseeker")

    if not form_data:
        return jsonify({"error": "Form data dictionary is empty."}), 400

    try:
        profile = profile_from_form(form_data, module)
        return jsonify(profile)
    except Exception as e:
        return jsonify({"error": f"Validation failed: {str(e)}"}), 422


@app.route("/api/opportunities/match", methods=["POST"])
def api_match_opportunities():
    """
    Given a user profile, matches opportunities from jobseekers.csv or senior_citizens.csv.
    Applies the eligibility engine, translates explanations, lists missing skills and fixes,
    and returns alerts and missed items.
    """
    data = request.json or {}
    profile = data.get("profile")
    lang = data.get("lang", "en")

    if not profile:
        return jsonify({"error": "Profile object is required."}), 400

    module = profile.get("module", "jobseeker")
    
    # Load correct CSV data pack based on module
    if module == "senior_citizen" or module == "seniors":
        opportunities = _load_csv("senior_citizens.csv")
    else:
        opportunities = _load_csv("jobseekers.csv")

    matched_eligible = []
    matched_partial = []
    matched_not_eligible = []

    for opp in opportunities:
        # Run eligibility engine
        eligibility = check_eligibility(profile, opp)
        
        # Translate explain layer (T3)
        explained = explain(eligibility, lang)
        
        # Skill upgrades mapping (T5)
        missing_skills = explained.get("missing_skills", [])
        upgrades = free_fix(missing_skills)

        # Merge results together for the UI
        result_entry = {
            "opportunity": opp,
            "verdict": explained["verdict"],
            "readiness": explained["readiness"],
            "reasons": explained["reasons_plain"],
            "missing_documents": explained["missing_documents"],
            "missing_skills": missing_skills,
            "upgrades": upgrades
        }

        verdict = explained["verdict"]
        if verdict == "eligible":
            matched_eligible.append(result_entry)
        elif verdict == "partial":
            matched_partial.append(result_entry)
        else:
            matched_not_eligible.append(result_entry)

    # 4. Missed Opportunities Detector (T6)
    missed_opps = missed(profile, opportunities, check_eligibility)
    
    # 5. Deadline Alerts (T6)
    deadline_alerts = alerts(profile, opportunities, within_days=90)

    return jsonify({
        "eligible": matched_eligible,
        "partial": matched_partial,
        "not_eligible": matched_not_eligible,
        "missed": missed_opps,
        "alerts": deadline_alerts
    })


@app.route("/api/scam/check", methods=["POST"])
def api_scam_check():
    """
    Runs rule-based heuristics on job descriptions to identify scams.
    """
    data = request.json or {}
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "Text description required for scam checking."}), 400

    result = check_scam(text)
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Starting Udaan API Backend on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
