import sys
import os
import time

sys.path.append(os.path.dirname(__file__))

from image.image_service import generate_image
from image.prompt_enhancer import enhance_prompt

subjects = [
    ("human heart", "tamil"),
    ("human eye diagram", "english"),
    ("plant cell anatomy", "bilingual"),
    ("mitochondria", "bilingual") # Unknown subject test
]

for prompt, medium in subjects:
    print(f"\n--- Testing: {prompt} ({medium}) ---")
    try:
        enhanced, labels, subject, language = enhance_prompt(prompt, medium)
        print(f"Subject: {subject}")
        print(f"Language: {language}")
        print(f"Labels: {labels}")
        print(f"Enhanced Prompt: {enhanced}")
        
    except Exception as e:
        print(f"Error: {e}")
