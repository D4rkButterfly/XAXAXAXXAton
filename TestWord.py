from docx import Document
import re

def check_template(path):
    doc = Document(path)
    for i, p in enumerate(doc.paragraphs):
        full_text = p.text
        found = re.findall(r"{{(\w+)}}", full_text)
        run_text = "".join(r.text for r in p.runs)
        if found and full_text != run_text:
            print(f"⚠️ Параграф {i}: '{full_text}' — плейсхолдер разбит на runs!")
        elif found:
            print(f"✅ Параграф {i}: {found}")

check_template(r"C:\Users\ilyap\Downloads\Ш1.docx")