import json, requests

with open("messy_qa_pairs.json", "r", encoding="utf-8") as f:
    items = json.load(f)

prompt_template = """You are a technical evaluator for Tamil Language Content.
Evaluate the terminology correctness of the following 'Answer' to the 'Question' on a scale of 1-5.

Score 5: The answer uses the correct Tamil term. It is highly acceptable to use English technical terms IF they are provided in parentheses or brackets next to the Tamil term (e.g. திசைவேகம் (Velocity) or அச்சு இயந்திரம் [Printer] or ( Hardware )).
Score 1-4: The answer uses raw English loan words directly inside the Tamil sentence grammar without brackets (e.g. 'science ,' or 'mouse.'). The score should be lower the more egregious the mixing is. 

Question: {q}
Answer: {a}

Return ONLY a JSON object with 'score' (int 1-5) and 'justification' (string). Nothing else.
"""

results = []
for item in items:
    prompt = prompt_template.format(q=item['question'], a=item['model_answer'])
    payload = {
        "model": "llama3.1:latest",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    try:
        print(f"Scoring {item['id']}...")
        r = requests.post("http://localhost:11434/api/generate", json=payload, timeout=60)
        res_json = json.loads(r.json()['response'])
        score = int(res_json.get('score', 3))
        justification = res_json.get('justification', '')
    except Exception as e:
        print(f"Error on {item['id']}: {e}")
        score = 3
        justification = 'Error'
        
    results.append({
        "id": item['id'],
        "judge_score": score,
        "justification": justification
    })

with open("llm_messy_scores.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("Done!")
