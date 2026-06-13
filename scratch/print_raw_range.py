content = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()
idx = 21700747 + 21641
print("Length of file:", len(content))
print("Target index:", idx)
print("Context:")
print(repr(content[idx - 100:idx + 100]))
