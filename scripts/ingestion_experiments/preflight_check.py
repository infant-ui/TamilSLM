import fitz
import re
import sys

def test_pdf(filepath, desc, search_term="சொல்லகராதி"):
    print(f"\n{'='*50}\nTesting {desc}\nFile: {filepath}\n{'='*50}")
    try:
        doc = fitz.open(filepath)
        print(f"Total Pages: {len(doc)}")
        
        # Check last 10 pages for the search term
        match_found = False
        target_page = None
        for i in range(max(0, len(doc)-10), len(doc)):
            text = doc[i].get_text()
            if search_term in text or "Glossary" in text:
                match_found = True
                target_page = i
                break
                
        if not target_page:
            target_page = len(doc) - 2 # Just show the second to last page if no glossary found
            
        text = doc[target_page].get_text()
        print(f"--- Raw Text (Page {target_page}) Snippet (First 500 chars) ---")
        print(text[:500])
        print("---------------------------------------------------------")
        
        # Test Regex for Tamil
        if search_term:
            matches = re.findall(search_term, text)
            print(f"Regex match for '{search_term}': {'FOUND' if matches else 'NOT FOUND'} ({len(matches)} matches)")
            
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

if __name__ == "__main__":
    files = [
        (r"data\books\class_6\science\tamil\textbook\term_1\Class_6_Science_Tamil_Science_-_Term_1.pdf", "Class 6 Tamil Science Term 1", "சொல்லகராதி"),
        (r"data\books\class_6\science\english\textbook\term_1\Class_6_Science_English_Science_-_Term_1_-_2025.pdf", "Class 6 English Science Term 1", "Glossary"),
        (r"data\books\class_8\Tamil\textbooks\Maths\Class_8_Mathematics_Tamil_2025.pdf", "Class 8 Tamil Maths", "சொல்லகராதி")
    ]
    
    # Ensure stdout uses utf-8
    sys.stdout.reconfigure(encoding='utf-8')
    for fp, desc, term in files:
        test_pdf(fp, desc, term)
