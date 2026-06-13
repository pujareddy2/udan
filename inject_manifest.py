import json
import base64
import gzip
import os

print("Loading manifest_dump.json...")
manifest = json.load(open('manifest_dump.json'))

files_to_update = [
    '4f088cda-a00e-40fa-90c8-2eb2398d268b',
    'c33aa38d-654c-4053-bad9-41e46538669f',
    'b7e1da8a-a516-4d12-aab4-e9383c107ecf',
    '615a609b-2f33-4430-bf48-494bb7f47957',
    '68bb7126-d744-4b6f-a0bf-a718510a5474'
]

for k in files_to_update:
    path = f'scripts_decoded/{k}.js'
    print(f"Updating {k} from {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        decoded_text = f.read()
    
    compressed = gzip.compress(decoded_text.encode('utf-8'))
    b64 = base64.b64encode(compressed).decode('utf-8')
    manifest[k]['data'] = b64

# Now inject the updated manifest back into the HTML file
html_path = 'UDAAN AI (standalone).html'
print(f"Reading {html_path}...")
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

manifest_start = content.find('<script type="__bundler/manifest">')
json_start = content.find('\n', manifest_start) + 1
json_end = content.find('</script>', json_start)

# Convert to JSON string (without indent to save space)
print("Stringifying manifest...")
manifest_json_str = json.dumps(manifest)

print("Injecting...")
new_content = content[:json_start] + manifest_json_str + "\n  " + content[json_end:]

print(f"Writing {html_path}...")
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done!")
