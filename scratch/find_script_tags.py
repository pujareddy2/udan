import re

content = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()

# Find all occurrences of </script> (case-insensitive) in the entire file
matches = [m.start() for m in re.finditer(r'</script>', content, re.IGNORECASE)]
print("Total </script> matches:", len(matches))
for i, idx in enumerate(matches):
    start = max(0, idx - 50)
    end = min(len(content), idx + 50)
    print(f"Match {i} (index {idx}):")
    print(repr(content[start:end]))
