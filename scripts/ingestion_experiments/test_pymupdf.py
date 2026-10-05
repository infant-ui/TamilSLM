import fitz

def fix_text(text):
    try:
        return text.encode('cp437').decode('utf-8')
    except Exception:
        return text 

pdf_path = r"data\books\class_8\Tamil\textbooks\Maths\Class_8_Mathematics_Tamil_2025.pdf"
doc = fitz.open(pdf_path)
page = doc[294] # Page 295
raw_text = page.get_text()

fixed_text = fix_text(raw_text)

with open("pymupdf_fixed_294.md", "w", encoding="utf-8") as f:
    f.write(fixed_text)
