import re
import json

content = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()
match = re.search(r'<script type="__bundler/template">(.*?)</script>', content, re.DOTALL)
if match:
    raw = match.group(1).strip()
    print("Length:", len(raw))
    print("Starts with double quote:", raw.startswith('"'))
    print("Ends with double quote:", raw.endswith('"'))
    print("Last 20 characters of raw:")
    print(repr(raw[-20:]))
