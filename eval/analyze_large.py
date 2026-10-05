import json
from sklearn.metrics import cohen_kappa_score

def main():
    try:
        with open('llm_large_scores.json', 'r', encoding='utf-8') as f:
            judge_data = json.load(f)
        with open('large_human_scores.json', 'r', encoding='utf-8') as f:
            human_data = json.load(f)
    except FileNotFoundError as e:
        print(f'Error: {e}')
        return

    judge_scores_map = {str(item['id']): item['judge_score'] for item in judge_data}
    
    y_judge = []
    y_human = []
    disagreements = []
    
    for item_id, human_score in human_data.items():
        if item_id in judge_scores_map:
            j_score = judge_scores_map[item_id]
            y_judge.append(j_score)
            y_human.append(human_score)
            if abs(j_score - human_score) >= 1:
                disagreements.append({
                    'id': item_id,
                    'human': human_score,
                    'judge': j_score,
                    'diff': abs(j_score - human_score)
                })

    kappa = cohen_kappa_score(y_human, y_judge, weights='quadratic')
    
    print('\n--- Validation Pipeline Analysis (Large N=30 Batch) ---')
    print(f'Total Items Analyzed: {len(y_judge)}')
    print(f'Quadratic Weighted Cohen Kappa: {kappa:.3f}')
    
    if kappa < 0.6:
        print('\nWARNING: Low agreement (< 0.6).')
    else:
        print('\nSUCCESS: Good agreement (>= 0.6).')
        
    if disagreements:
        print('\n--- Disagreements ---')
        for d in sorted(disagreements, key=lambda x: x['diff'], reverse=True)[:5]: # Only print top 5
            justification = next(i['justification'] for i in judge_data if str(i['id']) == d['id'])
            print(f"Item ID {d['id']} -> Human: {d['human']} | LLM: {d['judge']}")
            # Truncate justification if too long for printing issue
            print(f"LLM Says: {justification[:100]}...")
    else:
        print('\nNo disagreements found.')

if __name__ == '__main__':
    main()
