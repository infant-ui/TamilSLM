from flask import Flask, render_template_string, request, redirect, url_for
import json
import os

app = Flask(__name__)

# Load QA pairs
with open('test_qa_pairs.json', 'r', encoding='utf-8') as f:
    qa_pairs = json.load(f)

SCORES_FILE = 'human_scores.json'

def load_scores():
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_scores(scores):
    with open(SCORES_FILE, 'w', encoding='utf-8') as f:
        json.dump(scores, f, indent=2)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Human Scoring - Terminology Judge</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; max-width: 600px; }
        .card { border: 1px solid #ccc; padding: 20px; border-radius: 5px; background: #f9f9f9; }
        .score-btn { margin: 5px; padding: 10px 20px; font-size: 16px; cursor: pointer; }
    </style>
</head>
<body>
    <h2>Tamil Terminology Scoring ({current_idx + 1} / {total})</h2>
    <div class="card">
        <p><strong>Question:</strong> {question}</p>
        <p><strong>Model Answer:</strong> {answer}</p>
        <hr>
        <form method="POST">
            <p>Score the Tamil terminology correctness (1-5):</p>
            <input type="hidden" name="item_id" value="{item_id}">
            <button type="submit" name="score" value="1" class="score-btn">1</button>
            <button type="submit" name="score" value="2" class="score-btn">2</button>
            <button type="submit" name="score" value="3" class="score-btn">3</button>
            <button type="submit" name="score" value="4" class="score-btn">4</button>
            <button type="submit" name="score" value="5" class="score-btn">5</button>
        </form>
    </div>
</body>
</html>
"""

HTML_DONE = """
<!DOCTYPE html>
<html>
<head><title>Done</title></head>
<body style="font-family: Arial; text-align: center; margin-top: 50px;">
    <h2>Scoring Complete!</h2>
    <p>Thank you. Results saved to human_scores.json.</p>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    scores = load_scores()
    
    if request.method == 'POST':
        item_id = request.form['item_id']
        score = int(request.form['score'])
        scores[item_id] = score
        save_scores(scores)
        return redirect(url_for('index'))
    
    # Find next unscored item
    for i, item in enumerate(qa_pairs):
        if str(item['id']) not in scores:
            return render_template_string(
                HTML_TEMPLATE,
                current_idx=i,
                total=len(qa_pairs),
                question=item['question'],
                answer=item['model_answer'],
                item_id=item['id']
            )
            
    return render_template_string(HTML_DONE)

if __name__ == '__main__':
    # Run slightly briefly and automatically exit for automated test purposes
    import threading
    import time
    def shutdown():
        time.sleep(2) # Give it enough time to be tested manually if needed
        # In a real environment we'd keep this running, but here we can mock the human scores for end-to-end verification.
    
    print("Flask app running on http://127.0.0.1:5000")
    app.run(port=5000, debug=False)
