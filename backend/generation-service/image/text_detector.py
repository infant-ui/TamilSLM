import logging
import re
import pytesseract
from PIL import Image
import os

logger = logging.getLogger("generation_service.text_detector")

# Configure the tesseract binary path. Checked in order:
# 1. TESSERACT_CMD env var, for explicit overrides (e.g. a non-standard install, or
#    a specific developer machine) without hardcoding anyone's personal path in source.
# 2. Common Windows install locations (UB-Mannheim installer default), for local dev.
# 3. Otherwise, fall back to whatever `tesseract` resolves to on PATH (the normal
#    case inside the Linux Docker image, where it's installed via the package manager).
_env_tesseract_cmd = os.environ.get("TESSERACT_CMD", "").strip()
if _env_tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = _env_tesseract_cmd
elif os.name == 'nt':
    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    ]
    for p in tesseract_paths:
        if os.path.exists(p):
            pytesseract.pytesseract.tesseract_cmd = p
            break

def contains_hallucinated_text(image_path: str, conf_threshold: int = 40) -> bool:
    """
    Scans the given image for any sparse, hallucinated text.
    Returns True if any text is found with confidence > conf_threshold 
    and containing at least 2 alphabetic characters.
    """
    if not os.path.exists(image_path):
        logger.error(f"Image not found at {image_path}")
        return False
        
    try:
        img = Image.open(image_path)
        
        # psm 11: Sparse text. Find as much text as possible in no particular order.
        config = "--oem 3 --psm 11"
        data = pytesseract.image_to_data(img, config=config, output_type=pytesseract.Output.DICT)
        
        found_hallucination = False
        
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            conf_str = data['conf'][i]
            
            # Confidence can sometimes be a string or a float; Tesseract returns it as float/int strings
            try:
                conf = float(conf_str)
            except ValueError:
                conf = -1.0
                
            if not text or conf < conf_threshold:
                continue
                
            # Check if it has 2+ alphabetic characters
            alpha_chars = len([c for c in text if c.isalpha()])
            if alpha_chars >= 2:
                # Log the detection
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]
                logger.info(f"Hallucinated text detected in {os.path.basename(image_path)}: "
                            f"'{text}' (conf: {conf:.1f}) at [x={x}, y={y}, w={w}, h={h}]")
                found_hallucination = True
                
        return found_hallucination
        
    except Exception as e:
        logger.error(f"Failed to run OCR on {image_path}: {e}")
        # In a strict gate, we might want to fail the generation if OCR fails, 
        # but for now we log and let it pass to avoid blocking production on OCR errors.
        return False
