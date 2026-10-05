import fitz

def fix_text(text):
    try:
        return text.encode('cp437').decode('utf-8')
    except Exception:
        return text 

pdf_path = r"data\books\class_6\science\tamil\textbook\term_1\Class_6_Science_Tamil_Science_-_Term_1.pdf"
doc = fitz.open(pdf_path)
page = doc[105] # Page 106
raw_text = page.get_text()
fixed_text = fix_text(raw_text)

with open("pymupdf_fixed_c6.md", "w", encoding="utf-8") as f:
    f.write(fixed_text)
