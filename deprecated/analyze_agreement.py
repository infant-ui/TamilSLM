import json
from sklearn.metrics import cohen_kappa_score

def main():
    try:
        with open('judge_scores.json', 'r', encoding='utf-8') as f:
            judge_data = json.load(f)
        
        with open('human_scores.json', 'r', encoding='utf-8') as f:
            human_data = json.load(f)
            
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # Align scores by item ID
    judge_scores_map = {str(item['id']): item['judge_score'] for item in judge_data}
    
    y_judge = []
    y_human = []
    disagreements = []
    
    for item_id, human_score in human_data.items():
        if item_id in judge_scores_map:
            j_score = judge_scores_map[item_id]
            y_judge.append(j_score)
            y_human.append(human_score)
            
            # Flag largest disagreements (difference >= 2)
            if abs(j_score - human_score) >= 2:
                disagreements.append({
                    "id": item_id,
                    "human": human_score,
                    "judge": j_score,
                    "diff": abs(j_score - human_score)
                })

    if not y_judge:
        print("No matching items found between judge and human scores.")
        return

    # Calculate Quadratic Weighted Kappa (weights='quadratic')
    kappa = cohen_kappa_score(y_human, y_judge, weights='quadratic')
    
    print("\n--- Validation Pipeline Analysis ---")
    print(f"Total Items Analyzed: {len(y_judge)}")
    print(f"Quadratic Weighted Cohen's Kappa: {kappa:.3f}")
    
    if kappa < 0.6:
        print("\nWARNING: Low agreement (< 0.6).")
        print("Suggestion: The judge's logic or rubric prompt may need revision.")
    else:
        print("\nSUCCESS: Good agreement (>= 0.6). The LLM judge aligns well with human scoring.")
        
    if disagreements:
        print("\n--- Largest Disagreements (|Human - Judge| >= 2) ---")
        for d in sorted(disagreements, key=lambda x: x['diff'], reverse=True):
            print(f"Item ID {d['id']} -> Human: {d['human']} | Judge: {d['judge']}")
    else:
        print("\nNo major disagreements found (all differences < 2).")

if __name__ == "__main__":
    main()
