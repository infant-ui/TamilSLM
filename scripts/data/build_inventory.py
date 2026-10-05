import os
import json
import re
import csv
from collections import defaultdict

def extract_units(text):
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
            subq_regex = r'(?m)^\s*(?:\d+\.|[a-z]\))\s+'
            matches = list(re.finditer(subq_regex, c))
            if matches:
                preamble = c[:matches[0].start()].strip()
                if preamble:
                    units.append({"type": "Exercise Block", "name": n})
                for i, match in enumerate(matches):
                    units.append({"type": "Exercise Sub-Question", "name": match.group().strip()})
            else:
                units.append({"type": "Exercise Block", "name": n})
                
        elif t == "Example/Problem":
            units.append({"type": "Example/Problem", "name": n})
            
        elif t == "Activity Instruction":
            units.append({"type": "Activity Instruction", "name": "Activity Step"})
            
        elif t == "Heading":
            units.append({"type": "Heading", "name": n})
            
        elif t == "Table":
            units.append({"type": "Table", "name": n})
            
        elif t == "Descriptive":
            if len(c.split()) >= 40 and len(re.split(r'[.!?]+', c)) >= 4:
                if len(re.findall(r'[a-zA-Z]', c)) > len(c) * 0.5:
                    units.append({"type": "Descriptive Unit", "name": "Paragraph"})

    for block in blocks:
        block = block.strip()
        if not block: continue
        
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
            current_state = "Descriptive"
            name = activity_match.group(1) if activity_match else "Activity Step"
            current_unit = {"type": "Activity Instruction", "name": name, "content": block}
            save_current_unit()
            current_unit = {"type": None, "name": None, "content": ""}
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
            
        if current_state == "Descriptive":
            save_current_unit()
            current_unit = {"type": "Descriptive", "name": "Paragraph", "content": block}
        else:
            current_unit["content"] += "\n\n" + block
            
    save_current_unit()
    return units

def main():
    chunks_dir = r"data\processed\chunks\books"
    inventory = []
    
    if not os.path.exists(chunks_dir):
        print(f"Directory not found: {chunks_dir}")
        return

    # Walk through the directory and process all JSON files
    for root, _, files in os.walk(chunks_dir):
        for file in files:
            if file.endswith(".json"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        for chunk in data:
                            text = chunk.get("text", "")
                            meta = chunk.get("metadata", {})
                            
                            grade = meta.get("class_level", "Unknown")
                            subject = meta.get("subject", "Unknown")
                            chapter = meta.get("chapter_title", "Unknown")
                            source_file = meta.get("filename", file)
                            
                            extracted_units = extract_units(text)
                            
                            # To avoid duplicates in overlapping chunks
                            seen_in_chunk = set()
                            for unit in extracted_units:
                                u_key = (unit["type"], unit["name"])
                                if u_key not in seen_in_chunk:
                                    inventory.append({
                                        "grade": grade,
                                        "subject": subject,
                                        "chapter": chapter,
                                        "unit_type": unit["type"],
                                        "unit_name": unit["name"],
                                        "source_file": source_file,
                                        "source_page": "N/A" # No page metadata available in chunks
                                    })
                                    seen_in_chunk.add(u_key)
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

    # Remove duplicates globally
    unique_inventory = []
    seen = set()
    for item in inventory:
        key = (item["grade"], item["subject"], item["chapter"], item["unit_type"], item["unit_name"])
        if key not in seen:
            unique_inventory.append(item)
            seen.add(key)
            
    # Write to CSV
    csv_file = "content_inventory.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["grade", "subject", "chapter", "unit_type", "unit_name", "source_file", "source_page"])
        writer.writeheader()
        writer.writerows(unique_inventory)
        
    print(f"Successfully wrote inventory to {csv_file}")
    
    # Summary Statistics
    total_units = len(unique_inventory)
    
    grade_counts = defaultdict(int)
    subject_counts = defaultdict(int)
    formula_heavy_counts = defaultdict(int) # Maths, Science
    descriptive_counts = defaultdict(int) # Others
    
    for item in unique_inventory:
        grade = str(item["grade"])
        subject = str(item["subject"]).lower()
        
        grade_counts[grade] += 1
        subject_counts[subject] += 1
        
        # New counting logic based on actual parsed unit type
        if item["unit_type"] in ["Example/Problem", "Exercise Sub-Question", "Exercise Block", "Concept/Law", "Heading"]:
            formula_heavy_counts[subject] += 1
        elif item["unit_type"] in ["Descriptive Unit", "Activity", "Activity Instruction"]:
            descriptive_counts[subject] += 1
            
    # Markdown Report
    report = f"""# Curriculum Content Inventory Report

## Summary Statistics
- **Total Teachable Units Found:** {total_units}

### Breakdown by Grade
"""
    for g, count in sorted(grade_counts.items()):
        report += f"- Class {g}: {count} units\n"
        
    report += "\n### Breakdown by Subject\n"
    for s, count in sorted(subject_counts.items()):
        report += f"- {s.capitalize()}: {count} units\n"
        
    report += "\n### Subject Categories (Template Targeting)\n"
    report += f"- **Formula/Derivation-Heavy Units:** {sum(formula_heavy_counts.values())}\n"
    report += f"- **Purely Descriptive Units:** {sum(descriptive_counts.values())}\n"
    
    report += "\n## Training Pair Multipliers\n"
    report += "To estimate the total supervised fine-tuning (SFT) dataset size, we apply multipliers to the total teachable units:\n\n"
    report += f"- **1x (One pair per unit):** {total_units * 1:,} training pairs\n"
    report += f"- **5x (Phrasing/Difficulty variants):** {total_units * 5:,} training pairs\n"
    report += f"- **10x (Full bilingual x difficulty x phrasing expansion):** {total_units * 10:,} training pairs\n\n"
    report += "*(This replaces the previous folklore estimate of 250k-500k)*\n"
    
    report_file = "inventory_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"Successfully wrote report to {report_file}")

if __name__ == "__main__":
    main()
