import base64
import re
with open('UDAAN AI (standalone).html', 'r', encoding='utf-8') as f:
    data = f.read()

for m in re.finditer(r'src="data:text/(?:javascript|babel|plain);base64,([A-Za-z0-9+/=]+)"', data):
    b64 = m.group(1)
    try:
        decoded = base64.b64decode(b64).decode('utf-8')
        if 'UDAAN_PROFILE_SCHEMA' in decoded:
            print('Found UDAAN_PROFILE_SCHEMA in script of length', len(decoded))
            idx = decoded.find('UDAAN_PROFILE_SCHEMA')
            print(decoded[max(0, idx-50):idx+500])
    except Exception as e:
        print('Error decoding', e)
