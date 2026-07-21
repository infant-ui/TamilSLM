import os
import requests
from dotenv import load_dotenv

load_dotenv(r"d:\Project Assistan\backend\generation-service\.env")

api_key = os.environ.get("NVIDIA_API_KEY")
headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}

# 1. Test diffusiongemma
dg_url = "https://integrate.api.nvidia.com/v1/models/google/diffusiongemma-26b-a4b-it/generate"
# or maybe "https://ai.api.nvidia.com/v1/genai/google/diffusiongemma-26b-a4b-it" ?
dg_url2 = "https://ai.api.nvidia.com/v1/genai/google/diffusiongemma-26b-a4b-it"

payload = {
    "prompt": "A simple red apple",
    "cfg_scale": 5,
    "steps": 10,
    "seed": 0
}

print(f"Testing {dg_url}")
res = requests.post(dg_url, headers=headers, json=payload, timeout=20)
print(f"Status: {res.status_code}")
if res.status_code != 200:
    print(res.text[:200])

print(f"\nTesting {dg_url2}")
res2 = requests.post(dg_url2, headers=headers, json=payload, timeout=20)
print(f"Status: {res2.status_code}")
if res2.status_code != 200:
    print(res2.text[:200])

