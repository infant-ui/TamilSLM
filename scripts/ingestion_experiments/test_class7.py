import fitz
import re

def test_file(filepath, expected_term):
    print(f"Testing {filepath}")
    doc = fitz.open(filepath)
    found = False
    
    # Check all pages from end to start for the expected term
    for i in range(len(doc)-1, -1, -1):
        text = doc[i].get_text()
        
        if expected_term in text:
            found = True
            print(f"  Found '{expected_term}' on page {i} (0-indexed)")
            
            # Print a snippet around the term (safely as ascii to avoid console errors)
            idx = text.find(expected_term)
            snippet = text[max(0, idx):min(len(text), idx+100)]
            print("  Snippet (ASCII):", ascii(snippet))
            
            # Check if it has actual Tamil unicode characters
            tamil_chars = sum(1 for c in text if 0x0B80 <= ord(c) <= 0x0BFF)
            print(f"  Tamil chars on this page: {tamil_chars}")
            break
            
    if not found:
        print(f"  '{expected_term}' NOT FOUND")

files = [
    (r"data\books\class_7\Maths\Tamil\textbooks\term_1\Class_7_Mathematics_Tamil_Mathematics_-_Term_1.pdf", "சொல்லகராதி"),
    (r"data\books\class_7\Science\Tamil\textbooks\term_1\Class_7_Science_Tamil_Science_-_Term_1_-_2025.pdf", "சொல்லகராதி")
]

for f, term in files:
    test_file(f, term)
