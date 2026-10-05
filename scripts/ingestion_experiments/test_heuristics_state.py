import os
import json
import re
import fitz
import sys
sys.stdout.reconfigure(encoding='utf-8')

def extract_units_state_machine(text):
    units = []
    blocks = re.split(r'\n\s*\n', text)
    
    current_state = "Descriptive"
    current_unit = {"type": None, "name": None, "content": ""}
    
    def save_current_unit():
        nonlocal current_unit
        c = current_unit["content"].strip()
        if not c:
            return
            
        t = current_unit["type"]
        n = current_unit["name"]
        
        if t == "Exercise Block":
            # Post-process the exercise block to find sub-questions
            subq_regex = r'(?m)^\s*(?:\d+\.|[a-z]\))\s+'
            matches = list(re.finditer(subq_regex, c))
            if matches:
                # Add the main block preamble (if any) as part of the exercise block
                preamble = c[:matches[0].start()].strip()
                if preamble:
                    units.append({"type": "Exercise Block", "name": n, "content": preamble})
                for i, match in enumerate(matches):
                    start = match.start()
                    end = matches[i+1].start() if i + 1 < len(matches) else len(c)
                    sub_text = c[start:end].strip()
                    units.append({"type": "Exercise Sub-Question", "name": match.group().strip(), "content": sub_text})
            else:
                units.append({"type": "Exercise Block", "name": n, "content": c})
                
        elif t == "Example/Problem":
            units.append({"type": "Example/Problem", "name": n, "content": c})
            
        elif t == "Activity Instruction":
            units.append({"type": "Activity Instruction", "name": "Activity Step", "content": c})
            
        elif t == "Heading":
            units.append({"type": "Heading", "name": n, "content": c})
            
        elif t == "Table":
            units.append({"type": "Table", "name": n, "content": c})
            
        elif t == "Descriptive":
            # Check threshold
            if len(c.split()) >= 40 and len(re.split(r'[.!?]+', c)) >= 4:
                if len(re.findall(r'[a-zA-Z]', c)) > len(c) * 0.5:
                    units.append({"type": "Descriptive Unit", "name": "Paragraph", "content": c})

    for block in blocks:
        block = block.strip()
        if not block: continue
        
        # Check if block transitions to a new state
        heading_match = re.match(r'^(\d+\.\d+(?:\.\d+)?)\s+([A-Z][a-zA-Z\s]+?)(?=\s[A-Z]|\s[a-z]{2,}ing|\s[a-z]{2,}ed|\sis|\sare|\s=|\s[a-z]{3,})', block)
        example_match = re.search(r'\b((?:Problem|Example)\s+\d+\.\d+(?:\.\d+)?)\b', block, re.IGNORECASE)
        exercise_match = re.search(r'(?i)Exercise\s+\d+\.\d+', block)
        table_match = re.search(r'\b(Table\s+\d+\.\d+)\s+([A-Z][a-zA-Z\s]+?)(?=\s[A-Z]|\s[a-z]{3,})', block)
        activity_match = re.search(r'\b(ACTIVITY\s+\d+)\b', block, re.IGNORECASE)
        
        is_activity_instr = False
        if re.search(r'^(Aim|Procedure|Observation|Materials Required):', block, re.IGNORECASE):
            is_activity_instr = True
        elif re.match(r'^\s*([A-Za-z]|\d+\.)?\s*(Draw|Find|Measure|Take|Place|Keep|Fill|Cut|Make|Observe)\b', block, re.IGNORECASE):
            is_activity_instr = True

        law_match = re.search(r'\b([A-Z][a-zA-Z\s]+(?:Law|Theorem|Principle|Rule|Effect))\b', block, re.IGNORECASE)
        
        if exercise_match:
            save_current_unit()
            current_state = "Exercise"
            current_unit = {"type": "Exercise Block", "name": exercise_match.group(), "content": block}
            continue
            
        if example_match:
            save_current_unit()
            current_state = "Example"
            current_unit = {"type": "Example/Problem", "name": example_match.group(1), "content": block}
            continue
            
        if heading_match:
            save_current_unit()
            current_state = "Descriptive"
            current_unit = {"type": "Heading", "name": f"{heading_match.group(1)} {heading_match.group(2).strip()}", "content": block}
            save_current_unit()
            current_unit = {"type": None, "name": None, "content": ""}
            continue
            
        if activity_match or is_activity_instr:
            save_current_unit()
            current_state = "Activity"
            name = activity_match.group(1) if activity_match else "Activity Step"
            current_unit = {"type": "Activity Instruction", "name": name, "content": block}
            continue
            
        if table_match:
            save_current_unit()
            current_state = "Descriptive"
            current_unit = {"type": "Table", "name": f"{table_match.group(1)} {table_match.group(2).strip()}", "content": block}
            save_current_unit()
            current_unit = {"type": None, "name": None, "content": ""}
            continue
            
        if law_match and len(law_match.group(1)) < 50:
            save_current_unit()
            current_state = "Descriptive"
            current_unit = {"type": "Concept/Law", "name": law_match.group(1).strip(), "content": block}
            save_current_unit()
            current_unit = {"type": None, "name": None, "content": ""}
            continue
            
        # If no transition, append to current state
        if current_state == "Descriptive":
            # For descriptive, we evaluate each block individually as a paragraph
            # We don't accumulate multiple paragraphs into one giant descriptive unit
            save_current_unit()
            current_unit = {"type": "Descriptive", "name": "Paragraph", "content": block}
        else:
            current_unit["content"] += "\n\n" + block
            
    # Save the last unit
    save_current_unit()
    return units

def main():
    print("=== Testing Science Chunk ===")
    science_chunk_path = r"D:\Project Assistan\data\processed\chunks\books\class_6\science\english\textbook\term_1\Class_6_Science_English_Science_-_Term_1_-_2025_chunks.json"
    if os.path.exists(science_chunk_path):
        with open(science_chunk_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            text = "\n\n".join(c["text"] for c in chunks[10:30]) 
            new_units = extract_units_state_machine(text)
            
            print("\nExamples of new Descriptive Units:")
            desc = [u for u in new_units if u["type"] == "Descriptive Unit"]
            for u in desc[:3]:
                display_text = u['content'].replace('\n', ' ')
                print(f" - {display_text[:120]}... [FULL LENGTH: {len(u['content'])} chars]")
                
            print("\nExamples of Activity Instructions:")
            act = [u for u in new_units if u["type"] == "Activity Instruction"]
            for u in act[:3]:
                display_text = u['content'].replace('\n', ' ')
                print(f" - {display_text[:120]}... [FULL LENGTH: {len(u['content'])} chars]")
    
    print("\n=== Testing Maths Chunk ===")
    maths_pdf = r"D:\Project Assistan\data\books\class_6\Maths\english\textbooks\term_1\Class_6_Mathematics_English_Mathematics_-_Term_1.pdf"
    if os.path.exists(maths_pdf):
        doc = fitz.open(maths_pdf)
        text = ""
        for i in range(25, 45):
            text += doc[i].get_text("text") + "\n\n"
            
        new_units = extract_units_state_machine(text)
        
        print("\nExamples of Maths Units (Examples/Exercises):")
        math_units = [u for u in new_units if u["type"] in ["Example/Problem", "Exercise Sub-Question", "Exercise Block"]]
        
        short_count = sum(1 for u in math_units if len(u["content"].split()) < 15)
        print(f"Total Maths Units: {len(math_units)}")
        print(f"Short/Label-only Maths Units (<15 words): {short_count} ({short_count/len(math_units)*100:.1f}%)")
        
        for u in math_units:
            if "Example" in u["type"] or "Example" in u["name"]:
                display_text = u['content'].replace('\n', ' ')
                print(f" - [{u['type']}] ({u['name']}) {display_text[:120]}... [FULL LENGTH: {len(u['content'])} chars]")
        print("First 5 other units:")
        for u in math_units[:5]:
            display_text = u['content'].replace('\n', ' ')
            print(f" - [{u['type']}] {display_text[:120]}... [FULL LENGTH: {len(u['content'])} chars]")
            
if __name__ == "__main__":
    main()
