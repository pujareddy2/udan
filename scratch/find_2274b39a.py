content = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()
sub = "2274b39a"
import re
matches = [m.start() for m in re.finditer(re.escape(sub), content)]
print("All matches for 2274b39a:", matches)
for m in matches:
    print(f"Context at {m}:")
    print(repr(content[m - 100:m + len(sub) + 100]))
