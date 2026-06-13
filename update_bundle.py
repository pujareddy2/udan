import json, gzip, base64, re

script_id = 'b7e1da8a-a516-4d12-aab4-e9383c107ecf'

# Read the updated JS source
with open(f'scripts_decoded/{script_id}.js', 'r', encoding='utf-8') as f:
    updated_js = f.read()

print(f'Updated JS length: {len(updated_js)}')

# Compress it
compressed = gzip.compress(updated_js.encode('utf-8'))
encoded = base64.b64encode(compressed).decode('ascii')
print(f'Encoded length: {len(encoded)}')

# New entry JSON
new_entry = json.dumps({"mime": "application/javascript", "compressed": True, "data": encoded}, separators=(',', ':'))
print(f'New entry length: {len(new_entry)}')

# Read standalone HTML
with open('UDAAN AI (standalone).html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the script entry in the bundle
idx = content.find(f'"{script_id}"')
print(f'Key at: {idx}')

# Find the value object start (the { after the key's colon)
after_key = content[idx + len(f'"{script_id}"'):]
# skip whitespace and colon
colon_pos = after_key.index(':')
after_colon = after_key[colon_pos+1:].lstrip()
# Find the matching brace
obj_rel_start = colon_pos + 1 + (len(after_key[colon_pos+1:]) - len(after_colon))

depth = 0
obj_end_rel = -1
for i, c in enumerate(after_colon):
    if c == '{':
        depth += 1
    elif c == '}':
        depth -= 1
        if depth == 0:
            obj_end_rel = i + 1
            break

if obj_end_rel == -1:
    print('ERROR: Could not find end of entry object')
    exit(1)

# Absolute positions in original content
abs_obj_start = idx + len(f'"{script_id}"') + colon_pos + 1 + (len(after_key[colon_pos+1:]) - len(after_colon))
abs_obj_end = abs_obj_start + obj_end_rel

old_entry = content[abs_obj_start:abs_obj_end]
print(f'Old entry length: {len(old_entry)}')
print(f'Old entry start (first 80): {old_entry[:80]}')

# Verify it parses correctly
try:
    parsed = json.loads(old_entry)
    print(f'Old entry parsed OK. Keys: {list(parsed.keys())}')
except Exception as e:
    print(f'WARNING: Old entry JSON parse error: {e}')

# Replace
new_content = content[:abs_obj_start] + new_entry + content[abs_obj_end:]
print(f'Old HTML length: {len(content)}')
print(f'New HTML length: {len(new_content)}')

with open('UDAAN AI (standalone).html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('SUCCESS: Standalone HTML updated with compressed new script')

# Verify the replacement
verify_idx = new_content.find(f'"{script_id}"')
after_v = new_content[verify_idx + len(f'"{script_id}"'):]
colon_v = after_v.index(':')
after_colon_v = after_v[colon_v+1:].lstrip()
depth_v = 0
for i, c in enumerate(after_colon_v):
    if c == '{':
        depth_v += 1
    elif c == '}':
        depth_v -= 1
        if depth_v == 0:
            new_obj = after_colon_v[:i+1]
            break
parsed_new = json.loads(new_obj)
decompressed_check = gzip.decompress(base64.b64decode(parsed_new['data'])).decode('utf-8')
print(f'Verification: decompressed length={len(decompressed_check)}, starts with: {decompressed_check[:80]}')
print('Trust/Source Chips present:', 'Trust/Source Chips' in decompressed_check)
