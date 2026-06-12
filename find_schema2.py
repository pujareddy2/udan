import re
import json
import base64

with open('UDAAN AI (standalone).html', 'r', encoding='utf-8') as f:
    data = f.read()

# The bundler usually stores files in a dictionary or base64 map.
# Let's find any mention of UDAAN_PROFILE_SCHEMA anywhere in the file.
for match in re.finditer(r'UDAAN_PROFILE_SCHEMA', data):
    start = max(0, match.start() - 100)
    end = min(len(data), match.end() + 100)
    print("MATCH AT", match.start())
    print(data[start:end])
    print("-" * 40)
