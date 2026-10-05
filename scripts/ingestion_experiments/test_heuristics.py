import os
import json
import re
import fitz

def extract_units_old(text):
    units = []
    heading_pattern = r'\b(\d+\.\d+(?:\.\d+)?)\s+([A-Z][a-zA-Z\s]+?)(?=\s[A-Z]|\s[a-z]{2,}ing|\s[a-z]{2,}ed|\sis|\sare|\s=|\s[a-z]{3,})'
    for match in re.finditer(heading_pattern, text):
        units.append({"type": "Heading", "name": f"{match.group(1)} {match.group(2).strip()}"})
    problem_pattern = r'\b(Problem\s+\d+\.\d+)\b'
    for match in re.finditer(problem_pattern, text):
        units.append({"type": "Problem", "name": match.group(1)})
    table_pattern = r'\b(Table\s+\d+\.\d+)\s+([A-Z][a-zA-Z\s]+?)(?=\s[A-Z]|\s[a-z]{3,})'
    for match in re.finditer(table_pattern, text):
        units.append({"type": "Table", "name": f"{match.group(1)} {match.group(2).strip()}"})
    activity_pattern = r'\b(ACTIVITY\s+\d+)\b'
    for match in re.finditer(activity_pattern, text):
        units.append({"type": "Activity", "name": match.group(1)})
    law_pattern = r'\b([A-Z][a-zA-Z\s]+(?:Law|Theorem|Principle|Rule|Effect))\b'
    for match in re.finditer(law_pattern, text, re.IGNORECASE):
        if len(match.group(1)) < 50:
            units.append({"type": "Concept/Law", "name": match.group(1).strip()})
    return units

def extract_units_new(text):
    units = []
    
    # Existing patterns with fixes for Maths
    heading_pattern = r'\b(\d+\.\d+(?:\.\d+)?)\s+([A-Z][a-zA-Z\s]+?)(?=\s[A-Z]|\s[a-z]{2,}ing|\s[a-z]{2,}ed|\sis|\sare|\s=|\s[a-z]{3,})'
    for match in re.finditer(heading_pattern, text):
        units.append({"type": "Heading", "name": f"{match.group(1)} {match.group(2).strip()}", "content": match.group(0)})
        
    problem_pattern = r'\b((?:Problem|Example)\s+\d+\.\d+(?:\.\d+)?)\b'
    for match in re.finditer(problem_pattern, text, re.IGNORECASE):
        units.append({"type": "Example/Problem", "name": match.group(1), "content": match.group(0)})
        
    table_pattern = r'\b(Table\s+\d+\.\d+)\s+([A-Z][a-zA-Z\s]+?)(?=\s[A-Z]|\s[a-z]{3,})'
    for match in re.finditer(table_pattern, text):
        units.append({"type": "Table", "name": f"{match.group(1)} {match.group(2).strip()}", "content": match.group(0)})
        
    activity_pattern = r'\b(ACTIVITY\s+\d+)\b'
    for match in re.finditer(activity_pattern, text, re.IGNORECASE):
        units.append({"type": "Activity", "name": match.group(1), "content": match.group(0)})
        
    law_pattern = r'\b([A-Z][a-zA-Z\s]+(?:Law|Theorem|Principle|Rule|Effect))\b'
    for match in re.finditer(law_pattern, text, re.IGNORECASE):
        if len(match.group(1)) < 50:
            units.append({"type": "Concept/Law", "name": match.group(1).strip(), "content": match.group(0)})
            
    # Sub-question tracking for Exercises
    exercise_pattern = r'(?i)Exercise\s+\d+\.\d+'
    blocks = re.split(r'\n\s*\n', text)
    in_exercise = False
    
    for block in blocks:
        block = block.strip()
        if not block: continue
        
        # Check if this block starts an exercise
        if re.search(exercise_pattern, block):
            in_exercise = True
            units.append({"type": "Exercise Block", "name": re.search(exercise_pattern, block).group(), "content": block[:100].replace('\n', ' ')})
            continue
            
        if in_exercise:
            # Check for sub-questions
            sub_matches = re.findall(r'^\s*(\d+\.|[a-z]\))', block, re.MULTILINE)
            for m in sub_matches:
                units.append({"type": "Exercise Sub-Question", "name": m, "content": block[:100].replace('\n', ' ')})
            # Assume exercise ends if we hit a new heading or text that isn't a sub-question but is long
            if re.search(r'^\d+\.\d+', block) or (not sub_matches and len(block.split()) > 20):
                in_exercise = False

        # Descriptive Unit Threshold:
        # Must be >= 3 sentences AND >= 40 words.
        if not in_exercise and len(block.split()) >= 40 and len(re.split(r'[.!?]+', block)) >= 4:
            if len(re.findall(r'[a-zA-Z]', block)) > len(block) * 0.5:
                # Exclude if it already matched a heading etc
                # We do a simple check by not doing exact overlap for this test
                units.append({"type": "Descriptive Unit", "name": "Paragraph", "content": block[:150].replace('\n', ' ') + "..."})
                
    return units

def main():
    print("=== Testing Science Chunk ===")
    science_chunk_path = r"d:\Project Assistan\data\processed\chunks\books\class_6\science\english\textbooks\term_1\6th_science_t1_chunks.json"
    if os.path.exists(science_chunk_path):
        with open(science_chunk_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            text = "\n\n".join(c["text"] for c in chunks[:15]) # first 15 chunks
            old_units = extract_units_old(text)
            new_units = extract_units_new(text)
            print(f"Old count: {len(old_units)}")
            print(f"New count: {len(new_units)}")
            print("Examples of new Descriptive Units:")
            desc = [u for u in new_units if u["type"] == "Descriptive Unit"]
            for u in desc[:3]:
                print(f" - {u['content']}")
    else:
        print("Science chunk not found.")

    print("\n=== Testing Maths Chunk ===")
    maths_pdf = r"d:\Project Assistan\data\books\class_6\Maths\english\textbooks\term_1\6th_Maths_T1_EM.pdf"
    if os.path.exists(maths_pdf):
        doc = fitz.open(maths_pdf)
        text = ""
        for i in range(15, 30):
            text += doc[i].get_text("text") + "\n\n"
            
        old_units = extract_units_old(text)
        new_units = extract_units_new(text)
        print(f"Old count: {len(old_units)}")
        print(f"New count: {len(new_units)}")
        
        print("Examples of Maths Units (Examples/Exercises):")
        math_units = [u for u in new_units if u["type"] in ["Example/Problem", "Exercise Sub-Question", "Exercise Block"]]
        for u in math_units[:8]:
            print(f" - [{u['type']}] {u['content']}")
    else:
        print("Maths PDF not found.")

if __name__ == "__main__":
    main()
