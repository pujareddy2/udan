import os

# Check if the .env file exists and print its status
env_path = ".env"
print("Does .env exist?", os.path.exists(env_path))

if os.path.exists(env_path):
    # Read the raw bytes of the file
    with open(env_path, "rb") as f:
        content_bytes = f.read()
    print("Raw bytes of .env:", content_bytes)
    
    # Try reading as text
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            content_text = f.read()
        print("Text of .env:", repr(content_text))
    except Exception as e:
        print("Error reading as text:", repr(e))
