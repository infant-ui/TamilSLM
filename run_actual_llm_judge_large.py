import json, re, requests

with open('large_qa_pairs.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

def normalize_brackets(text):
    text = re.sub(r'\(\s+([^\)]+?)\s+\)', r'(\1)', text)
    text = re.sub(r'\[\s+([^\]]+?)\s+\]', r'[\1]', text)
    return text

prompt_template = """You are a technical evaluator for Tamil Language Content.
Evaluate the terminology correctness of the following 'Answer' to the 'Question' on a scale of 1-5.

Score 5: The answer uses the correct Tamil term. It is highly acceptable to use English technical terms IF they are provided in parentheses or brackets next to the Tamil term (e.g. திசைவேகம் (Velocity) or அச்சு இயந்திரம் [Printer] or (Hardware)).
Score 1-4: The answer uses raw English loan words directly inside the Tamil sentence grammar without brackets (e.g. 'science ,' or 'mouse.'). The score should be lower the more egregious the mixing is. 

Question: {q}
Answer: {a}

Return ONLY a JSON object with 'score' (int 1-5) and 'justification' (string). Nothing else.
"""

results = []
for item in items:
    clean_answer = normalize_brackets(item['model_answer'])
    prompt = prompt_template.format(q=item['question'], a=clean_answer)
    payload = {
        'model': 'llama3.1:latest',
        'prompt': prompt,
        'stream': False,
        'format': 'json'
    }
    try:
        r = requests.post('http://localhost:11434/api/generate', json=payload, timeout=60)
        res_json = json.loads(r.json()['response'])
        score = int(res_json.get('score', 3))
        justification = res_json.get('justification', '')
    except Exception as e:
        score = 3
        justification = 'Error'
        
    results.append({
        'id': item['id'],
        'judge_score': score,
        'justification': justification
    })

with open('llm_large_scores.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
