import base64
import json

file_path = 'UDAAN AI (standalone).html'
with open(file_path, 'r', encoding='utf-8') as f:
    data = f.read()

# Read the two scripts we modified
with open(r'scripts_decoded\4f088cda-a00e-40fa-90c8-2eb2398d268b.js', 'r', encoding='utf-8') as f:
    script_4f = f.read()
with open(r'scripts_decoded\c33aa38d-654c-4053-bad9-41e46538669f.js', 'r', encoding='utf-8') as f:
    script_c3 = f.read()

b64_4f = base64.b64encode(script_4f.encode('utf-8')).decode('utf-8')
b64_c3 = base64.b64encode(script_c3.encode('utf-8')).decode('utf-8')

import re
# We need to find the base64 chunks for these in UDAAN AI (standalone).html
# The HTML contains {"mime":"application/javascript","compressed":true,"data":"H4sIAAAAAAA...
# Wait! In UDAAN AI (standalone).html, it was actually embedded in base64 string inside the template.html block or script tags.
# Actually, the original base64 was extracted by edit_frontend.py? No, they are inside template.html maybe?
# Let's replace the base64 string in UDAAN AI (standalone).html where it says src="data:text/javascript;base64,... No, that regex failed earlier.
# Wait, where are the base64 strings located?
# Let's check `manifest_dump.json` or just search for the old base64 strings!
