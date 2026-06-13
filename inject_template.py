import json
import os

file_path = "UDAAN AI (standalone).html"
template_path = "template.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

with open(template_path, "r", encoding="utf-8") as f:
    template_html = f.read()

template_start = content.find('<script type="__bundler/template">')
json_start = content.find('\n', template_start) + 1
json_end = content.find('</script>', json_start)

# CRITICAL: JSON-encode the template, then escape any </script> sequences.
# Without this, the HTML parser terminates the outer <script> block early
# whenever it encounters </script> inside the JSON string — corrupting the JSON
# and causing every downstream error (broken src paths, SVG attribute escapes, etc.)
# Replacing '</' with '<\/' is safe: the JS engine still parses it correctly.
new_template_json = json.dumps(template_html).replace('</', '<\\/')

new_content = content[:json_start] + new_template_json + "\n  " + content[json_end:]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Injected updated template into {file_path}")
