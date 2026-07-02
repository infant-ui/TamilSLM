import csv

data = [
    ["Class", "Subject", "Medium", "Tamil_Term", "English_Term"],
    ["Class 8", "Maths", "Tamil", "அசல்", "Principal"],
    ["Class 8", "Maths", "Tamil", "அடக்க விலை", "Cost price"]
]

with open('test_glossary.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(data)
print("CSV written successfully.")
