import os
import sys
from dotenv import load_dotenv
from groq import Groq

# Configure stdout to use UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Load environment variables
load_dotenv()

key = os.getenv("GROQ_API_KEY")

print("=========================================")
print("          GROQ API KEY CHECK             ")
print("=========================================")

if not key:
    print("[ERROR] GROQ_API_KEY environment variable is NOT set.")
    print("Please set it in your environment or add it to a '.env' file in the root directory:")
    print("GROQ_API_KEY=your_actual_api_key_here")
else:
    print(f"[SUCCESS] Key found: Starts with '{key[:6]}...' (Total length: {len(key)})")
    print("Testing connection to Groq API...")
    try:
        client = Groq(api_key=key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say hello!"}],
            temperature=0.2
        )
        print("[SUCCESS] Response from Groq:")
        print(response.choices[0].message.content.strip())
    except Exception as e:
        print("[ERROR] FAILED! Connection error or invalid API key:")
        print(repr(e))

print("=========================================")
