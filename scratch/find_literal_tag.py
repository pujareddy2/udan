import re

content = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()
match = re.search(r'<script type="__bundler/template">(.*?)</script>', content, re.DOTALL)
if match:
    body = match.group(1)
    # Search for </script> (case-insensitive) in body
    matches = [m.start() for m in re.finditer(r'</script>', body, re.IGNORECASE)]
    print("Matches for </script> inside template body:", matches)
    for m in matches:
        print(f"Context in body at {m}:")
        print(repr(body[max(0, m - 50):min(len(body), m + 50)]))
else:
    print("Template not found")
