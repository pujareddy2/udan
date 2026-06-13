from bs4 import BeautifulSoup

html = open("UDAAN AI (standalone).html", "r", encoding="utf-8").read()
soup = BeautifulSoup(html, "html.parser")
template_el = soup.find("script", type="__bundler/template")

if template_el:
    text = template_el.string
    print("Length of raw text:", len(text))
    pos = 21641
    print(f"Around index {pos} in raw JSON string (text):")
    print(repr(text[pos - 50:pos + 50]))
