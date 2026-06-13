with open('template.html', 'r', encoding='utf-8') as f:
    content = f.read()
# find register view
idx = content.find('view-register')
if idx == -1:
    print('view-register NOT FOUND')
else:
    print('Found view-register at:', idx)
    print(content[idx:idx+3500])
