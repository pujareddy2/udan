from bs4 import BeautifulSoup
import json

html = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()
soup = BeautifulSoup(html, "html.parser")
manifest_el = soup.find("script", type="__bundler/manifest")

if manifest_el:
    text = manifest_el.string
    print("Manifest length:", len(text))
    try:
        parsed = json.loads(text)
        print("Manifest successfully parsed in Python!")
    except Exception as e:
        print("Manifest parsing failed in Python:", repr(e))
        import re
        m = re.search(r'char (\d+)', str(e))
        if m:
            pos = int(m.group(1))
            print(f"Error at position {pos}:")
            print(repr(text[max(0, pos - 50):min(len(text), pos + 50)]))
else:
    print("Manifest element not found")
