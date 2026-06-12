import base64
import json

with open('UDAAN AI (standalone).html', 'r', encoding='utf-8') as f:
    data = f.read()

start = data.find('__bundler_data = {')
if start != -1:
    end = data.find('};', start)
    json_str = data[start+17:end+1]
    bundler_data = json.loads(json_str)
    count = 0
    for k, v in bundler_data.items():
        try:
            if v.startswith('data:text/'):
                b64 = v.split('base64,')[1]
                decoded = base64.b64decode(b64).decode('utf-8')
                with open(f'script_{count}.js', 'w', encoding='utf-8') as out:
                    out.write(decoded)
                if 'UDAAN_PROFILE_SCHEMA' in decoded:
                    print(f'Found schema in script_{count}.js (original id {k})')
                count += 1
        except Exception as e:
            pass
