import fitz
import os
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_DISABLE_ONEDNN"] = "1"
os.environ["FLAGS_enable_pir_api"] = "0"
import paddle
paddle.enable_static()
from paddleocr import PaddleOCR

def run_paddle_preflight():
    ocr = PaddleOCR(use_angle_cls=True, lang='ta', show_log=False)
    
    results_report = []
    
    # --- Class 8 Tamil Maths (Target Page 294) ---
    c8_path = r"data\books\class_8\Tamil\textbooks\Maths\Class_8_Mathematics_Tamil_2025.pdf"
    if os.path.exists(c8_path):
        doc = fitz.open(c8_path)
        # 0-indexed, so page 294 is index 293
        # I'll render index 293 and 294 just in case. Let's do 293.
        target_idx = 293
        if target_idx < len(doc):
            pix = doc[target_idx].get_pixmap(dpi=150)
            img_path = "c8_page_294.png"
            pix.save(img_path)
            
            # OCR
            results = ocr.ocr(img_path)
            text_lines = [line[1][0] for res in results if res for line in res]
            text = "\n".join(text_lines)
            
            results_report.append("### Class 8 Tamil Maths (Page 294)\n")
            results_report.append(f"**Regex match for 'சொல்லகராதி':** {'FOUND' if 'சொல்லகராதி' in text else 'NOT FOUND'}\n")
            results_report.append(f"**OCR Snippet:**\n```text\n{text[:1000]}\n```\n")
    else:
        results_report.append("### Class 8 Tamil Maths - FILE NOT FOUND\n")

    # --- Class 6 Tamil Science Term 1 (Target Page ~105) ---
    c6_path = r"data\books\class_6\science\tamil\textbook\term_1\Class_6_Science_Tamil_Science_-_Term_1.pdf"
    if os.path.exists(c6_path):
        doc = fitz.open(c6_path)
        # Render a page near the end that we saw had the garbage text
        target_idx = 104
        if target_idx < len(doc):
            pix = doc[target_idx].get_pixmap(dpi=150)
            img_path = "c6_page_105.png"
            pix.save(img_path)
            
            # OCR
            results = ocr.ocr(img_path, cls=True)
            text_lines = [line[1][0] for res in results if res for line in res]
            text = "\n".join(text_lines)
            
            results_report.append("### Class 6 Tamil Science Term 1 (Page 105)\n")
            results_report.append(f"**OCR Snippet:**\n```text\n{text[:1000]}\n```\n")
            
    # --- Class 6 English Science Term 1 (Search full PDF) ---
    c6_eng_path = r"data\books\class_6\science\english\textbook\term_1\Class_6_Science_English_Science_-_Term_1_-_2025.pdf"
    results_report.append("### Class 6 English Science Term 1 (PyMuPDF Search)\n")
    if os.path.exists(c6_eng_path):
        doc = fitz.open(c6_eng_path)
        found_pages = []
        for i, page in enumerate(doc):
            text = page.get_text()
            if "Glossary" in text:
                found_pages.append(i)
                
        if found_pages:
            results_report.append(f"**'Glossary' FOUND on pages:** {found_pages}\n")
            # Grab the text from the first found page
            text = doc[found_pages[0]].get_text()
            # Extract context around the word Glossary
            idx = text.find("Glossary")
            snippet = text[max(0, idx-100):min(len(text), idx+500)]
            results_report.append(f"**Snippet from Page {found_pages[0]+1}:**\n```text\n{snippet}\n```\n")
        else:
            results_report.append("**'Glossary' NOT FOUND in any page of the PDF.**\n")
            
    with open("C:/Users/YAZHINI/.gemini/antigravity-ide/brain/06206702-19be-47b6-b7c2-659df79c9991/paddle_preflight_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(results_report))

if __name__ == "__main__":
    run_paddle_preflight()
