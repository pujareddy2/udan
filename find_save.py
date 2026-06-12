with open('UDAAN AI (standalone).html', 'r', encoding='utf-8') as f:
    data = f.read()

idx = data.find('Save Profile')
if idx != -1:
    print('Found Save Profile at', idx)
    print(data[max(0, idx-100):idx+500])
else:
    print('Not found')
