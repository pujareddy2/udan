import os
import requests
from dotenv import load_dotenv

load_dotenv()

def call_gemini(prompt: str) -> str | None:
    """
    Calls the Groq API (named call_gemini for legacy drop-in compatibility)
    Uses llama-3.3-70b-versatile.
    """
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("LLM_API_KEY")
    if not api_key:
        print("Warning: GROQ_API_KEY not found in .env")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1 # Low temp for structured JSON extraction
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"LLM API Error: {e}")
        return None
