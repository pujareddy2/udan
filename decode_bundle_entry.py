import json, gzip, base64, re

with open('UDAAN AI (standalone).html', 'r', encoding='utf-8') as f:
    content = f.read()

script_id = 'b7e1da8a-a516-4d12-aab4-e9383c107ecf'

# Find the key and extract the whole entry object
idx = content.find(f'"{script_id}"')
print(f'Key at: {idx}')

# After the key, extract the value object { "mime": ..., "compressed": ..., "data": "..." }
after = content[idx:]
# Find matching braces for the value
obj_start = after.index('{')
depth = 0
obj_end = -1
for i, c in enumerate(after[obj_start:], obj_start):
    if c == '{':
        depth += 1
    elif c == '}':
        depth -= 1
        if depth == 0:
            obj_end = i + 1
            break

if obj_end == -1:
    print('Could not find end of entry object')
else:
    entry_str = after[obj_start:obj_end]
    print(f'Entry JSON (first 200): {entry_str[:200]}')
    entry = json.loads(entry_str)
    print('Keys:', list(entry.keys()))
    print('Compressed:', entry.get('compressed'))
    print('Mime:', entry.get('mime'))
    
    # Decode the current content
    data_b64 = entry['data']
    compressed_bytes = base64.b64decode(data_b64 + '==')  # add padding
    try:
        original_js = gzip.decompress(compressed_bytes).decode('utf-8')
        print(f'Decompressed successfully. Length: {len(original_js)}')
        print('First 200 chars:', original_js[:200])
    except Exception as e:
        print(f'Decompression error: {e}')
        # Try without extra padding
        try:
            original_js = gzip.decompress(base64.b64decode(data_b64)).decode('utf-8')
            print(f'Decompressed OK (no extra padding). Length: {len(original_js)}')
        except Exception as e2:
            print(f'Also failed without padding: {e2}')
