from bs4 import BeautifulSoup
import json

html = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()
soup = BeautifulSoup(html, "html.parser")
template_el = soup.find("script", type="__bundler/template")

if template_el:
    text = template_el.string
    parsed = json.loads(text)
    print("Length of parsed template HTML:", len(parsed))
    pos = 21641
    print(f"Around index {pos} in decoded HTML template:")
    print(repr(parsed[pos - 50:pos + 50]))
