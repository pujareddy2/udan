import gzip, base64, json

with open('UDAAN AI (standalone).html', 'r', encoding='utf-8') as f:
    content = f.read()

script_id = 'b7e1da8a-a516-4d12-aab4-e9383c107ecf'
key_str = '"' + script_id + '"'
idx = content.find(key_str)
after = content[idx + len(key_str):]
colon = after.index(':')
after_c = after[colon+1:].lstrip()
depth = 0
for i, c in enumerate(after_c):
    if c == '{': depth += 1
    elif c == '}':
        depth -= 1
        if depth == 0:
            obj = after_c[:i+1]
            break
parsed = json.loads(obj)
js = gzip.decompress(base64.b64decode(parsed['data'])).decode('utf-8')
print('trustScore >= 90 present:', 'trustScore >= 90' in js)
print('Official Govt present:', 'Official Govt' in js)
print('Trust/Source section present:', 'Trust / Source Chips' in js)
print('globe icon chip:', 'name="globe"' in js or "name='globe'" in js)
