import json

with open("UDAAN AI (standalone).html", "r", encoding="utf-8", errors="replace") as f:
    html = f.read()

print(f"File size: {len(html):,} bytes")

# Check manifest
ms = html.find('<script type="__bundler/manifest">')
mjs = html.find('\n', ms) + 1
mje = html.find('</script>', mjs)
manifest = json.loads(html[mjs:mje])
print(f"Manifest assets: {len(manifest)}")

# Check template
ts = html.find('<script type="__bundler/template">')
tjs = html.find('\n', ts) + 1
tje = html.find('</script>', tjs)
template = json.loads(html[tjs:tje])
print(f"Template length: {len(template)} chars")

checks = [
    "udaan-landing-page",
    "hero-slide",
    "lc-problem",
    "lc-grid-3",
    "lc-grid-who",
    "lc-grid-feat",
    "astra-design-system",
    "bg-video",
    "liquid-glass",
    "Instrument Serif",
    "Barlow",
]
print("\nNew landing features present:")
for c in checks:
    found = c in template
    print(f"  [{'OK' if found else 'MISSING'}] {c}")

print("\nOld app features still present:")
old_checks = ["Login", "Register", "Dashboard", "root"]
for c in old_checks:
    found = c in template
    print(f"  [{'OK' if found else 'MISSING'}] {c}")
