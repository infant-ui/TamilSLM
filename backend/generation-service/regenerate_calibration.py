import os
import shutil
import time
from dotenv import load_dotenv

load_dotenv(r"d:\Project Assistan\backend\generation-service\.env")

from image.image_service import generate_image

PROMPTS = {
    "human_heart": "A cross-section diagram of a human heart, biology textbook style",
    "human_eye": "A cross-section diagram of a human eye, biology textbook style",
    "plant_cell": "A cross-section diagram of a plant cell, biology textbook style"
}

output_dir = r"D:\Project Assistan\backend\generation-service\scratch_calibration"
os.makedirs(output_dir, exist_ok=True)

for subject, prompt in PROMPTS.items():
    print(f"\nGenerating 3 images for {subject}...")
    for i in range(3):
        print(f"  Image {i+1}/3:")
        try:
            start = time.time()
            img_path = generate_image(prompt=prompt, labels=[], subject=subject)
            duration = time.time() - start
            new_path = os.path.join(output_dir, f"{subject}_{i}.png")
            shutil.copy(img_path, new_path)
            print(f"    Success! Saved to {new_path}")
            print(f"    Total time: {duration:.1f}s")
        except Exception as e:
            print(f"    Failed: {e}")
