import sys
import os
import shutil
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(__file__))

from image.image_service import generate_image
from image.prompt_enhancer import enhance_prompt

subjects = ["human heart", "human eye", "plant cell"]
output_dir = r"C:\Users\YAZHINI\.gemini\antigravity-ide\brain\07e5a5f2-3df1-4bfa-91f7-8e260feefe35\scratch"
os.makedirs(output_dir, exist_ok=True)

for subject in subjects:
    print(f"\nGenerating 3 images for {subject}...")
    for i in range(3):
        # We only need the prompt, not the overlay, so we'll just get the enhanced prompt
        enhanced, _, _, _ = enhance_prompt(subject, "english")
        try:
            # We pass empty labels so no overlay is applied
            image_path = generate_image(prompt=enhanced, labels=[], subject=subject, language="english")
            
            # Copy to scratch directory for user viewing
            target_path = os.path.join(output_dir, f"{subject.replace(' ', '_')}_{i}.png")
            shutil.copy2(image_path, target_path)
            print(f"Generated: {target_path}")
        except Exception as e:
            print(f"Failed on {subject} ({i}): {e}")
