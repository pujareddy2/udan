import re

content = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()
pattern = re.compile(r'(<script[^>]*>)(.*?)(</script>)', re.DOTALL)
matches = list(pattern.finditer(content))
if matches:
    print(matches[0].group(2))
