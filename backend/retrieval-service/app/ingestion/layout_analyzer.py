# services/retrieval-service/app/ingestion/layout_analyzer.py
import logging
import re
import fitz  # PyMuPDF
from typing import List, Dict, Tuple, Optional
from app.ingestion.hardware_detector import get_hardware_level

logger = logging.getLogger("ingestion.layout_analyzer")

# Attempt imports for optional Level 2 GPU packages
HAS_GPU_LAYOUT = False
try:
    import layoutparser as lp
    import cv2
    # We can import detectron2 or layoutlmv3 utilities here if present
    HAS_GPU_LAYOUT = True
except ImportError:
    pass

class LayoutBlock:
    def __init__(self, bbox: Tuple[float, float, float, float], text: str, block_type: str):
        self.bbox = bbox  # (x0, y0, x1, y1)
        self.text = text.strip()
        self.type = block_type  # "heading", "paragraph", "table", "box", "list", "figure"

class LayoutAnalyzer:
    def __init__(self):
        self.hw_level = get_hardware_level()
        self.use_gpu_model = (self.hw_level == "LEVEL_2_GPU") and HAS_GPU_LAYOUT
        
        if self.use_gpu_model:
            logger.info("Initializing GPU-based LayoutParser model (LayoutLMv3/Detectron2)...")
            try:
                # Load LayoutLMv3 or PubLayNet model
                self.model = lp.Detectron2LayoutModel(
                    config_path="lp://PubLayNet/layoutlmv3_base_inference/config",
                    extra_config=["MODEL.DEVICE", "cuda"],
                    label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}
                )
            except Exception as e:
                logger.warning(f"Failed to load GPU LayoutModel: {str(e)}. Falling back to CPU heuristics.")
                self.use_gpu_model = False

    def is_page_searchable(self, page: fitz.Page) -> bool:
        """
        Detects if a PDF page is digitally searchable (has embedded text streams)
        or if it is scanned (requiring full page OCR).
        """
        text = page.get_text("text")
        return len(text.strip()) > 100

    def analyze_layout_cpu(self, page: fitz.Page, cleaned_text_blocks: List[Dict]) -> List[LayoutBlock]:
        """
        Level 1 (CPU): Rule-based layout parsing using PyMuPDF bounding boxes.
        Clusters text blocks, detects columns, and sorts in natural reading order.
        """
        width = page.rect.width
        
        # Sort blocks by vertical y0 coordinate first
        blocks = sorted(cleaned_text_blocks, key=lambda b: b["bbox"][1])
        
        # 1. Identify Columns
        # Standard two-column check: find if multiple blocks exist at similar vertical bands
        # but with non-overlapping horizontal spreads.
        midpoint = width / 2
        col1_blocks = []
        col2_blocks = []
        full_width_blocks = []

        for b in blocks:
            x0, y0, x1, y1 = b["bbox"]
            w = x1 - x0
            
            # If a block spans more than 65% of the page width, classify it as full width
            if w > (width * 0.65):
                full_width_blocks.append(b)
            # If it's located mostly on the left half of the page
            elif x1 < (midpoint * 1.15) and x0 < midpoint:
                col1_blocks.append(b)
            # If it's located mostly on the right half of the page
            elif x0 > (midpoint * 0.85) and x1 > midpoint:
                col2_blocks.append(b)
            else:
                full_width_blocks.append(b)

        # 2. Reconstruct Reading Order
        # Group left and right blocks into vertical layout structures
        sorted_layout = []
        
        # Merge columns by slicing vertically:
        # If there are full width blocks (like headings or tables), they act as dividers.
        all_blocks = []
        
        # In a robust heuristic: group blocks by their vertical overlap.
        # For simplicity and accuracy in school textbooks, we sort using columns:
        # We partition the page into horizontal bands based on full-width blocks.
        dividers = sorted(full_width_blocks, key=lambda b: b["bbox"][1])
        
        last_y = 0.0
        for div in dividers:
            div_y0 = div["bbox"][1]
            div_y1 = div["bbox"][3]
            
            # Extract column blocks that are above this divider
            band_col1 = [b for b in col1_blocks if last_y <= b["bbox"][1] < div_y0]
            band_col2 = [b for b in col2_blocks if last_y <= b["bbox"][1] < div_y0]
            
            # Sort band elements vertically
            band_col1 = sorted(band_col1, key=lambda b: b["bbox"][1])
            band_col2 = sorted(band_col2, key=lambda b: b["bbox"][1])
            
            # Add Left Column, then Right Column, then the Divider block itself
            all_blocks.extend(band_col1)
            all_blocks.extend(band_col2)
            all_blocks.append(div)
            
            last_y = div_y1

        # Add remaining blocks below the last divider
        rem_col1 = sorted([b for b in col1_blocks if b["bbox"][1] >= last_y], key=lambda b: b["bbox"][1])
        rem_col2 = sorted([b for b in col2_blocks if b["bbox"][1] >= last_y], key=lambda b: b["bbox"][1])
        all_blocks.extend(rem_col1)
        all_blocks.extend(rem_col2)

        # Handle case where there were no dividers
        if not dividers:
            col1_sorted = sorted(col1_blocks, key=lambda b: b["bbox"][1])
            col2_sorted = sorted(col2_blocks, key=lambda b: b["bbox"][1])
            all_blocks = col1_sorted + col2_sorted + full_width_blocks
            # Sort everything vertically again if it was mostly single column anyway
            if len(col1_blocks) < 2 or len(col2_blocks) < 2:
                all_blocks = sorted(blocks, key=lambda b: b["bbox"][1])

        # 3. Label Block Types (Title, List, Paragraph, Heading)
        layout_blocks = []
        for b in all_blocks:
            text = b["text"]
            bbox = b["bbox"]
            
            # Simple heuristic labelling based on text pattern & length
            block_type = "paragraph"
            if len(text) < 120 and (re.match(r"^(\d+\.\d+|\d+\.|[IVXLCDM]+\.)", text) or text.isupper()):
                block_type = "heading"
            elif text.startswith("•") or text.startswith("-") or re.match(r"^(\d+\))", text):
                block_type = "list"
            elif "bbox_type" in b:
                block_type = b["bbox_type"]
                
            layout_blocks.append(LayoutBlock(bbox, text, block_type))

        return layout_blocks

    def analyze_layout_gpu(self, page: fitz.Page, img_path: str) -> List[LayoutBlock]:
        """
        Level 2 (GPU): Deep learning layout analysis using LayoutParser models.
        Segments the page into bounding boxes with structural labels.
        """
        # Load image via CV2
        img = cv2.imread(img_path)
        
        # Execute layout parser inference
        layout = self.model.detect(img)
        
        layout_blocks = []
        # Translate layout objects back to relative coordinates and match text inside PDF
        for block in layout:
            x0, y0, x1, y1 = block.coordinates
            block_type = block.type.lower() # "text", "title", "list", "table", "figure"
            
            # Map coordinates from image scale back to PDF page scale
            # (Assumes page scale translation maps correctly)
            pdf_bbox = (x0, y0, x1, y1)
            
            # Extract text intersecting with these coordinates
            text = page.get_text("text", clip=pdf_bbox)
            
            layout_blocks.append(LayoutBlock(pdf_bbox, text, block_type))
            
        return layout_blocks

    def segment_page(self, page: fitz.Page, cleaned_text_blocks: List[Dict], temp_img_path: Optional[str] = None) -> List[LayoutBlock]:
        """
        Main entrypoint. Auto-selects between CPU heuristics and GPU neural layout engines.
        """
        if self.use_gpu_model and temp_img_path:
            try:
                return self.analyze_layout_gpu(page, temp_img_path)
            except Exception as e:
                logger.warning(f"GPU layout segmentation failed: {str(e)}. Falling back to CPU.")
                
        return self.analyze_layout_cpu(page, cleaned_text_blocks)
