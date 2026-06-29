# services/retrieval-service/app/ingestion/chapter_parser.py
import re
from typing import List, Dict, Any
from app.ingestion.layout_analyzer import LayoutBlock

# Common bilingual textbook chapter triggers
CHAPTER_REGEX = re.compile(
    r"^(அலகு|அத்தியாயம்|அதிகாரம்|unit|chapter)\s*([ivxlcdm]+|\d+)\s*:?\s*(.*)$",
    re.IGNORECASE
)

class ChapterParser:
    def __init__(self):
        pass

    def detect_chapter_header(self, text: str) -> re.Match:
        """
        Regex-based chapter header detection. Matches Tamil and English prefixes.
        e.g., "அலகு 1: அளவீட்டியல்" or "Unit 3: Light"
        """
        # Clean text to remove extra whitespace/newlines
        clean_text = re.sub(r'\s+', ' ', text).strip()
        return CHAPTER_REGEX.match(clean_text)

    def split_by_chapters(self, blocks: List[LayoutBlock]) -> List[Dict[str, Any]]:
        """
        Organizes page layout blocks into distinct chapter dictionaries.
        """
        chapters = []
        current_chapter = {
            "chapter_no": "0",
            "chapter_title": "Front Matter / Introduction",
            "blocks": []
        }

        for idx, block in enumerate(blocks):
            if block.type == "heading" or len(block.text) < 150:
                match = self.detect_chapter_header(block.text)
                if match:
                    # Save current chapter if it has contents
                    if current_chapter["blocks"]:
                        chapters.append(current_chapter)
                    
                    chap_no = match.group(2).strip()
                    chap_title = match.group(3).strip()
                    if not chap_title:
                        # Sometimes the title is in the next block, use heuristic
                        if idx + 1 < len(blocks) and len(blocks[idx+1].text) < 80:
                            chap_title = blocks[idx+1].text.strip()
                    
                    current_chapter = {
                        "chapter_no": chap_no,
                        "chapter_title": chap_title if chap_title else f"Chapter {chap_no}",
                        "blocks": [block]
                    }
                    continue
            
            current_chapter["blocks"].append(block)

        # Append last chapter
        if current_chapter["blocks"]:
            chapters.append(current_chapter)

        return chapters
