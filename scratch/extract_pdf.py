import pypdf

reader = pypdf.PdfReader('Sree_Checklist_and_Agent_Prompts.md.pdf')
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"

with open('scratch/Sree_Checklist_and_Agent_Prompts.txt', 'w', encoding='utf-8') as f:
    f.write(text)

print("Text extracted successfully to scratch/Sree_Checklist_and_Agent_Prompts.txt")
