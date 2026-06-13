import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

# 1. Register a fresh user
email = "jobseeker_test@udaan.com"
password = "TestPassword123!"

# Register
resp = requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password, "name": "Test Jobseeker"})
print("REGISTER STATUS:", resp.status_code)
user_data = resp.json()
print("REGISTER RESP:", json.dumps(user_data, indent=2))
user_id = user_data.get("user_id") or user_data.get("id")

# Login
resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
print("LOGIN STATUS:", resp.status_code)
login_data = resp.json()
print("LOGIN RESP:", json.dumps(login_data, indent=2))
token = login_data.get("access_token")

headers = {"Authorization": f"Bearer {token}"}

# Assign role jobseeker
resp = requests.post(f"{BASE_URL}/auth/{user_id}/role", json={"role": "jobseeker"}, headers=headers)
print("ROLE ASSIGN STATUS:", resp.status_code)

# Create a jobseeker profile via PUT
profile_payload = {
    "state": "Telangana",
    "district": "Hyderabad",
    "qualification": "graduate",
    "experience_years": "2.5",
    "preferred_job_role": "Python Developer",
    "employment_status": "Unemployed",
    "skills": ["python", "javascript", "fastapi"],
    "special_category": "PwD"
}
resp = requests.put(f"{BASE_URL}/profile/{user_id}/jobseeker", json=profile_payload, headers=headers)
print("PUT PROFILE STATUS:", resp.status_code)

# Now, fetch each endpoint
endpoints = [
    ("dashboard", f"/dashboard/jobseeker/{user_id}", "GET", None),
    ("profile_status", f"/profile/{user_id}/jobseeker/status", "GET", None),
    ("missed_opportunities", "/lifecycle/missed-opportunities", "GET", None),
    ("readiness", "/readiness", "GET", None),
    ("value", "/value", "GET", None),
    ("documents_summary", "/jobseeker/documents/summary", "GET", None),
    ("recovery_guide", "/documents/aadhaar/recovery-guide", "GET", None),
    ("recovery_plan", "/lifecycle/recovery-plan", "GET", None),
    ("opportunities_summary", "/jobseeker/opportunities/summary", "GET", None),
    ("trust_score", "/trust/ssc_cgl_2026", "GET", None),
    ("notifications_summary", "/notifications/summary", "GET", None),
    ("notifications_list", "/notifications", "GET", None),
    ("eligibility_run", "/eligibility/run", "POST", {"user_id": user_id, "opportunity_id": "ssc_cgl_2026"}),
    ("eligibility_questions", "/eligibility/questions", "POST", {"user_id": user_id, "opportunity_id": "ssc_cgl_2026"}),
    ("scam_shield", "/search", "POST", {"query": "Government job OBC Telangana", "module": "jobseeker", "user_id": user_id}),
    ("voice_chat", "/voice/chat", "POST", {"user_id": str(user_id), "message": "what jobs am I eligible for?", "language": "en"}),
    ("voice_suggestions", "/voice/suggestions", "GET", None),
]

for name, path, method, body in endpoints:
    url = f"{BASE_URL}{path}"
    print(f"\n==================== {name.upper()} ({method} {path}) ====================")
    try:
        if method == "GET":
            r = requests.get(url, headers=headers)
        elif method == "POST":
            r = requests.post(url, json=body, headers=headers)
        print("STATUS CODE:", r.status_code)
        print("RESPONSE:")
        try:
            print(json.dumps(r.json(), indent=2))
        except:
            print(r.text)
    except Exception as e:
        print("ERROR:", e)
