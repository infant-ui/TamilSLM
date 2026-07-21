import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Load env vars
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
NVIDIA_API_URL = os.environ.get("NVIDIA_API_URL", "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.2-klein-4b")

def test_nim_api():
    prompt = "Anatomical diagram of cross-section diagram of a single plant cell showing internal organelles, biology textbook microscope-view style, clean line-art medical illustration style, clearly showing distinct regions and structures, NO TEXT, NO LABELS, NO WRITING, NO NUMBERS, plain white background, high contrast outlines suitable for adding external labels and leader lines"
    
    payload = {
        "prompt": prompt,
        "height": 1024,
        "width": 1024,
        "cfg_scale": 1.0,
        "samples": 1,
        "seed": 0,
        "steps": 4
    }
    
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    safe_headers = headers.copy()
    safe_headers["Authorization"] = "Bearer <HIDDEN_API_KEY>"
    
    print(f"--- REQUEST HEADERS ---")
    print(json.dumps(safe_headers, indent=2))
    
    print(f"\n--- REQUEST PAYLOAD ---")
    print(json.dumps(payload, indent=2))
    
    print(f"\nPrompt Length: {len(prompt)} characters")
    
    print(f"\n--- SENDING REQUEST to {NVIDIA_API_URL} ---")
    try:
        response = requests.post(NVIDIA_API_URL, headers=headers, json=payload, timeout=60)
        print(f"Response Status: {response.status_code}")
        print(f"Response Body (Raw): {response.text}")
        response.raise_for_status()
        print("\nRequest succeeded!")
    except Exception as e:
        print(f"\nRequest failed with exception: {e}")

if __name__ == "__main__":
    test_nim_api()
