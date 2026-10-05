import json

def generate_mock_human_scores():
    # Simulate a human scoring the same 10 items.
    # Scores are exactly the same as judge logic except maybe some off-by-one differences
    mock_scores = {
        "1": 3,
        "2": 5,
        "3": 3,
        "4": 5,
        "5": 3,
        "6": 3,
        "7": 5,
        "8": 3,
        "9": 5,
        "10": 3
    }
    with open('human_scores.json', 'w', encoding='utf-8') as f:
        json.dump(mock_scores, f, indent=2)
    print("Mock human scores generated for testing.")

if __name__ == "__main__":
    generate_mock_human_scores()
