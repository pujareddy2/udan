import os
import re

# Read standalone HTML
standalone = open('UDAAN AI (standalone).html', 'r', encoding='utf-8').read()

# Read updated JS
script_id = 'b7e1da8a-a516-4d12-aab4-e9383c107ecf'
updated_js = open(f'scripts_decoded/{script_id}.js', 'r', encoding='utf-8').read()

# Build pattern to find inlined script with this id
pattern = r'(<script[^>]*id=["\']?' + re.escape(script_id) + r'["\']?[^>]*>)(.*?)(</script>)'
match = re.search(pattern, standalone, re.DOTALL | re.IGNORECASE)

if match:
    print(f'Found script tag at: {match.start()} - {match.end()}')
    replacement = match.group(1) + updated_js + match.group(3)
    standalone = standalone[:match.start()] + replacement + standalone[match.end():]
    with open('UDAAN AI (standalone).html', 'w', encoding='utf-8') as f:
        f.write(standalone)
    print('SUCCESS: Updated standalone HTML')
else:
    # Script might be referenced by src not embedded
    src_pattern = r'src=["\']?' + re.escape(script_id) + r'["\']?'
    m2 = re.search(src_pattern, standalone)
    if m2:
        print(f'Found as external src reference at: {m2.start()} - it is loaded externally, no rebuild needed')
    else:
        # Look for src attr with path
        m3 = re.search(script_id, standalone)
        if m3:
            print(f'Found reference to script at pos: {m3.start()}')
            print(standalone[max(0, m3.start()-100):m3.end()+100])
        else:
            print('Script ID NOT found in standalone HTML at all')
