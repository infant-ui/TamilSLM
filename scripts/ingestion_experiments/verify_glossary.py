import csv
import random

with open('glossary.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print("--- 15 RANDOM SPOT CHECKS ---")
random.seed(42)
sample15 = random.sample(rows, min(15, len(rows)))
for i, r in enumerate(sample15):
    print(f"{i+1}. {r['Class']} {r['Subject']} {r['Medium']}: {r['Tamil_Term']} <-> {r['English_Term']}")

print("\n--- 5 MEDIUM-MISMATCH SPOT CHECKS (English Medium) ---")
english_rows = [r for r in rows if r['Medium'] == 'English']
sample5 = random.sample(english_rows, min(5, len(english_rows)))
for i, r in enumerate(sample5):
    print(f"{i+1}. {r['Class']} {r['Subject']} {r['Medium']}: {r['Tamil_Term']} <-> {r['English_Term']}")
