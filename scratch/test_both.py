import re

content = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()

match1 = re.search(r'<script type="__bundler/template">(.*?)</script>', content, re.DOTALL)
if match1:
    print("Match 1 group 1 span:", match1.span(1))
    print("Match 1 group 1 length:", len(match1.group(1)))
    print("Match 1 group 1 strip length:", len(match1.group(1).strip()))
    print("Match 1 group 1 end chars:", repr(match1.group(1)[-50:]))
else:
    print("Match 1 not found")

match2 = re.search(r'<script type="__bundler/template">(.*?)</script>', content) # without DOTALL
if match2:
    print("Match 2 group 1 span:", match2.span(1))
else:
    print("Match 2 not found")
