import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY", "").strip('"')
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)
print(response.status_code)
if response.status_code == 200:
    data = response.json()
    for model in data.get("models", []):
        print(model["name"])
else:
    print(response.text)
