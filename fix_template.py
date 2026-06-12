import json

file_path = "UDAAN AI (standalone).html"
template_path = "template.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

with open(template_path, "r", encoding="utf-8") as f:
    template_html = f.read()

template_start = content.find('<script type="__bundler/template">')
json_start = content.find('\n', template_start) + 1

# Escape the </script> tag so it doesn't break out of the HTML script block
new_template_json = json.dumps(template_html)
new_template_json = new_template_json.replace("</script>", "<\\/script>")

# Since the rest of the file is just the closing tags, we can just hardcode them
new_content = content[:json_start] + new_template_json + "\n  </script>\n</body>\n</html>\n"

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Fixed and injected template properly.")
