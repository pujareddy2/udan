import csv
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# Absolute imports for the Clean System structure
from backend.integrations.profile_agent import parse_profile
from backend.integrations.explain import explain
from backend.logic.scam_shield import check_scam
from backend.logic.skill_to_scheme import free_fix
from backend.logic.eligibility import check_eligibility
from backend.logic.missed_and_alerts import missed, alerts

app = Flask(__name__)
CORS(app)

def load_csv(filename: str):
    """Utility to load rows from the specified CSV in the data folder."""
    filepath = os.path.join(os.path.dirname(__file__), "data", filename)
    if not os.path.exists(filepath):
        print(f"Warning: CSV not found at {filepath}")
        return []
        
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

@app.route("/api/ping", methods=["GET"])
def ping():
    return jsonify({"status": "healthy"})

@app.route("/api/profile/parse", methods=["POST"])
def parse():
    data = request.json or {}
    text = data.get("text", "")
    module = data.get("module", "jobseeker")
    lang = data.get("lang", "en")
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
        
    profile = parse_profile(text, module, lang)
    if not profile:
        return jsonify({"error": "Failed to parse profile"}), 500
        
    return jsonify({"profile": profile})

@app.route("/api/scam/check", methods=["POST"])
def scam_check():
    data = request.json or {}
    text = data.get("text", "")
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
        
    result = check_scam(text)
    return jsonify(result)

@app.route("/api/opportunities/match", methods=["POST"])
def match_opps():
    data = request.json or {}
    profile = data.get("profile", {})
    lang = data.get("lang", "en")
    
    if not profile:
        return jsonify({"error": "No profile provided"}), 400
        
    module = profile.get("module", "jobseeker")
    filename = "senior_citizens.csv" if module == "senior_citizen" else "jobseekers.csv"
    
    all_opps = load_csv(filename)
    
    eligible_list = []
    partial_list = []
    not_eligible_list = []
    
    # 1. Run core engine on active opportunities
    active_opps = [opp for opp in all_opps if str(opp.get("is_active")).lower() in ["true", "1", "yes"]]
    
    for opp in active_opps:
        # Step A: Deterministic Rules Engine
        eligibility = check_eligibility(profile, opp)
        
        # Step B: LLM Multilingual Translation
        explained = explain(eligibility, lang)
        
        verdict = explained.get("verdict")
        reasons_plain = explained.get("reasons_plain", [])
        missing_skills = explained.get("missing_skills", [])
        
        result_payload = {
            "opportunity": opp,
            "verdict": verdict,
            "reasons": reasons_plain,
            "readiness": explained.get("readiness", 0),
            "missing_documents": explained.get("missing_documents", []),
            "missing_skills": missing_skills
        }
        
        # Step C: Classification & Upgrades
        if verdict == "eligible":
            eligible_list.append(result_payload)
        elif verdict == "partial":
            # Inject free skill upgrades
            upgrades = free_fix(missing_skills)
            result_payload["upgrades"] = upgrades
            partial_list.append(result_payload)
        else:
            not_eligible_list.append(result_payload)
            
    # 2. Run Missed Opportunities Detector
    missed_list = missed(profile, all_opps, check_eligibility)
    
    # 3. Run Deadline Alert Center
    alert_list = alerts(profile, all_opps)
    
    return jsonify({
        "eligible": eligible_list,
        "partial": partial_list,
        "not_eligible": not_eligible_list,
        "missed": missed_list,
        "alerts": alert_list
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
