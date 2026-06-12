import json
import base64
import gzip
import os

os.makedirs('scripts_decoded', exist_ok=True)
d = json.load(open('manifest_dump.json'))

for k, v in d.items():
    if isinstance(v, dict) and v.get('compressed') and 'data' in v:
        try:
            compressed_data = base64.b64decode(v['data'])
            decoded = gzip.decompress(compressed_data).decode('utf-8')
            with open(f'scripts_decoded/{k}.js', 'w', encoding='utf-8') as f:
                f.write(decoded)
        except Exception as e:
            print(f"Error decoding {k}: {e}")
    else:
        with open(f'scripts_decoded/{k}.js', 'w', encoding='utf-8') as f:
            f.write(str(v))
print("Decoded scripts")
