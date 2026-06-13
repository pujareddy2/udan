"""
Merge the new LANDING PAGE features into the old UDAAN AI (standalone).html.

The key insight: the bundler stores the template as a JSON string inside a
<script type="__bundler/template"> block. Any </script> inside that JSON string
MUST be written as <\/script> to avoid the HTML parser prematurely closing the
script tag. json.dumps() does NOT do this automatically, so we must do it manually.
"""
import json, re

SCRIPT_CLOSE = '</script>'
SCRIPT_CLOSE_SAFE = '<\\/script>'  # safe inside a JSON string inside a <script> block

def safe_json_for_script(obj):
    """JSON-encode obj so the result is safe to embed inside a <script> block."""
    s = json.dumps(obj, ensure_ascii=False)
    return s.replace(SCRIPT_CLOSE, SCRIPT_CLOSE_SAFE)

print("Reading files...")
with open("UDAAN AI (standalone).html", "r", encoding="utf-8", errors="replace") as f:
    old_html = f.read()

with open("UDAAN AI - Landing (standalone).html", "r", encoding="utf-8", errors="replace") as f:
    new_html = f.read()

def parse_bundler_json(html, script_type):
    """Extract and JSON-parse the content of <script type="..."> block."""
    tag = f'<script type="{script_type}">'
    ts = html.find(tag)
    if ts == -1:
        raise ValueError(f"Script type {script_type} not found")
    content_start = html.index('\n', ts) + 1
    # Find the end: the JSON is on one big line ending with \n before </script>
    content_end = html.find('\n</script>', content_start)
    if content_end == -1:
        content_end = html.find('</script>', content_start)
    json_str = html[content_start:content_end].strip()
    return json.loads(json_str)

def replace_block(html, script_type, new_json):
    """Replace the content of a <script type="..."> block with new_json."""
    tag = f'<script type="{script_type}">'
    ts = html.find(tag)
    if ts == -1:
        print(f"WARNING: {script_type} not found")
        return html
    content_start = html.index('\n', ts) + 1
    content_end = html.find('\n</script>', content_start)
    if content_end == -1:
        content_end = html.find('</script>', content_start)
    return html[:content_start] + new_json + '\n' + html[content_end:]

print("Extracting manifests and templates...")
old_manifest = parse_bundler_json(old_html, "__bundler/manifest")
old_template = parse_bundler_json(old_html, "__bundler/template")

new_manifest = parse_bundler_json(new_html, "__bundler/manifest")
new_template = parse_bundler_json(new_html, "__bundler/template")

print(f"Old: {len(old_manifest)} assets, template {len(old_template)} chars")
print(f"New: {len(new_manifest)} assets, template {len(new_template)} chars")

# Merge manifests
merged_manifest = {**old_manifest, **new_manifest}
print(f"Merged: {len(merged_manifest)} assets")

# Extract Astra design-system CSS from new template
astra_css_blocks = re.findall(r'<style>(.*?)</style>', new_template, re.DOTALL)
astra_css = '\n'.join(astra_css_blocks)

# Extract body content from new template
body_start = new_template.find('<body>')
body_end = new_template.find('</body>')
new_body_html = new_template[body_start + 6:body_end].strip()

# Build landing section (wrapped div, hidden initially)
landing_section = """
  <!-- =====================================================
       UDAAN AI LANDING PAGE (merged from Landing file)
       Shown on fresh load; hidden when user enters the app.
       ===================================================== -->
  <div id="udaan-landing-page" style="display:none;">
""" + new_body_html + """
  </div>

  <!-- Landing to App routing -->
  <script>
  (function () {
    function showLanding() {
      var lp = document.getElementById('udaan-landing-page');
      var root = document.getElementById('root');
      if (lp) lp.style.display = 'block';
      if (root) root.style.display = 'none';
      document.body.style.background = '#000';
    }
    function showApp() {
      var lp = document.getElementById('udaan-landing-page');
      var root = document.getElementById('root');
      if (lp) lp.style.display = 'none';
      if (root) { root.style.display = ''; }
      document.body.style.background = '';
    }
    function decide() {
      var h = window.location.hash;
      if (!h || h === '#' || h === '#/' || h === '#landing' || h === '#home') {
        showLanding();
      } else {
        showApp();
      }
    }
    window.addEventListener('load', function () {
      decide();
      var lp = document.getElementById('udaan-landing-page');
      if (lp) {
        lp.addEventListener('click', function (e) {
          var el = e.target.closest('a[href]');
          if (el) {
            var href = el.getAttribute('href');
            if (href === 'login.html' || href === 'register.html') {
              e.preventDefault();
              showApp();
              window.location.hash = href === 'register.html' ? '#register' : '#login';
            }
          }
        });
      }
      window.addEventListener('hashchange', decide);
    });
  })();
  </script>
"""

# Inject Astra CSS into old template's <head>
astra_tag = "\n<style id='astra-design-system'>\n" + astra_css + "\n</style>\n"
modified_template = old_template.replace('</head>', astra_tag + '</head>', 1)

# Inject landing section after <body>
modified_template = modified_template.replace('<body>', '<body>\n' + landing_section, 1)

print(f"Modified template: {len(modified_template)} chars")

# Serialize safely
manifest_json = safe_json_for_script(merged_manifest)
template_json = safe_json_for_script(modified_template)

# Rebuild the HTML
print("Rebuilding HTML...")
merged_html = replace_block(old_html, "__bundler/manifest", manifest_json)
merged_html = replace_block(merged_html, "__bundler/template", template_json)

output = "UDAAN AI (standalone).html"
print(f"Writing {len(merged_html):,} bytes to {output}...")
with open(output, "w", encoding="utf-8") as f:
    f.write(merged_html)

print("Done!")
print()
print("NEW FEATURES ADDED TO STANDALONE HTML:")
print("  [+] Background video (cinematic fullscreen loop)")
print("  [+] Astra design system (Barlow + Instrument Serif fonts, CSS tokens)")
print("  [+] Glassmorphism .liquid-glass / .liquid-glass-strong components")
print("  [+] Landing hero with animated 3-slide carousel")
print("  [+] Smooth-scroll navigation bar with mobile hamburger menu")
print("  [+] Trust strip (government-verified sources, 7 communities)")
print("  [+] Problem band")
print("  [+] How it works section (3 glass cards)")
print("  [+] Built for every Indian - communities grid (7 categories)")
print("  [+] Features section (7 capability cards)")
print("  [+] Why trust us section")
print("  [+] Final CTA section")
print("  [+] Seamless landing->app routing (hash-based, no page reload)")
print("  [+] All OLD features preserved (login, register, dashboard, etc.)")
