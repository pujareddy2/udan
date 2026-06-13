import requests

base_url = "http://localhost:8000/api/v1"

endpoints = [
    ("/dashboard/jobseeker/5", "GET"),
    ("/profile-context/5", "GET"),
    ("/lifecycle/missed-opportunities", "GET"),
    ("/lifecycle/recovery-plan", "GET"),
    ("/readiness?user_id=5", "GET"),
    ("/wallet/documents?user_id=5", "GET"),
    ("/jobseeker/roadmap?user_id=5", "GET"),
    ("/opportunities/recommended?user_id=5", "GET"),
    ("/trust/1", "GET"),
    ("/approval?user_id=5", "GET"),
    ("/value?user_id=5", "GET"),
    ("/wallet/opportunities?user_id=5", "GET"),
    ("/jobseeker/applications?user_id=5", "GET"),
    ("/jobseeker/deadlines?user_id=5", "GET"),
    ("/jobseeker/opportunity-summary?user_id=5", "GET"),
    ("/jobseeker/value-summary?user_id=5", "GET"),
    ("/jobseeker/document-summary?user_id=5", "GET"),
    ("/notifications", "GET"),
]

print("--- Testing Job Seeker API Endpoints ---")
for path, method in endpoints:
    url = base_url + path
    try:
        if method == "GET":
            r = requests.get(url, timeout=5)
        else:
            r = requests.post(url, timeout=5)
        print(f"[{r.status_code}] {method} {path}")
        if r.status_code != 200:
            print("  Response:", r.text)
        else:
            print("  Keys:", list(r.json().keys()) if isinstance(r.json(), dict) else "List length: " + str(len(r.json())))
    except Exception as e:
        print(f"[ERROR] {method} {path} - {e}")

print("\n--- Testing Coach POST API ---")
try:
    r = requests.post(base_url + "/coach/generate", json={"user_id": "5", "prompt": "Give me government jobs"}, timeout=5)
    print(f"[{r.status_code}] POST /coach/generate")
    print("  Response:", r.json())
except Exception as e:
    print(f"[ERROR] POST /coach/generate - {e}")

print("\n--- Testing Document Upload POST API ---")
try:
    r = requests.post(base_url + "/documents/upload", json={"user_id": 5, "document_name": "Income Certificate"}, timeout=5)
    print(f"[{r.status_code}] POST /documents/upload")
    print("  Response:", r.json())
except Exception as e:
    print(f"[ERROR] POST /documents/upload - {e}")
