import os
import re
import fitz
import csv
from pathlib import Path

def is_tamil(text):
    return any(0x0B80 <= ord(c) <= 0x0BFF for c in text)

def is_english(text):
    return any(c.isascii() and c.isalpha() for c in text)

def clean_text(text):
    text = re.sub(r'^\d+\.\s*', '', text)
    text = re.sub(r'^-\s*', '', text)
    text = re.sub(r'-\s*$', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def cluster_words_into_lines(words):
    if not words: return []
    
    heights = [w[3] - w[1] for w in words]
    heights.sort()
    median_height = heights[len(heights)//2] if heights else 12.0
    threshold = median_height * 0.4
    
    words.sort(key=lambda w: (w[1] + w[3]) / 2)
    
    y_bands = []
    current_band = [words[0]]
    current_cy = (words[0][1] + words[0][3]) / 2
    
    for w in words[1:]:
        cy = (w[1] + w[3]) / 2
        if abs(cy - current_cy) <= threshold:
            current_band.append(w)
            # DO NOT update current_cy dynamically to prevent chain-bleeding down the page
        else:
            y_bands.append(current_band)
            current_band = [w]
            current_cy = cy
            
    if current_band:
        y_bands.append(current_band)
        
    return y_bands

def split_band_into_columns(band):
    # Sort band left-to-right
    band.sort(key=lambda w: w[0])
    columns = []
    current_col = [band[0]]
    
    for w in band[1:]:
        # If the gap between words is large, it's a new column
        if w[0] - current_col[-1][2] > 20:
            columns.append(current_col)
            current_col = [w]
        else:
            current_col.append(w)
    
    if current_col:
        columns.append(current_col)
        
    return columns

def extract_term_from_col(col):
    col_text = " ".join(w[4] for w in col).strip()
    has_t = is_tamil(col_text)
    has_e = is_english(col_text)
    
    t_term = ""
    e_term = ""
    
    if has_t and has_e:
        if '-' in col_text:
            parts = col_text.split('-', 1)
            if is_tamil(parts[0]) and is_english(parts[1]):
                t_term = parts[0]
                e_term = parts[1]
            elif is_english(parts[0]) and is_tamil(parts[1]):
                e_term = parts[0]
                t_term = parts[1]
        
        if not t_term and not e_term:
            t_words = []
            e_words = []
            for w in col:
                if is_tamil(w[4]): t_words.append(w[4])
                elif is_english(w[4]): e_words.append(w[4])
            t_term = " ".join(t_words)
            e_term = " ".join(e_words)
    elif has_t:
        t_term = col_text
    elif has_e:
        e_term = col_text
        
    return clean_text(t_term), clean_text(e_term), has_t, has_e

def process_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    all_pairs = []
    
    start_page = max(0, len(doc) - 15)
    
    for p_num in range(start_page, len(doc)):
        page = doc[p_num]
        words = page.get_text("words")
        y_bands = cluster_words_into_lines(words)
        
        pending_orphan = None
        
        for band in y_bands:
            # Drop headers
            line_text = " ".join(w[4] for w in band).strip()
            if not line_text or line_text.lower() in ["glossary", "சொல்லகராதி", "கலைச்சொற்கள்", "அகராதி"]:
                continue
                
            cols = split_band_into_columns(band)
            
            for col in cols:
                t_term, e_term, has_t, has_e = extract_term_from_col(col)
                
                if t_term and e_term:
                    if pending_orphan:
                        # Flush the unresolved pending orphan as a flagged incomplete term
                        if pending_orphan['type'] == 'tamil':
                            all_pairs.append({'tamil': pending_orphan['text'], 'english': '', 'review': True})
                        else:
                            all_pairs.append({'tamil': '', 'english': pending_orphan['text'], 'review': True})
                        pending_orphan = None
                    all_pairs.append({'tamil': t_term, 'english': e_term, 'review': False})
                elif t_term and not e_term:
                    if pending_orphan and pending_orphan['type'] == 'english':
                        all_pairs.append({'tamil': t_term, 'english': pending_orphan['text'], 'review': True})
                        pending_orphan = None
                    else:
                        if pending_orphan:
                            # Flush the previous pending orphan
                            if pending_orphan['type'] == 'tamil':
                                all_pairs.append({'tamil': pending_orphan['text'], 'english': '', 'review': True})
                            else:
                                all_pairs.append({'tamil': '', 'english': pending_orphan['text'], 'review': True})
                        pending_orphan = {'type': 'tamil', 'text': t_term}
                elif e_term and not t_term:
                    if pending_orphan and pending_orphan['type'] == 'tamil':
                        all_pairs.append({'tamil': pending_orphan['text'], 'english': e_term, 'review': True})
                        pending_orphan = None
                    else:
                        if pending_orphan:
                            # Flush the previous pending orphan
                            if pending_orphan['type'] == 'tamil':
                                all_pairs.append({'tamil': pending_orphan['text'], 'english': '', 'review': True})
                            else:
                                all_pairs.append({'tamil': '', 'english': pending_orphan['text'], 'review': True})
                        pending_orphan = {'type': 'english', 'text': e_term}
        
        if pending_orphan:
            if pending_orphan['type'] == 'tamil':
                all_pairs.append({'tamil': pending_orphan['text'], 'english': '', 'review': True})
            else:
                all_pairs.append({'tamil': '', 'english': pending_orphan['text'], 'review': True})
                        
    return all_pairs

def extract_metadata(filepath):
    path_str = str(filepath).lower()
    cls_match = re.search(r'class_(\d+)', path_str)
    cls_val = f"Class {cls_match.group(1)}" if cls_match else "Unknown"
    
    subj_val = "Unknown"
    if 'math' in path_str: subj_val = "Maths"
    elif 'science' in path_str: subj_val = "Science"
    
    term_match = re.search(r'term_(\d+)', path_str)
    term_val = f"Term {term_match.group(1)}" if term_match else "Full Year"
    
    med_val = "Unknown"
    if 'tamil' in path_str: med_val = "Tamil"
    elif 'english' in path_str: med_val = "English"
    
    return cls_val, subj_val, term_val, med_val

def write_csv(filename, rows):
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Class", "Subject", "Term", "Medium", "Tamil_Term", "English_Term", "Needs_Human_Review"])
        for r in rows:
            writer.writerow([r['class'], r['subject'], r['term'], r['medium'], r['tamil'], r['english'], r['review']])

def main():
    books_dir = Path(r"data\books")
    out_dir = Path("glossary_outputs")
    out_dir.mkdir(exist_ok=True)
    
    all_rows = []
    failures = []
    file_groups = {}
    
    for pdf_path in books_dir.rglob("*.pdf"):
        print(f"Processing {pdf_path.name}...")
        cls, subj, term, med = extract_metadata(pdf_path)
        pairs = process_pdf(pdf_path)
        
        file_rows = []
        for p in pairs:
            if len(p['tamil']) > 1 and len(p['english']) > 1:
                if not any(r['tamil'] == p['tamil'] and r['english'] == p['english'] for r in file_rows):
                    file_rows.append({
                        'class': cls, 'subject': subj, 'term': term, 'medium': med,
                        'tamil': p['tamil'], 'english': p['english'], 'review': p['review']
                    })
                
        if not file_rows:
            failures.append({'file': pdf_path.name, 'reason': '0 terms found'})
        else:
            flag_count = sum(1 for r in file_rows if r['review'])
            if flag_count / len(file_rows) > 0.5:
                failures.append({'file': pdf_path.name, 'reason': f'>50% terms flagged ({flag_count}/{len(file_rows)})'})
                
        all_rows.extend(file_rows)
        
        term_key = f"{cls.replace(' ', '')}_{subj}_{term.replace(' ', '')}"
        if term_key not in file_groups: file_groups[term_key] = []
        file_groups[term_key].extend(file_rows)
        
        book_key = f"{cls.replace(' ', '')}_{subj}"
        if book_key not in file_groups: file_groups[book_key] = []
        file_groups[book_key].extend(file_rows)

    write_csv("glossary_all_classes.csv", all_rows)
    for key, rows in file_groups.items():
        write_csv(f"glossary_outputs/{key}.csv", rows)
        
    with open('extraction_failures.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Filename", "Reason"])
        for fail in failures:
            writer.writerow([fail['file'], fail['reason']])
            
    with open("glossary_report.md", "w", encoding="utf-8") as f:
        f.write("# Glossary Extraction Report\n\n")
        f.write(f"Total Unique Terms (pre-deduplication): {len(all_rows)}\n")
        if all_rows:
            flagged = sum(1 for r in all_rows if r['review'])
            f.write(f"Total Terms Flagged for Review: {flagged} ({flagged/len(all_rows):.1%})\n\n")
        
        f.write("## Failures & High-Risk Files\n")
        for fail in failures:
            f.write(f"- **{fail['file']}**: {fail['reason']}\n")
            
        f.write("\n## Output Files Generated\n")
        f.write("- glossary_all_classes.csv\n")
        f.write("- extraction_failures.csv\n")
        f.write("- glossary_outputs/ (Contains term-wise and book-wise CSVs)\n")
        
    print(f"\nDone! Extracted {len(all_rows)} terms.")

if __name__ == "__main__":
    main()
