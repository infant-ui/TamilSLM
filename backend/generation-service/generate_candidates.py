import os
import shutil
import time
from dotenv import load_dotenv

load_dotenv(r"d:\Project Assistan\backend\generation-service\.env")

from image.image_service import generate_image

PROMPTS = {
    "human_eye": "A cross-section diagram of a human eye, biology textbook style",
    "plant_cell": "A cross-section diagram of a plant cell, biology textbook style"
}

output_dir = r"D:\Project Assistan\backend\generation-service\candidates"
os.makedirs(output_dir, exist_ok=True)

for subject in ["plant_cell"]:
    prompt = PROMPTS[subject]
    num_to_generate = 5
    print(f"\nGenerating {num_to_generate} candidates for {subject}...")
    for i in range(num_to_generate):
        print(f"  Candidate {i+1}/{num_to_generate}:")
        try:
            start = time.time()
            img_path = generate_image(prompt=prompt, labels=[], subject=subject)
            duration = time.time() - start
            new_path = os.path.join(output_dir, f"{subject}_candidate_{i}.png")
            shutil.copy(img_path, new_path)
            print(f"    Success! Saved to {new_path}")
            print(f"    Total time: {duration:.1f}s")
        except Exception as e:
            print(f"    Failed: {e}")
