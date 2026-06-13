import requests, uuid, json, sys

BASE = "http://127.0.0.1:8000"

email = f"smoke_{uuid.uuid4().hex[:8]}@test.com"
password = "Test1234!"

r = requests.post(f"{BASE}/api/v1/auth/register", json={"email": email, "password": password, "name": "Smoke Tester"})
if r.status_code not in (200, 201):
    print(f"FATAL: register failed {r.status_code} {r.text}"); sys.exit(1)
body = r.json()
user_id = body.get("user_id") or body.get("id") or (body.get("data") or {}).get("user_id")
print(f"Registered: {user_id}")

r = requests.post(f"{BASE}/api/v1/auth/login", json={"email": email, "password": password})
if r.status_code != 200:
    print(f"FATAL: login failed {r.status_code} {r.text}"); sys.exit(1)
token = r.json().get("access_token") or r.json().get("token")
H = {"Authorization": f"Bearer {token}"}

requests.post(f"{BASE}/api/v1/auth/{user_id}/role", json={"role": "jobseeker"}, headers=H)
requests.put(f"{BASE}/api/v1/profile/{user_id}/jobseeker", headers=H, json={
    "name":"Smoke","age":26,"gender":"male","category":"OBC","state":"Telangana",
    "district":"Hyderabad","language":"en","qualification":"graduate","income":200000,
    "skills":["python"],"interests":["government_job"]})

opp_id = "ssc_cgl_2026"
r2 = requests.get(f"{BASE}/api/v1/jobseeker/opportunities/summary", headers=H)
if r2.status_code == 200:
    d = r2.json()
    items = d if isinstance(d, list) else d.get("opportunities") or d.get("data") or []
    if items:
        opp_id = items[0].get("id") or items[0].get("opportunity_id") or opp_id

def s(p):
    return p.replace("{user_id}", str(user_id)).replace("{role}","jobseeker").replace("{module}","jobseeker").replace("{opportunity_id}",opp_id).replace("{document_name}","aadhaar").replace("{id}","notif_1")

endpoints = [
    ("Auth","POST","/api/v1/auth/register",{"email":f"x{uuid.uuid4().hex[:6]}@t.com","password":"Test1234!","name":"X"}),
    ("Auth","POST","/api/v1/auth/{user_id}/profile",{"name":"Smoke","bio":"test"}),
    ("Auth","POST","/api/v1/auth/{user_id}/role",{"role":"jobseeker"}),
    ("Auth","POST","/api/v1/auth/login",{"email":email,"password":password}),
    ("Profile","PUT","/api/v1/profile/{user_id}/farmer",{"name":"S","age":40,"gender":"male","category":"OBC","state":"Telangana","district":"H","language":"en","land_size":2.0,"crop":"rice","irrigation":"canal","income":100000,"skills":[],"interests":[]}),
    ("Profile","PUT","/api/v1/profile/{user_id}/jobseeker",{"name":"S","age":26,"gender":"male","category":"OBC","state":"Telangana","district":"H","language":"en","qualification":"graduate","income":200000,"skills":["python"],"interests":["government_job"]}),
    ("Profile","GET","/api/v1/profile/{user_id}/{role}/status",None),
    ("ProfileCtx","POST","/api/v1/profile-context/generate",{"user_id":user_id,"module":"jobseeker"}),
    ("Discovery","POST","/api/v1/ai-discovery/run",{"user_id":user_id,"module":"jobseeker"}),
    ("Eligibility","POST","/api/v1/eligibility/run",{"user_id":user_id,"module":"jobseeker"}),
    ("Eligibility","POST","/api/v1/eligibility/questions",{"user_id":user_id,"module":"jobseeker"}),
    ("Opportunities","GET","/api/v1/student/opportunities/summary",None),
    ("Opportunities","GET","/api/v1/farmer/opportunities/summary",None),
    ("Opportunities","GET","/api/v1/jobseeker/opportunities/summary",None),
    ("Opportunities","GET","/api/v1/entrepreneur/opportunities/summary",None),
    ("Opportunities","GET","/api/v1/women-entrepreneur/opportunities/summary",None),
    ("Opportunities","GET","/api/v1/startup/opportunities/summary",None),
    ("Opportunities","GET","/api/v1/senior-citizen/opportunities/summary",None),
    ("Wallet","GET","/api/v1/wallet/summary",None),
    ("Wallet","GET","/api/v1/wallet/opportunities",None),
    ("Lifecycle","GET","/api/v1/lifecycle/missed-opportunities",None),
    ("Lifecycle","GET","/api/v1/lifecycle/recovery-plan",None),
    ("Readiness","GET","/api/v1/readiness",None),
    ("Value","GET","/api/v1/value",None),
    ("Documents","GET","/api/v1/{module}/documents/summary",None),
    ("Documents","GET","/api/v1/documents/{document_name}",None),
    ("Documents","GET","/api/v1/documents/{document_name}/recovery-guide",None),
    ("Notifications","GET","/api/v1/notifications",None),
    ("Notifications","GET","/api/v1/notifications/summary",None),
    ("Notifications","PUT","/api/v1/notifications/{id}/read",{}),
    ("Dashboard","GET","/api/v1/dashboard/farmer/{user_id}",None),
    ("Dashboard","GET","/api/v1/dashboard/student/{user_id}",None),
    ("Dashboard","GET","/api/v1/dashboard/jobseeker/{user_id}",None),
    ("Dashboard","GET","/api/v1/dashboard/entrepreneur/{user_id}",None),
    ("Dashboard","GET","/api/v1/dashboard/women-entrepreneur/{user_id}",None),
    ("Dashboard","GET","/api/v1/dashboard/startup/{user_id}",None),
    ("Dashboard","GET","/api/v1/dashboard/senior-citizen/{user_id}",None),
    ("Coach","GET","/api/v1/opportunities/{opportunity_id}/guidance",None),
    ("Intelligence","GET","/api/v1/farmer/services",None),
    ("Intelligence","GET","/api/v1/farmer/recommendations",None),
    ("Intelligence","GET","/api/v1/approval",None),
    ("Intelligence","GET","/api/v1/approval/farmer/{user_id}",None),
    ("Intelligence","GET","/api/v1/opportunity-health/{opportunity_id}",None),
    ("Intelligence","GET","/api/v1/trust/{opportunity_id}",None),
    ("Search","POST","/api/v1/search",{"query":"government job OBC Telangana","module":"jobseeker","user_id":user_id}),
    ("Voice","POST","/api/v1/voice/chat",{"message":"what jobs am I eligible for?","user_id":user_id,"module":"jobseeker"}),
    ("Voice","GET","/api/v1/voice/suggestions",None),
]

results = []
for tag, method, path, body in endpoints:
    url = BASE + s(path)
    try:
        if method == "GET": resp = requests.get(url, headers=H, timeout=15)
        elif method == "POST": resp = requests.post(url, headers=H, json=body, timeout=15)
        elif method == "PUT": resp = requests.put(url, headers=H, json=body, timeout=15)
        status = resp.status_code
        ok = status < 400
        snippet = "" if ok else resp.text[:100].replace("\n"," ")
    except Exception as e:
        status, ok, snippet = 0, False, str(e)[:80]
    results.append((tag, method, s(path), status, ok, snippet))

print(f"\n{'TAG':<16}{'METHOD':<7}{'PATH':<56}{'STATUS':<8}RESULT")
print("-"*110)
cur = None
for tag, method, path, status, ok, snippet in results:
    if tag != cur: print(); cur = tag
    r = "PASS" if ok else f"FAIL <- {snippet}"
    print(f"  {tag:<14}{method:<7}{path:<56}{status:<8}{r}")

passed = sum(1 for *_,ok,_ in results if ok)
print(f"\n{'='*110}\n  {passed} passed / {len(results)-passed} failed")

print("\n── FEATURE MAP ──")
checks = {
    "Regret banner":      lambda p: "missed-opportunities" in p,
    "Readiness ring":     lambda p: p.endswith("/readiness"),
    "Value tile":         lambda p: p.endswith("/value"),
    "Eligibility/run":    lambda p: "eligibility/run" in p,
    "Eligibility/questions": lambda p: "eligibility/questions" in p,
    "Opportunities feed": lambda p: "jobseeker/opportunities" in p,
    "Doc wallet summary": lambda p: "documents/summary" in p,
    "Scam Shield":        lambda p: "/search" in p,
    "Roadmap":            lambda p: "recovery-plan" in p,
    "Notifications":      lambda p: "/notifications" in p and "summary" not in p and "read" not in p,
    "Dashboard aggregate":lambda p: f"dashboard/jobseeker/{user_id}" in p,
    "Voice chat":         lambda p: "voice/chat" in p,
}
for feat, fn in checks.items():
    rows = [r for r in results if fn(r[2])]
    if not rows: print(f"  ⚪ {feat:<35} NO ROUTE")
    elif all(r[4] for r in rows): print(f"  GREEN  {feat}")
    else:
        bad = [f"{r[3]}" for r in rows if not r[4]]
        print(f"  BROKEN {feat:<35} status={bad}")