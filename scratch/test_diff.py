import re

content = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()
match = re.search(r'<script type="__bundler/template">(.*?)</script>', content, re.DOTALL)
if match:
    g1 = match.group(1)
    g1_strip = g1.strip()
    print("g1 length:", len(g1))
    print("g1_strip length:", len(g1_strip))
    print("span difference:", match.end(1) - match.start(1))
else:
    print("No match")
