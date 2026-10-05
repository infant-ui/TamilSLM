import os
import json
import re

target_books = {
    "class_6_tamil": "Class_6_Science_Tamil_Science_-_Term_1",
    "class_6_english": "Class_6_Science_English_Science_-_Term_1_-_2025",
    "class_8_tamil": "Class_8_Mathematics_Tamil_2025"
}

def analyze_chunks(base_dir="data/processed/chunks"):
    report = []
    
    # 1. Find all chunk files
    chunk_files = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".json"):
                chunk_files.append(os.path.join(root, f))
                
    # 2. Check each target
    for key, search_str in target_books.items():
        report.append(f"### Target: {key} ({search_str})")
        # Find matching file
        matched_file = next((f for f in chunk_files if search_str in f), None)
        
        if not matched_file:
            report.append(f"**Result:** ❌ Chunk file NOT FOUND in `{base_dir}`.")
            continue
            
        report.append(f"**File Found:** `{matched_file}`")
        try:
            with open(matched_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
                
            report.append(f"**Total Chunks:** {len(chunks)}")
            if len(chunks) == 0:
                report.append("File is empty.")
                continue
                
            # Print sample structure
            sample_chunk = chunks[0]
            report.append(f"**Chunk Schema/Keys:** `{list(sample_chunk.keys())}`")
            if 'metadata' in sample_chunk:
                report.append(f"**Metadata Schema:** `{list(sample_chunk['metadata'].keys())}`")
                
            # Scan for telltale garbled characters 'α«'
            garbled_count = sum(1 for c in chunks if 'text' in c and 'α«' in c['text'])
            report.append(f"**Garbled chunks (contains 'α«'):** {garbled_count} out of {len(chunks)}")
            
            # Search for Glossary
            glossary_term = "சொல்லகராதி" if "tamil" in key else "Glossary"
            glossary_chunks = [c for c in chunks if 'text' in c and glossary_term in c['text']]
            
            report.append(f"**Regex match for '{glossary_term}':** {'FOUND' if glossary_chunks else 'NOT FOUND'} ({len(glossary_chunks)} chunks)")
            
            if glossary_chunks:
                text_sample = glossary_chunks[0]['text'][:500]
                report.append(f"**Snippet with '{glossary_term}':**\n```text\n{text_sample}\n```")
            else:
                # Provide a random chunk snippet to verify if it's clean Unicode Tamil
                text_sample = chunks[len(chunks)//2]['text'][:500]
                report.append(f"**Random Snippet (Mid-book):**\n```text\n{text_sample}\n```")
                
        except Exception as e:
            report.append(f"Error reading {matched_file}: {e}")
            
    # Write report
    output_path = "C:/Users/YAZHINI/.gemini/antigravity-ide/brain/06206702-19be-47b6-b7c2-659df79c9991/chunk_report.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(report))
        
if __name__ == "__main__":
    analyze_chunks()
