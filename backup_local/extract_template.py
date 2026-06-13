import json
import re

with open("UDAAN AI (standalone).html", "r", encoding="utf-8") as f:
    content = f.read()

# Match the template content in Tag 4
match = re.search(r'<script type="__bundler/template">(.*?)</script>', content, re.DOTALL)
if match:
    raw_template = match.group(1).strip()
    # It is wrapped in quotes as a JSON string, let's load it
    try:
        html_content = json.loads(raw_template)
    except Exception:
        # If not direct JSON, maybe it's surrounded by quotes but escaped
        # Let's try parsing it by prepending/appending quotes
        if not raw_template.startswith('"'):
            raw_template = '"' + raw_template + '"'
        html_content = json.loads(raw_template)
    
    with open("extracted_template.html", "w", encoding="utf-8") as out:
        out.write(html_content)
    
    print("Successfully extracted template to extracted_template.html!")
    print(f"Size: {len(html_content)} characters")
else:
    print("Could not find template tag!")
