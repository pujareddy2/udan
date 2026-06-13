import json
import csv
import os
from backend.logic.eligibility import check_eligibility
from backend.integrations.explain import explain
from backend.logic.skill_to_scheme import free_fix
from backend.logic.missed_and_alerts import missed, alerts

profile = {
    "name": "Sree",
    "age": 25,
    "category": "general",
    "state": "Telangana",
    "qualification": "graduate",
    "module": "jobseeker",
    "skills": [],
    "documents": []
}

filepath = "backend/data/jobseekers.csv"
with open(filepath, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    all_opps = list(reader)

eligible_list = []
partial_list = []
not_eligible_list = []

active_opps = [opp for opp in all_opps if str(opp.get("is_active")).lower() in ["true", "1", "yes"]]

for opp in active_opps:
    eligibility = check_eligibility(profile, opp)
    explained = explain(eligibility, "en")
    
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
    
    if verdict == "eligible":
        eligible_list.append(result_payload)
    elif verdict == "partial":
        upgrades = free_fix(missing_skills)
        result_payload["upgrades"] = upgrades
        partial_list.append(result_payload)
    else:
        not_eligible_list.append(result_payload)
        
missed_list = missed(profile, all_opps, check_eligibility)
alert_list = alerts(profile, all_opps)

payload = {
    "eligible": eligible_list,
    "partial": partial_list,
    "not_eligible": not_eligible_list,
    "missed": missed_list,
    "alerts": alert_list
}

print("Trying standard json.dumps...")
try:
    s = json.dumps(payload)
    print("Success! Length:", len(s))
except Exception as e:
    print("Failed standard json.dumps:", e)

print("Trying sorting keys json.dumps...")
try:
    s = json.dumps(payload, sort_keys=True)
    print("Success! Length:", len(s))
except Exception as e:
    print("Failed sorting keys json.dumps:", e)
