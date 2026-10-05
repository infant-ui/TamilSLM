import os
import json
import re
import fitz

def extract_units_new(text):
    units = []
    
    # 1. Existing patterns with fixes for Maths
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
        
        if re.search(exercise_pattern, block):
            in_exercise = True
            units.append({"type": "Exercise Block", "name": re.search(exercise_pattern, block).group(), "content": block})
            continue
            
        if in_exercise:
            # FIX 3: Sub-question boundary bug
            # Find all sub-questions and split the block by them
            subq_regex = r'(?m)^\s*(?:\d+\.|[a-z]\))\s+'
            # Find the starting positions of all sub-questions
            matches = list(re.finditer(subq_regex, block))
            
            if matches:
                for i, match in enumerate(matches):
                    start = match.start()
                    end = matches[i+1].start() if i + 1 < len(matches) else len(block)
                    sub_text = block[start:end].strip()
                    name = match.group().strip()
                    units.append({"type": "Exercise Sub-Question", "name": name, "content": sub_text})
            else:
                # Still in exercise but no sub-questions matched. Could be continuation of text.
                pass
                
            # Assume exercise ends if we hit a new heading or text that isn't a sub-question but is long
            if re.search(r'^\d+\.\d+', block) or (not matches and len(block.split()) > 20):
                in_exercise = False

        # FIX 2: Miscategorization check
        # Many Science "activities" are just numbered lists starting with imperative verbs or Activity/Aim/Procedure
        # Check if block looks like an activity
        is_activity = False
        if re.search(r'^(Aim|Procedure|Observation|Materials Required):', block, re.IGNORECASE):
            is_activity = True
        elif re.match(r'^\s*([A-Za-z]|\d+\.)?\s*(Draw|Find|Measure|Take|Place|Keep|Fill|Cut|Make|Observe)\b', block, re.IGNORECASE):
            is_activity = True
            
        if is_activity and not in_exercise:
            units.append({"type": "Activity Instruction", "name": "Activity Step", "content": block})
            continue
            
        # Descriptive Unit Threshold:
        # Must be >= 3 sentences AND >= 40 words.
        if not in_exercise and not is_activity and len(block.split()) >= 40 and len(re.split(r'[.!?]+', block)) >= 4:
            if len(re.findall(r'[a-zA-Z]', block)) > len(block) * 0.5:
                # We store the FULL block to avoid truncation in training pairs
                units.append({"type": "Descriptive Unit", "name": "Paragraph", "content": block})
                
    return units

def main():
    print("=== Testing Science Chunk ===")
    science_chunk_path = r"D:\Project Assistan\data\processed\chunks\books\class_6\science\english\textbook\term_1\Class_6_Science_English_Science_-_Term_1_-_2025_chunks.json"
    if os.path.exists(science_chunk_path):
        with open(science_chunk_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            text = "\n\n".join(c["text"] for c in chunks[10:30]) 
            new_units = extract_units_new(text)
            print(f"New count: {len(new_units)}")
            
            print("\nExamples of new Descriptive Units:")
            desc = [u for u in new_units if u["type"] == "Descriptive Unit"]
            for u in desc[:3]:
                # Print first 120 chars purely for display in the terminal
                # The actual content has the full block as verified above
                display_text = u['content'].replace('\n', ' ')
                print(f" - {display_text[:120]}... [FULL LENGTH: {len(display_text)} chars]")
                
            print("\nExamples of Activity Instructions (rescued from Descriptive):")
            act = [u for u in new_units if u["type"] == "Activity Instruction"]
            for u in act[:3]:
                display_text = u['content'].replace('\n', ' ')
                print(f" - {display_text[:120]}... [FULL LENGTH: {len(display_text)} chars]")
    else:
        print("Science chunk not found.")

    print("\n=== Testing Maths Chunk ===")
    maths_pdf = r"D:\Project Assistan\data\books\class_6\Maths\english\textbooks\term_1\Class_6_Mathematics_English_Mathematics_-_Term_1.pdf"
    if os.path.exists(maths_pdf):
        doc = fitz.open(maths_pdf)
        text = ""
        for i in range(25, 45):
            text += doc[i].get_text("text") + "\n\n"
            
        new_units = extract_units_new(text)
        print(f"New count: {len(new_units)}")
        
        print("\nExamples of Maths Units (Examples/Exercises):")
        math_units = [u for u in new_units if u["type"] in ["Example/Problem", "Exercise Sub-Question", "Exercise Block"]]
        for u in math_units[:8]:
            display_text = u['content'].replace('\n', ' ')
            print(f" - [{u['type']}] {display_text}")
    else:
        print("Maths PDF not found.")

if __name__ == "__main__":
    main()
