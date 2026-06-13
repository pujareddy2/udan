"""
Compare both HTML files and extract what's new in the landing file.
Focus on the template HTML (actual UI code) from each.
"""
import json, re

def extract_template(filepath):
    print(f"Reading {filepath}...")
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Find the bundler/template script
    ts = content.find('<script type="__bundler/template">')
    if ts == -1:
        print(f"  No bundler/template found in {filepath}")
        return None, content
    
    js = content.find('\n', ts) + 1
    je = content.find('</script>', js)
    json_str = content[js:je].strip()
    
    print(f"  Template JSON length: {len(json_str)}")
    
    try:
        template_html = json.loads(json_str)
        print(f"  Template HTML length: {len(template_html)}")
        return template_html, content
    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}")
        # Return raw content for inspection
        return json_str[:5000], content

def extract_manifest_keys(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    ms = content.find('<script type="__bundler/manifest">')
    if ms == -1:
        return set()
    mjs = content.find('\n', ms) + 1
    mje = content.find('</script>', mjs)
    try:
        manifest = json.loads(content[mjs:mje])
        return set(manifest.keys()), manifest
    except:
        return set(), {}

print("=== ANALYZING OLD FILE (UDAAN AI standalone) ===")
old_template, old_content = extract_template("UDAAN AI (standalone).html")
old_keys, old_manifest = extract_manifest_keys("UDAAN AI (standalone).html")
print(f"Old manifest UUIDs: {len(old_keys)}")

print()
print("=== ANALYZING NEW FILE (Landing standalone) ===")
new_template, new_content = extract_template("UDAAN AI - Landing (standalone).html")
new_keys, new_manifest = extract_manifest_keys("UDAAN AI - Landing (standalone).html")
print(f"New manifest UUIDs: {len(new_keys)}")

print()
print("=== COMPARISON ===")
new_only = new_keys - old_keys
old_only = old_keys - new_keys
shared = new_keys & old_keys
print(f"UUIDs only in NEW: {len(new_only)}")
print(f"UUIDs only in OLD: {len(old_only)}")
print(f"Shared UUIDs: {len(shared)}")

if new_only:
    print("\nNew assets (in landing but not standalone):")
    for k in sorted(new_only):
        info = new_manifest.get(k, {})
        print(f"  {k}: mime={info.get('mime','?')} size={len(info.get('data',''))} bytes")

# Save templates for inspection
if old_template and isinstance(old_template, str):
    with open('old_template_extracted.html', 'w', encoding='utf-8') as f:
        f.write(old_template[:50000])  # First 50K chars
    print("\nOld template saved to old_template_extracted.html (first 50K)")

if new_template and isinstance(new_template, str):
    with open('new_template_extracted.html', 'w', encoding='utf-8') as f:
        f.write(new_template)
    print(f"New template saved to new_template_extracted.html (full: {len(new_template)} chars)")
