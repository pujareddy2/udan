import json
import re

file_path = "UDAAN AI (standalone).html"

print("Reading file...")
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Find the template script tag
template_start = content.find('<script type="__bundler/template">')
if template_start == -1:
    print("Template not found!")
    exit(1)

json_start = content.find('\n', template_start) + 1
json_end = content.find('</script>', json_start)

template_json = content[json_start:json_end].strip()
print(f"Template JSON length: {len(template_json)}")

try:
    template = json.loads(template_json)
except Exception as e:
    print(f"JSON parsing failed: {e}")
    exit(1)

print(f"Decoded template length: {len(template)}")

# Let's search for Username and the login logic
# We need to change Username to Email Address
# And implement the fetch API.

# To inspect where login is, let's dump the surroundings of 'Username'
idx = template.find('Username')
if idx != -1:
    print("\n--- Context around 'Username' ---")
    print(template[max(0, idx-200):min(len(template), idx+200)])
else:
    print("Username not found in template.")

idx2 = template.find('handleLogin')
if idx2 != -1:
    print("\n--- Context around 'handleLogin' ---")
    print(template[max(0, idx2-400):min(len(template), idx2+400)])
else:
    print("handleLogin not found in template.")

