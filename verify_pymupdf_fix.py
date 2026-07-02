import fitz
import re
import os

def detect_and_fix(raw_text):
    # Detection heuristic: check for common mojibake characters like 'α«' or high frequency of characters in Latin-1 supplement
    mojibake_count = raw_text.count("α«")
    if mojibake_count > 10:
        try:
            fixed = raw_text.encode('cp437').decode('utf-8')
            return fixed, True
        except Exception:
            return raw_text, False
    return raw_text, False

def check_file(pdf_path, check_pages=None, search_term=None):
    if not os.path.exists(pdf_path):
        return f"File not found: {pdf_path}"
    
    doc = fitz.open(pdf_path)
    pages_to_check = check_pages if check_pages else list(range(min(10, doc.page_count)))
    
    results = []
    found_search_term = False
    
    for p_num in pages_to_check:
        if p_num >= doc.page_count:
            continue
            
        page = doc[p_num]
        raw_text = page.get_text()
        
        fixed_text, was_fixed = detect_and_fix(raw_text)
        
        # Check for residual corruption (replacement character \ufffd or weird sequences)
        has_residual = "\ufffd" in fixed_text
        
        if search_term and search_term in fixed_text:
            found_search_term = True
            
        # Grab a snippet for manual review
        snippet = fixed_text[:200].replace('\n', ' ')
        
        results.append(f"Page {p_num}: Fixed={was_fixed}, Residual={has_residual}, Snippet: {snippet}")
        
    res_str = "\n".join(results)
    if search_term:
        res_str += f"\nSearch term '{search_term}' found: {found_search_term}"
        
    return res_str

def find_glossary_page(pdf_path, search_term):
    if not os.path.exists(pdf_path):
        return f"File not found: {pdf_path}"
        
    doc = fitz.open(pdf_path)
    for p_num in range(doc.page_count):
        page = doc[p_num]
        raw_text = page.get_text()
        fixed_text, _ = detect_and_fix(raw_text)
        
        if search_term in fixed_text:
            return f"Found '{search_term}' on page {p_num}."
            
    return f"'{search_term}' NOT FOUND in {pdf_path}."

def main():
    files_to_test = [
        (r"data\books\class_8\Tamil\textbooks\Maths\Class_8_Mathematics_Tamil_2025.pdf", [293, 294, 295], "சொல்லகராதி"),
        (r"data\books\class_6\science\tamil\textbook\term_1\Class_6_Science_Tamil_Science_-_Term_1.pdf", [5, 10, 105], None),
        (r"data\books\class_7\science\tamil\textbook\term_1\Class_7_Science_Tamil_Science_-_Term_1.pdf", [5, 10], None),
        (r"data\books\class_8\Tamil\textbooks\Science\Class_8_Science_Tamil_2025.pdf", [5, 10], None),
        (r"data\books\class_6\maths\tamil\textbook\term_1\Class_6_Maths_Tamil_Maths_-_Term_1.pdf", [5, 10], None),
        (r"data\books\class_6\science\english\textbook\term_1\Class_6_Science_English_Science_-_Term_1_-_2025.pdf", [5, 10, 105, 106, 107], "Glossary"),
    ]
    
    with open("verification_results.md", "w", encoding="utf-8") as out:
        for pdf_path, pages, search_term in files_to_test:
            out.write(f"### File: {pdf_path}\n")
            res = check_file(pdf_path, pages, search_term)
            out.write(res + "\n\n")
            
            if pdf_path.endswith("Class_6_Science_English_Science_-_Term_1_-_2025.pdf") or \
               pdf_path.endswith("Class_8_Mathematics_Tamil_2025.pdf"):
                out.write("Full search for glossary:\n")
                out.write(find_glossary_page(pdf_path, search_term) + "\n\n")
                
if __name__ == "__main__":
    main()
