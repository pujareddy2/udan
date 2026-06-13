"""
Generic bundle updater — replaces one or more script entries in the standalone HTML.
Usage: python repack_scripts.py <script_id_1> [script_id_2] ...
"""
import json, gzip, base64, sys

if len(sys.argv) < 2:
    print("Usage: python repack_scripts.py <script_id_1> [script_id_2] ...")
    sys.exit(1)

script_ids = sys.argv[1:]
html_path = 'UDAAN AI (standalone).html'

# Read standalone HTML
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f'Original HTML length: {len(content)}')

for script_id in script_ids:
    js_path = f'scripts_decoded/{script_id}.js'
    
    # Read the updated JS source
    with open(js_path, 'r', encoding='utf-8') as f:
        updated_js = f.read()
    print(f'\n--- Processing {script_id} ---')
    print(f'  JS source length: {len(updated_js)}')
    
    # Compress and encode
    compressed = gzip.compress(updated_js.encode('utf-8'))
    encoded = base64.b64encode(compressed).decode('ascii')
    
    # Build new entry JSON
    new_entry = json.dumps({"mime": "application/javascript", "compressed": True, "data": encoded}, separators=(',', ':'))
    print(f'  New entry length: {len(new_entry)}')
    
    # Find the script entry in the bundle
    key_str = f'"{script_id}"'
    idx = content.find(key_str)
    if idx == -1:
        print(f'  ERROR: Key {key_str} not found in HTML!')
        sys.exit(1)
    print(f'  Key found at position: {idx}')
    
    # Find the value object start (the { after the key's colon)
    after_key = content[idx + len(key_str):]
    colon_pos = after_key.index(':')
    after_colon = after_key[colon_pos+1:].lstrip()
    obj_rel_start = colon_pos + 1 + (len(after_key[colon_pos+1:]) - len(after_colon))
    
    # Find matching closing brace
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
        print(f'  ERROR: Could not find end of entry object for {script_id}')
        sys.exit(1)
    
    # Absolute positions
    abs_obj_start = idx + len(key_str) + obj_rel_start
    abs_obj_end = abs_obj_start + obj_end_rel
    
    old_entry = content[abs_obj_start:abs_obj_end]
    print(f'  Old entry length: {len(old_entry)}')
    
    # Verify old entry parses
    try:
        json.loads(old_entry)
        print(f'  Old entry parsed OK')
    except Exception as e:
        print(f'  WARNING: Old entry parse error: {e}')
    
    # Replace
    content = content[:abs_obj_start] + new_entry + content[abs_obj_end:]
    print(f'  Replaced successfully')

# Write updated HTML
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\nFinal HTML length: {len(content)}')
print(f'SUCCESS: Updated {len(script_ids)} script(s) in standalone HTML')

# Verify each
for script_id in script_ids:
    key_str = f'"{script_id}"'
    verify_idx = content.find(key_str)
    after_v = content[verify_idx + len(key_str):]
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
    decompressed = gzip.decompress(base64.b64decode(parsed_new['data'])).decode('utf-8')
    print(f'  Verified {script_id}: decompressed={len(decompressed)} chars, starts: {decompressed[:60]}...')
