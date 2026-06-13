import json, gzip, base64, re

with open('UDAAN AI (standalone).html', 'r', encoding='utf-8') as f:
    content = f.read()

script_id = 'b7e1da8a-a516-4d12-aab4-e9383c107ecf'

# Find the JSON bundle object in the page
# It looks like: window.__UDAAN_BUNDLE__ = {...} or similar
# Let's find the start of the bundle JSON
bundle_var_patterns = [
    r'window\.__UDAAN_BUNDLE__\s*=\s*',
    r'var\s+__bundle\s*=\s*',
    r'__BUNDLE__\s*=\s*',
]

found = False
for pat in bundle_var_patterns:
    m = re.search(pat, content)
    if m:
        print(f'Found bundle via pattern: {pat} at {m.start()}')
        found = True
        break

if not found:
    # Try to locate the JSON directly by finding the key
    idx = content.find(f'"{script_id}"')
    if idx == -1:
        idx = content.find(f"'{script_id}'")
    print(f'Key found at position: {idx}')
    # Find the enclosing JSON object start
    # Walk backwards to find the opening brace of the object containing this key
    # Look for the script tag or variable assignment before it
    pre = content[max(0,idx-500):idx]
    print(f'Pre-context: {pre[-300:]}')
