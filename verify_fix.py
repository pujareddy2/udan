content = open('UDAAN AI (standalone).html', 'r', encoding='utf-8').read()

# Find the bundler/template script tag
ts = content.find('<script type="__bundler/template">')
if ts == -1:
    print('ERROR: bundler/template not found')
else:
    print('Found bundler/template at pos:', ts)
    js = content.find('\n', ts) + 1
    je = content.find('</script>', js)
    snippet = content[js:js+100]
    print('JSON starts with:', repr(snippet))
    print('Length of template JSON:', je - js)
    sub = content[js:je]
    count = sub.count('</script>')
    esc_count = sub.count('<\\/script>')
    print(f'Unescaped </script> count in JSON: {count}')
    print(f'Escaped <\\/script> count in JSON: {esc_count}')

# Check for manifest section too
ms = content.find('<script type="__bundler/manifest">')
if ms == -1:
    print('ERROR: bundler/manifest not found')
else:
    print('\nFound bundler/manifest at pos:', ms)
    mjs = content.find('\n', ms) + 1
    mje = content.find('</script>', mjs)
    print('Manifest length:', mje - mjs, 'chars')
