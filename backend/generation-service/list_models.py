import os
import requests
from dotenv import load_dotenv

load_dotenv(r"d:\Project Assistan\backend\generation-service\.env")

api_key = os.environ.get("NVIDIA_API_KEY")
headers = {"Authorization": f"Bearer {api_key}"}

try:
    res = requests.get("https://integrate.api.nvidia.com/v1/models", headers=headers, timeout=10)
    if res.status_code == 200:
        models = [m['id'] for m in res.json()['data']]
        # Filter models related to images
        image_keywords = ["sd", "stable", "diffusion", "flux", "image"]
        image_models = [m for m in models if any(k in m.lower() for k in image_keywords)]
        print("All Models:", models)
        print("Image Models:", image_models)
    else:
        print(res.text)
except Exception as e:
    print(f"Error: {e}")
