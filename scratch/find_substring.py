content = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()
sub = "console, a);\\n  };\\n"
idx = content.find(sub)
print("Found substring at index:", idx)
if idx != -1:
    print("Context:")
    print(repr(content[idx - 50:idx + len(sub) + 50]))
