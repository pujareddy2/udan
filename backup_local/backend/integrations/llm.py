import os
from typing import Optional
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env
load_dotenv()

key = os.getenv("GROQ_API_KEY")
print("KEY LOADED, length:", len(key) if key else 0)

def call_gemini(prompt: str) -> Optional[str]:
    """
    Calls the Groq API (using llama-3.3-70b-versatile) with the given prompt.
    Keeps the function name 'call_gemini' identical so no other files need changes.
    Returns None on any error.
    """
    try:
        current_key = os.getenv("GROQ_API_KEY")
        if not current_key:
            raise ValueError("Groq API key is missing.")

        client = Groq(api_key=current_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        if response and response.choices and response.choices[0].message:
            return response.choices[0].message.content
        return None
    except Exception as e:
        print("LLM ERROR:", repr(e))
        return None
