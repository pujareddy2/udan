import requests
import json
from fastapi import FastAPI
from app.main import create_app
from fastapi.testclient import TestClient

# Create app
app = create_app()
client = TestClient(app)

# Test login
login_data = {
    "email": "job@gmail.com",
    "password": "123456"
}

response = client.post("/api/v1/auth/login", json=login_data)
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    print("\n✅ LOGIN SUCCESSFUL!")
else:
    print(f"\n❌ LOGIN FAILED")
