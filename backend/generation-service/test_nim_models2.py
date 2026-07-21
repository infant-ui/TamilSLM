import os
import requests
from dotenv import load_dotenv

load_dotenv(r"d:\Project Assistan\backend\generation-service\.env")

api_key = os.environ.get("NVIDIA_API_KEY")
headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}

# Test more standard NIM image generation model names
test_models = [
    "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.1-schnell",
    "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-3-medium",
    "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-xl"
]

for url in test_models:
    payload = {
        "text_prompts": [{"text": "A simple red apple", "weight": 1}],
        "cfg_scale": 5,
        "steps": 10,
        "seed": 0
    }
    print(f"\nTesting {url}")
    try:
        # Check standard payload
        res = requests.post(url, headers=headers, json=payload, timeout=20)
        print(f"Status with SDXL payload: {res.status_code}")
        if res.status_code != 200:
            # Check flux payload
            payload2 = {
                "prompt": "A simple red apple",
                "cfg_scale": 5,
                "steps": 10,
                "seed": 0
            }
            res2 = requests.post(url, headers=headers, json=payload2, timeout=20)
            print(f"Status with Flux payload: {res2.status_code}")
            if res2.status_code == 200:
                print("Valid Flux Model!")
        else:
            print("Valid SDXL Model!")
    except Exception as e:
        print(f"Error: {e}")
