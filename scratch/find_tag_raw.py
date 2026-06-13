content = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()
# Let's search for "crossorigin" and print the context
import re
for m in re.finditer(r'crossorigin', content):
    idx = m.start()
    print("Match at index:", idx)
    print(repr(content[idx - 50:idx + 100]))
