import json

file_path = "UDAAN AI (standalone).html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

template_start = content.find('<script type="__bundler/template">')
json_start = content.find('\n', template_start) + 1
json_end = content.find('</script>', json_start)

template_json = content[json_start:json_end].strip()
template = json.loads(template_json)

with open("template.html", "w", encoding="utf-8") as f:
    f.write(template)
print("Wrote template.html")
