import re

with open("UDAAN AI (standalone).html", "r", encoding="utf-8") as f:
    content = f.read()

# Search for speech-to-text keywords
keywords = ["recognition", "speech", "webkitSpeechRecognition", "mic", "microphone", "record"]
for kw in keywords:
    matches = list(re.finditer(re.escape(kw), content, re.IGNORECASE))
    print(f"Keyword '{kw}': found {len(matches)} matches")
    if matches:
        print("First match snippet:")
        m = matches[0]
        start = max(0, m.start() - 100)
        end = min(len(content), m.end() + 100)
        print(content[start:end].strip())
        print("--------------------")
