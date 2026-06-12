import json

file_path = "UDAAN AI (standalone).html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

manifest_start = content.find('<script type="__bundler/manifest">')
json_start = content.find('\n', manifest_start) + 1
json_end = content.find('</script>', json_start)

manifest_json = content[json_start:json_end]

# It is a JSON object mapping IDs to script contents.
try:
    manifest = json.loads(manifest_json)
    with open("manifest_dump.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print("Extracted manifest")
except Exception as e:
    print("Error parsing manifest:", e)
