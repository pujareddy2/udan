import httpx
import json

base_url = "http://localhost:8000/api/v1"

def test():
    print("Testing /health...")
    r = httpx.get("http://localhost:8000/health")
    print(r.status_code, r.json())

    print("\nTesting /opportunities/recommended...")
    r = httpx.get(f"{base_url}/opportunities/recommended?user_id=5")
    print(r.status_code)
    print(json.dumps(r.json(), indent=2)[:1000])

    print("\nTesting /jobseeker/roadmap...")
    r = httpx.get(f"{base_url}/jobseeker/roadmap?user_id=5")
    print(r.status_code, r.json())

    print("\nTesting /scam/scan flagged...")
    payload = {
        "text": "Earn Rs 5000 daily working from home! Join our Telegram group. Refundable security deposit of Rs 1500 mandatory."
    }
    r = httpx.post(f"{base_url}/scam/scan", json=payload)
    print(r.status_code, r.json())

    print("\nTesting /scam/scan safe...")
    payload = {
        "text": "Senior Software Engineer needed for full-time role at Google. Proficiency in Python and SQL required."
    }
    r = httpx.post(f"{base_url}/scam/scan", json=payload)
    print(r.status_code, r.json())

if __name__ == "__main__":
    test()
