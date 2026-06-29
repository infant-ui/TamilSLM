# services/retrieval-service/app/ingestion/ocr_cleaner.py
import re
import logging
import unicodedata
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
from typing import Tuple, Optional
from app.ingestion.hardware_detector import get_hardware_level

logger = logging.getLogger("ingestion.ocr_cleaner")

# Attempt imports for Level 2 PaddleOCR GPU acceleration
HAS_PADDLEOCR = False
try:
    from paddleocr import PaddleOCR
    HAS_PADDLEOCR = True
except ImportError:
    pass

class OCRCleaner:
    def __init__(self):
        self.hw_level = get_hardware_level()
        self.use_paddle = (self.hw_level == "LEVEL_2_GPU") and HAS_PADDLEOCR
        
        if self.use_paddle:
            logger.info("Initializing PaddleOCR with GPU acceleration...")
            try:
                # Initialize PaddleOCR for Tamil and English
                self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang="ta", use_gpu=True)
            except Exception as e:
                logger.warning(f"Failed to initialize PaddleOCR: {str(e)}. Falling back to Tesseract CPU.")
                self.use_paddle = False

    def normalize_tamil_unicode(self, text: str) -> str:
        """
        Normalizes Tamil Unicode characters to NFC (Canonical Composition).
        Fixes common OCR ligature splitting where vowel signs (e.g. ொ, ோ, ௌ) 
        are separated from their base consonants.
        """
        if not text:
            return ""
        
        # 1. Standard Unicode normalization (NFC)
        normalized = unicodedata.normalize("NFC", text)
        
        # 2. Fix OCR artifacts where vowel modifier tokens are detached/split
        # For example, replacing a split combination of ெ + consonant + ா with ொ
        # Tamil Unicode blocks: Consonants (க்-ன்), Modifiers (ா, ி, ீ, ு, ூ, ெ, ே, ை, ொ, ோ, ௌ, ்)
        # Re-assemble double-part vowel signs that get separated
        split_patterns = {
            r"ெ([\u0b85-\u0bbf\u0bc0-\u0bcd])ா": r"\1ொ",  # ெ + consonant + ா -> ொ
            r"ே([\u0b85-\u0bbf\u0bc0-\u0bcd])ா": r"\1ோ",  # ே + consonant + ா -> ோ
            r"ெ([\u0b85-\u0bbf\u0bc0-\u0bcd])ள": r"\1ௌ",  # ெ + consonant + ள -> ௌ
        }
        for pat, repl in split_patterns.items():
            normalized = re.sub(pat, repl, normalized)
            
        return normalized

    def clean_broken_words_and_hyphens(self, text: str) -> str:
        """
        Reconnects lines that end with a hyphen (broken line wraps).
        - English: photosyn-\nthesis -> photosynthesis
        - Tamil: ஒளிச்சேர்க்-\nகை -> ஒளிச்சேர்க்கை
        """
        # Reconnect words split across lines by a hyphen followed by a newline and whitespace
        text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)
        
        # Tamil specific line splits (often doesn't use standard hyphens, but splits mid-word)
        # If the line ends with a Tamil consonant character lacking a vowel (ends with pulli ்)
        # and the next line begins with a Tamil letter, check if they should be joined.
        # We can also handle simple newline cleanups by replacing single newlines with spaces,
        # unless they are paragraph breaks (indicated by double newlines).
        lines = text.split("\n")
        cleaned_lines = []
        for i, line in enumerate(lines):
            line_strip = line.strip()
            if not line_strip:
                cleaned_lines.append("")
                continue
                
            # If this is not the last line, and the next line exists
            if i < len(lines) - 1:
                next_line_strip = lines[i+1].strip()
                if next_line_strip:
                    # If this line ends with a Tamil word fragment (e.g. ending in a consonant or non-punctuation)
                    # and the next line starts with a lowercase letter or Tamil modifier vowel, merge them.
                    # In school textbooks, it's safest to merge lines in a paragraph with a space,
                    # unless a hyphen was present.
                    if line_strip.endswith("-"):
                        # Already handled by regex or we strip it here
                        line_strip = line_strip[:-1]
                        cleaned_lines.append(line_strip)
                    else:
                        cleaned_lines.append(line_strip + " ")
                else:
                    cleaned_lines.append(line_strip + "\n")
            else:
                cleaned_lines.append(line_strip)
                
        joined = "".join(cleaned_lines)
        # Replace multiple spaces with a single space
        joined = re.sub(r" {2,}", " ", joined)
        return joined.strip()

    def filter_ocr_garbage(self, text: str) -> str:
        """
        Identifies and screens out garbage character sequences produced by scanner/OCR noise.
        If a text block contains a high density of non-alphanumeric noise, returns empty string.
        """
        if not text:
            return ""
        
        # Calculate ratio of special characters
        total_chars = len(text)
        if total_chars < 5:
            return text
            
        # Count non-alphanumeric characters, ignoring standard spaces, punctuation, and Tamil character blocks
        # Tamil unicode range is \u0b80-\u0bff
        noise_chars = len(re.findall(r"[^\w\s\u0b80-\u0bff\.,\?\!\-\(\)]", text))
        noise_ratio = noise_chars / total_chars
        
        if noise_ratio > 0.15:
            logger.debug(f"Filtering OCR garbage block: {text}")
            return ""
            
        return text

    def perform_ocr_on_bbox(self, page: fitz.Page, bbox: Tuple[float, float, float, float], lang: str = "eng+tam") -> Tuple[str, float]:
        """
        Executes OCR on a specific bounding box of the page.
        - Primary: PaddleOCR (if GPU Level 2 is enabled)
        - Fallback: Tesseract OCR (with confidence filtering)
        """
        # Crop the bounding box area from the page
        rect = fitz.Rect(bbox)
        # Zoom in for better OCR accuracy (2x resolution)
        pix = page.get_pixmap(clip=rect, matrix=fitz.Matrix(2, 2))
        
        # Convert to PIL Image
        img_data = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        ocr_text = ""
        confidence = 0.0
        
        # 1. Try primary GPU PaddleOCR if active
        if self.use_paddle:
            try:
                # Convert PIL to cv2 numpy array
                opencv_img = np.array(img_data)
                result = self.paddle_ocr.ocr(opencv_img, cls=True)
                
                # Parse PaddleOCR outputs: result is a list of lines [[coordinates, (text, confidence)]]
                if result and result[0]:
                    texts = []
                    conf_sum = 0.0
                    count = 0
                    for line in result[0]:
                        texts.append(line[1][0])
                        conf_sum += line[1][1]
                        count += 1
                    ocr_text = " ".join(texts)
                    confidence = conf_sum / count if count > 0 else 0.0
            except Exception as e:
                logger.warning(f"PaddleOCR inference failed: {str(e)}. Falling back to Tesseract.")
                
        # 2. Use Tesseract if PaddleOCR is inactive, failed, or returned low confidence (<0.7)
        if not ocr_text or confidence < 0.70:
            try:
                # Run tesseract via pytesseract
                config = "--oem 3 --psm 6" # standard LSTM engine
                data = pytesseract.image_to_data(img_data, lang=lang, config=config, output_type=pytesseract.Output.DICT)
                
                # Extract words and confidences
                words = []
                conf_sum = 0.0
                count = 0
                for idx, word in enumerate(data["text"]):
                    w_strip = word.strip()
                    if w_strip:
                        words.append(w_strip)
                        # Tesseract conf ranges from -1 to 100
                        conf = data["conf"][idx]
                        if conf > 0:
                            conf_sum += (conf / 100.0)
                            count += 1
                
                ocr_text = " ".join(words)
                confidence = conf_sum / count if count > 0 else 0.0
            except Exception as e:
                logger.error(f"Tesseract OCR failed: {str(e)}")
                
        # 3. Apply post-cleanup transformations
        normalized_text = self.normalize_tamil_unicode(ocr_text)
        reconnected_text = self.clean_broken_words_and_hyphens(normalized_text)
        cleaned_text = self.filter_ocr_garbage(reconnected_text)
        
        return cleaned_text, confidence
