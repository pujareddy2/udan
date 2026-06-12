import zipfile
import xml.etree.ElementTree as ET

z = zipfile.ZipFile('c:/Desktop/projects/stlw hackthon/udan/Udaan_AI_API_Documentation (1).docx')
xml_content = z.read('word/document.xml')
tree = ET.fromstring(xml_content)
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
text = '\n'.join([node.text for node in tree.findall('.//w:t', ns) if node.text])

with open('docx_content.txt', 'w', encoding='utf-8') as f:
    f.write(text)
