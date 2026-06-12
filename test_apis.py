import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_groq():
    api_key = os.getenv("GROQ_API_KEY", "").strip('"')
    print("Testing Groq API...")
    if not api_key:
        print("[FAILED] GROQ_API_KEY is not set in the .env file.")
        return
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": "Reply 'OK' if you are working."}]
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            text = data['choices'][0]['message']['content']
            print(f"[SUCCESS] Groq is working! Response: {text.strip()}")
        else:
            print(f"[FAILED] Groq failed! Status: {response.status_code}, Error: {response.text}")
    except Exception as e:
        print(f"[ERROR] Groq request error: {e}")

def test_serper():
    api_key = os.getenv("SERPER_API_KEY", "").strip('"')
    print("\nTesting Serper API...")
    url = "https://google.serper.dev/search"
    payload = {
        "q": "Indian government scholarships"
    }
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] Serper is working! Found {len(data.get('organic', []))} organic results.")
        else:
            print(f"[FAILED] Serper failed! Status: {response.status_code}, Error: {response.text}")
    except Exception as e:
        print(f"[ERROR] Serper request error: {e}")

if __name__ == "__main__":
    test_groq()
    test_serper()
