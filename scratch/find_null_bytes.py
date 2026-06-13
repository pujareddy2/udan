content = open("UDAAN AI (standalone).html", "rb").read()
null_bytes = [i for i, b in enumerate(content) if b == 0]
print("Total null bytes:", len(null_bytes))
print("Indices of null bytes:", null_bytes[:10])
