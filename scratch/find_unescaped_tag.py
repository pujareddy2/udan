content = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()
# Let's search for "crossorigin=\"anonymous\"></script>" or similar
sub = "crossorigin=\\\"anonymous\\\"></script>"
idx = content.find(sub)
print("Found index with literal </script>:", idx)
if idx != -1:
    print("Context in raw file:")
    print(repr(content[idx - 50:idx + len(sub) + 50]))
else:
    # Try searching for "</script>"
    print("Trying searching for plain </script> in raw file...")
    import re
    matches = [m.start() for m in re.finditer(r'</script>', content, re.IGNORECASE)]
    print("Matches for </script> in raw file:", matches)
    for m in matches:
        print(f"Context at {m}:", repr(content[m-50:m+50]))
