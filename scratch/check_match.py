import re

content = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()
match = re.search(r'<script type="__bundler/template">(.*?)</script>', content, re.DOTALL)
if match:
    print("Match group 0 start/end:", match.span(0))
    print("Match group 1 start/end:", match.span(1))
    print("Exact content around group 0 end:")
    end_idx = match.end(0)
    print(repr(content[end_idx - 20:end_idx + 20]))
else:
    print("No match")
