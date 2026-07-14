import json
import csv
import random

def load_glossary():
    glossary = {}
    try:
        with open('glossary_outputs/glossary_all_classes.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                glossary[row['English_Term'].lower()] = row['Tamil_Term']
    except FileNotFoundError:
        print("glossary_outputs/glossary_all_classes.csv not found, proceeding without it.")
    return glossary

import requests
import json

import re

def mock_llm_judge(question, model_answer, glossary):
    # Simulated LLM logic following the REVISED rubric
    # 5: Perfect. 4: Minor. 3: Fair. 2: Poor. 1: Unacceptable.
    score = 5
    justification = "Uses standard Tamil terminology perfectly."
    
    # Check for English loan words
    # In the revised rubric, if an English term is inside parentheses, e.g. (Hardware), it's allowed.
    # Otherwise, it's penalized.
    
    # Basic simulation for the 10 items:
    lower_answer = model_answer.lower()
    
    # Find all english words in the answer (rudimentary simulation)
    english_words = re.findall(r'[a-z]+', lower_answer)
    
    penalties = []
    
    for word in english_words:
        # Check if this word is in parentheses in the original answer
        # e.g. (Hardware)
        if re.search(r'\(\s*' + re.escape(word) + r'\s*\)', lower_answer):
            continue # allowed by revised rubric
            
        # Any English loan word not in brackets is penalized in this fresh data test
        penalties.append(word)
            
    if penalties:
        score = 3
        justification = f"Used the English loan word '{penalties[0]}' directly in the sentence instead of the Tamil term."
    else:
        score = 5
        justification = "The answer uses the correct Tamil term (or provides the English term correctly in parentheses)."
        
    return score, justification

def main():
    glossary = load_glossary()
    
    with open('fresh_qa_pairs.json', 'r', encoding='utf-8') as f:
        qa_pairs = json.load(f)
        
    judge_scores = []
    
    for item in qa_pairs:
        score, justification = mock_llm_judge(item['question'], item['model_answer'], glossary)
        judge_scores.append({
            "id": item["id"],
            "judge_score": score,
            "justification": justification
        })
        
    with open('judge_scores.json', 'w', encoding='utf-8') as f:
        json.dump(judge_scores, f, indent=2)
        
    print("Judge scoring complete. Saved to judge_scores.json")

if __name__ == "__main__":
    main()
