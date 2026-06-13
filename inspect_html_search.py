import re
import json

content = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()

# Let's search for any occurrences of "localhost", "127.0.0.1", "5000", "fetch" or "axios" (even in escaped formats)
keywords = ["localhost", "127.0.0.1", "5000", "fetch", "axios", "http"]
for kw in keywords:
    matches = [m.start() for m in re.finditer(re.escape(kw), content, re.IGNORECASE)]
    print(f"Keyword '{kw}': found {len(matches)} matches")
    if matches:
        # Print a few samples
        for i, idx in enumerate(matches[:3]):
            start = max(0, idx - 50)
            end = min(len(content), idx + 50)
            print(f"  Match {i}: {repr(content[start:end])}")
