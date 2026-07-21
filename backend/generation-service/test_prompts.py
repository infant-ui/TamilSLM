import os
import requests
import random
import time
from image.text_detector import contains_hallucinated_text
from dotenv import load_dotenv

load_dotenv()

# Use local test environment instead of image_service.py to bypass retry loops and test raw rates
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")
base_dir = r"D:\Project Assistan\backend\generation-service\generated-images\2026\07\16"
os.makedirs(base_dir, exist_ok=True)

def generate_test_image(prompt: str) -> bool:
    payload = {
        "prompt": prompt,
        "height": 1024,
        "width": 1024,
        "cfg_scale": 1.0,
        "samples": 1,
        "seed": random.randint(0, 2**32 - 1),
        "steps": 4
    }
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    response = requests.post("https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.2-klein-4b", json=payload, headers=headers)
    if response.status_code == 200:
        import base64
        data = response.json()
        b64_image = data.get("artifacts", [])[0].get("base64", "")
        if not b64_image:
            print("API Error: No base64 returned")
            return False
        import uuid
        save_path = os.path.join(base_dir, f"test_{uuid.uuid4().hex}.png")
        with open(save_path, "wb") as fh:
            fh.write(base64.b64decode(b64_image))
        
        has_text = contains_hallucinated_text(save_path, conf_threshold=40)
        os.remove(save_path) # Clean up
        return not has_text # Return True if clean
    else:
        print(f"API Error: {response.status_code}")
        return False

test_prompts = [
    # Group A: "Diagram" & "Textbook" (Baseline ~9% clean)
    "A cross-section diagram of a human heart, biology textbook style",
    
    # Group B: "Medical Illustration" without diagram/textbook
    "A highly detailed medical illustration of a human heart cross-section, professional",
    
    # Group C: "3D Rendering / Visualization"
    "A photorealistic 3D rendering of the internal structure of a human heart, educational visualization",
    
    # Group D: "Microscopic View" (for cells)
    "A high resolution microscopic photograph of a plant cell showing internal organelles"
]

print("Testing raw per-attempt clean rate across prompt styles...\n")
for p in test_prompts:
    clean_count = 0
    attempts = 5
    for i in range(attempts):
        if generate_test_image(p):
            clean_count += 1
    print(f"Prompt: '{p}'")
    print(f"Clean Rate: {clean_count}/{attempts} ({clean_count/attempts*100:.0f}%)\n")
