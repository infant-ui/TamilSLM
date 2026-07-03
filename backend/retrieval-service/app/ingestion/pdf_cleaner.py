# services/retrieval-service/app/ingestion/pdf_cleaner.py
import re
import os
import cv2
import numpy as np
import fitz  # PyMuPDF
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Constants for layout boundaries
HEADER_MARGIN_RATIO = 0.08  # top 8%
FOOTER_MARGIN_RATIO = 0.92  # bottom 8%

class PDFCleaner:
    def __init__(self, output_img_dir: Optional[str] = None):
        self.output_img_dir = output_img_dir
        if output_img_dir:
            os.makedirs(output_img_dir, exist_ok=True)

    def is_copyright_page(self, text: str) -> bool:
        """
        Detects if a page is a publication copyright/publishing details page.
        """
        copyright_keywords = [
            "first edition", "reprint", "published by", "copyright",
            "பதிப்பு", "உரிமம்", "வெளியீடு", "விலை", "அச்சிட்டோர்",
            "printed by", "isbn", "government of tamil nadu", "அரசு"
        ]
        text_lower = text.lower()
        matches = sum(1 for kw in copyright_keywords if kw in text_lower)
        # If the page contains 3 or more copyright-specific keywords, classify as copyright page
        return matches >= 3

    def is_blank_page(self, page: fitz.Page) -> bool:
        """
        Checks if a page has minimal text and graphics.
        """
        text = page.get_text("text").strip()
        drawings = page.get_drawings()
        images = page.get_images()
        return len(text) < 15 and len(drawings) < 3 and len(images) == 0

    def detect_qr_code_opencv(self, pix) -> Optional[Tuple[int, int, int, int]]:
        """
        Uses OpenCV contour analysis to find square-like boxes matching QR code dimensions.
        Returns bounding box (x0, y0, x1, y1) in relative page coordinates if found.
        """
        try:
            # Convert PyMuPDF pixmap to OpenCV image
            img_data = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
            if pix.n == 4:
                gray = cv2.cvtColor(img_data, cv2.COLOR_BGRA2GRAY)
            elif pix.n == 3:
                gray = cv2.cvtColor(img_data, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_data

            # Threshold and find contours
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = float(w)/h
                # QR codes are square (aspect ratio near 1.0) and typically between 50x50 and 300x300 pixels
                if 0.9 <= aspect_ratio <= 1.1 and 40 <= w <= 400 and 40 <= h <= 400:
                    # Return bounding box in pixel coordinates (needs translation to PyMuPDF coords)
                    return (x, y, x + w, y + h)
        except cv2.error as e:
            logger.error(f"OpenCV error detecting QR code: {e}. Skipping QR detection for this image.", exc_info=True)
        except Exception as e:
            logger.error(f"Unexpected error detecting QR code: {e}. Skipping QR detection for this image.", exc_info=True)
        return None

    def clean_page_text_blocks(self, page: fitz.Page) -> List[Dict]:
        """
        Extracts and filters text blocks, discarding headers, footers, page numbers,
        watermarks, print metadata, and QR captions.
        """
        width = page.rect.width
        height = page.rect.height
        
        header_limit = height * HEADER_MARGIN_RATIO
        footer_limit = height * FOOTER_MARGIN_RATIO

        raw_blocks = page.get_text("blocks")
        cleaned_blocks = []

        # Find QR boxes on this page to remove captions near them
        qr_bboxes = []
        for img_info in page.get_image_info():
            bbox = img_info.get("bbox")  # (x0, y0, x1, y1)
            # Try to see if this image is a QR code (using aspect ratio checks on PDF images)
            img_w = bbox[2] - bbox[0]
            img_h = bbox[3] - bbox[1]
            if img_h > 0 and 0.95 <= (img_w / img_h) <= 1.05 and 40 <= img_w <= 120:
                qr_bboxes.append(bbox)

        for block in raw_blocks:
            x0, y0, x1, y1, text, block_no, block_type = block
            text_strip = text.strip()
            
            if not text_strip:
                continue

            # 1. Header/Footer Coordinate Filtering
            if y1 < header_limit:
                # Store potential header metadata but skip from content indexing
                continue
            if y0 > footer_limit:
                # Skip page numbers and running footers
                continue

            # 2. Page Number Heuristic
            if re.match(r"^\d+$", text_strip) or re.match(r"^-\s*\d+\s*-$", text_strip):
                continue

            # 3. Watermarks & Publisher Metadata (Regex matches)
            metadata_patterns = [
                r"government of tamil nadu", r"அரசு",
                r"first edition", r"\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}", # print timestamp
                r".*\.indd", r".*\.ai", r"http://.*"
            ]
            if any(re.search(pat, text_strip.lower()) for pat in metadata_patterns):
                continue

            # 4. QR Caption Removal
            # Captions like "Scan this QR code..." or "QR code instructions..."
            is_qr_caption = False
            qr_caption_keywords = ["qr code", "வளையப் படம்", "உரலி", "scan", "விரைவுக் குறியீடு"]
            if any(kw in text_strip.lower() for kw in qr_caption_keywords):
                # Verify if it's close to a detected QR image box
                for qr_box in qr_bboxes:
                    # If within 100 pixels vertically and overlaps horizontally
                    if abs(y0 - qr_box[3]) < 100 and (x0 < qr_box[2] and x1 > qr_box[0]):
                        is_qr_caption = True
                        break
            if is_qr_caption:
                continue

            # Preserve block
            cleaned_blocks.append({
                "bbox": (x0, y0, x1, y1),
                "text": text_strip,
                "type": "text"
            })

        return cleaned_blocks

    def extract_figures_and_tables(self, page: fitz.Page, page_no: int) -> List[Dict]:
        """
        Extracts figures and tables from the page while discarding small decorative icons.
        Returns a list of extracted elements.
        """
        elements = []
        
        # 1. Preserve Tables
        tables = page.find_tables()
        for idx, table in enumerate(tables):
            bbox = table.bbox  # (x0, y0, x1, y1)
            # Reconstruct table as markdown format
            df = table.to_pandas()
            markdown_table = df.to_markdown(index=False)
            elements.append({
                "type": "table",
                "bbox": bbox,
                "content": markdown_table,
                "id": f"table_{page_no}_{idx}"
            })

        # 2. Extract Figures with Captions
        images = page.get_images()
        raw_blocks = page.get_text("blocks")
        
        for idx, img_info in enumerate(page.get_image_info()):
            bbox = img_info.get("bbox")  # (x0, y0, x1, y1)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            
            # Skip tiny decorative icons, bullet markers, or running layout strips
            if w < 30 or h < 30:
                continue
                
            # Skip QR codes (which are captured/removed separately)
            if 0.95 <= (w / h) <= 1.05 and 40 <= w <= 120:
                continue

            # Look for captions near this image (within 100 pixels below or above)
            caption = ""
            for block in raw_blocks:
                bx0, by0, bx1, by1, btext, _, _ = block
                btext_strip = btext.strip()
                # Check for standard figure identifiers
                if re.match(r"^(Figure|Fig\.|படம்)\s*\d+", btext_strip, re.IGNORECASE):
                    # Check vertical proximity
                    if abs(by0 - bbox[3]) < 120 or abs(bbox[1] - by1) < 120:
                        caption = btext_strip
                        break

            # Save figure image if output directory is defined
            saved_path = ""
            if self.output_img_dir:
                try:
                    xref = img_info.get("xref")
                    if xref:
                        base_image = page.parent.extract_image(xref)
                        image_bytes = base_image["image"]
                        ext = base_image["ext"]
                        filename = f"fig_p{page_no}_{idx}.{ext}"
                        full_path = os.path.join(self.output_img_dir, filename)
                        with open(full_path, "wb") as f:
                            f.write(image_bytes)
                        saved_path = full_path
                except Exception as e:
                    logger.error(f"Failed to extract image {idx} on page {page_no}: {e}. Skipping this figure.", exc_info=True)

            elements.append({
                "type": "figure",
                "bbox": bbox,
                "caption": caption,
                "image_path": saved_path,
                "id": f"fig_{page_no}_{idx}"
            })

        return elements
