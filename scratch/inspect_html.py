import re

content = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()

pattern = re.compile(r'(<script[^>]*>)(.*?)(</script>)', re.DOTALL)
for i, match in enumerate(pattern.finditer(content)):
    tag = match.group(1)
    body = match.group(2)
    print(f"Script {i}: Tag={tag}, Body length={len(body)}")
    print(f"  Start: {repr(body[:100])}")
    print(f"  End  : {repr(body[-100:])}")
