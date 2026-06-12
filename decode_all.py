import re
import base64

with open('UDAAN AI (standalone).html', 'r', encoding='utf-8') as f:
    data = f.read()

with open('decoded_all.txt', 'w', encoding='utf-8') as out:
    for m in re.finditer(r'base64,([A-Za-z0-9+/=]+)', data):
        try:
            b64 = m.group(1)
            decoded = base64.b64decode(b64).decode('utf-8', errors='ignore')
            out.write(decoded)
            out.write('\n\n---NEXT---\n\n')
        except Exception as e:
            pass

print('Done decoding.')
