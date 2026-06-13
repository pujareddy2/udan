from bs4 import BeautifulSoup
import json

html = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()
soup = BeautifulSoup(html, "html.parser")
template_el = soup.find("script", type="__bundler/template")

if template_el:
    text = template_el.string
    print("BeautifulSoup parsed template tag string length:", len(text) if text else None)
    if text:
        # Check if starts/ends with double quotes
        print("Starts with quote:", text.startswith('"'))
        print("Ends with quote:", text.endswith('"'))
        print("First 50 chars:", repr(text[:50]))
        print("Last 50 chars:", repr(text[-50:]))
        
        # Where does JSON fail?
        try:
            parsed = json.loads(text)
            print("Successfully parsed!")
        except Exception as e:
            print("Parsing failed:", repr(e))
            # Let's inspect around the error position (if it says column)
            # Find the position of error from the message
            import re
            m = re.search(r'char (\d+)', str(e))
            if m:
                pos = int(m.group(1))
                print(f"Error at pos {pos}:")
                print("Context:")
                print(repr(text[max(0, pos - 50):min(len(text), pos + 50)]))
else:
    print("Script element not found via BeautifulSoup!")
