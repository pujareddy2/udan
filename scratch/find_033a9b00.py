content = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()
sub = '</script>\\n<script src=\\"033a9b00-867d-484d-ac3b-2ff654d116cc\\"'
idx = content.find(sub)
print("Found index of sub 033a9b00:", idx)
if idx != -1:
    print("Context around 033a9b00:")
    print(repr(content[idx - 50:idx + len(sub) + 50]))
