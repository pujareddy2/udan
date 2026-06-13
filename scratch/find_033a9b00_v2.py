content = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()
sub = "033a9b00-867d-484d-ac3b-2ff654d116cc"
idx = content.find(sub)
print("Found index:", idx)
if idx != -1:
    print("Context around index:")
    print(repr(content[idx - 100:idx + len(sub) + 100]))
