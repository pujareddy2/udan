content = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()
import re
matches = [m.start() for m in re.finditer(r'033a9b00', content)]
print("Matches for 033a9b00:", matches)
