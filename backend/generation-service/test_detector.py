import os
import logging
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

from image.text_detector import contains_hallucinated_text
from image.image_service import generate_image

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def validate_detector():
    bad_files = [
        "a4d3b0ff18f245c0baeab74ed40e86b6.png",
        "791f1d073e134b7bb40c66bd5b32f805.png",
        "90fd382589564177b029b62d27a46b0c.png",
        "51439ff83578470daa653b85a58741c1.png",
        "d8f03e26900140ddbbfdb5b34f762446.png",
        "df1c1f26318b40dd9566c39811367faa.png",
        "fea88279b354416cab816c307202e589.png",
        "78b8b4dded074cc9a0148ad5f4ba5a03.png",
        "7d4a233ce6f74117854920ec79578231.png",
        "3a1253aa910b44e9863d88467a4dce5d.png",
        "beead78fa6b1465bbf636c2d97a73838.png",
        "041c4acb8af3430bbeb7f7562c8807d5.png",
        "a575f631cf0f4c16a5d83e43a29a2f56.png",
        "422e2ae03b6d4b3883b46c5891f820cb.png",
        "2e174af13a73442c9edd3d5c71a4664f.png",
        "c4f4e604f63e43678db69dae49dc70c0.png",
        "4b673ff4652d4b2c9b55afa783786d27.png",
        "8eb8dbc0941c4a2eb0be87151af8c6fd.png"
    ]
    
    base_dir = r"D:\Project Assistan\backend\generation-service\generated-images\2026\07\16"
    
    # Generate anatomical diagrams to check for false positives on complex linework
    print("Generating 8 anatomical diagrams to test false positives...")
    good_images = []
    good_prompts = [
        "A cross-section diagram of a human heart, biology textbook style, NO LABELS, NO TEXT",
        "A detailed cellular structure of a plant cell, microscopic view, NO LABELS, NO TEXT",
        "Anatomical diagram of a human eye, medical textbook illustration, NO LABELS, NO TEXT",
        "A skeletal system diagram of a human arm, medical illustration, NO LABELS, NO TEXT",
        "A diagram of a neuron cell, biology textbook style, NO LABELS, NO TEXT",
        "A cross-section diagram of a human kidney, biology textbook style, NO LABELS, NO TEXT",
        "A detailed diagram of a chloroplast, microscopic view, NO LABELS, NO TEXT",
        "Anatomical diagram of the human digestive system, medical textbook illustration, NO LABELS, NO TEXT"
    ]
    
    for p in good_prompts:
        try:
            # Note: image_service.py has the detector gate built-in.
            # If it succeeds, it means it found an image the detector thinks is clean.
            path = generate_image(prompt=p, labels=[], subject="test", language="english")
            good_images.append(path)
            print(f"Generated clean diagram: {path}")
        except Exception as e:
            print(f"Failed to generate clean diagram for '{p}' after retries. Error: {e}")
            
    print("\n--- Testing Bad Images ---")
    bad_detected = 0
    for f in bad_files:
        path = os.path.join(base_dir, f)
        detected = contains_hallucinated_text(path, conf_threshold=40)
        print(f"Bad Image {f}: {'DETECTED' if detected else 'MISSED'}")
        if detected: bad_detected += 1
        
    print("\n--- Testing Clean Diagrams (False Positives) ---")
    good_detected = 0
    for path in good_images:
        detected = contains_hallucinated_text(path, conf_threshold=40)
        print(f"Clean Diagram {os.path.basename(path)}: {'FALSE POSITIVE' if detected else 'CLEAN'}")
        if detected: good_detected += 1
        
    print("\n--- SUMMARY ---")
    print(f"Bad Images Detected: {bad_detected}/{len(bad_files)}")
    print(f"Good Images False Positives: {good_detected}/{len(good_images)}")

if __name__ == "__main__":
    validate_detector()
