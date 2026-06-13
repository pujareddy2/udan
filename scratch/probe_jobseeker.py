import requests
import json

BASE = "http://127.0.0.1:8000"
uid = "27"
token = "mock_jwt_token_12345"
headers = {"Authorization": f"Bearer {token}"}

endpoints = [
    f"/api/v1/dashboard/jobseeker/{uid}",
    f"/api/v1/profile/{uid}/jobseeker/status",
    f"/api/v1/jobseeker/opportunities/summary?user_id={uid}",
    f"/api/v1/jobseeker/documents/summary?user_id={uid}",
    f"/api/v1/readiness?user_id={uid}",
    f"/api/v1/value?user_id={uid}",
    f"/api/v1/lifecycle/recovery-plan?user_id={uid}",
]

for ep in endpoints:
    r = requests.get(f"{BASE}{ep}", headers=headers)
    label = ep.split("?")[0]
    print(f"\n=== {label} [{r.status_code}] ===")
    if r.ok:
        print(json.dumps(r.json(), indent=2)[:1200])
    else:
        print(r.text[:300])
