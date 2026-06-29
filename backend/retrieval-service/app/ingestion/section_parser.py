# services/retrieval-service/app/ingestion/section_parser.py
import re
from typing import List, Dict, Any, Optional
from app.ingestion.layout_analyzer import LayoutBlock

# Match sections like "1.1 base quantities" or "1.2.3 Speed and Velocity" or Tamil digit equivalents
SECTION_REGEX = re.compile(
    r"^(\d+\.\d+(?:\.\d+)?)\s*:?\s*(.*)$",
    re.IGNORECASE
)

class SectionParser:
    def __init__(self):
        pass

    def detect_section_header(self, text: str) -> Optional[tuple[str, str]]:
        """
        Regex-based section header detection. Matches numbers like 1.1 or 1.2.3
        Returns (section_number, section_title) if matched, otherwise None.
        """
        clean_text = re.sub(r'\s+', ' ', text).strip()
        match = SECTION_REGEX.match(clean_text)
        if match:
            return match.group(1), match.group(2).strip()
        return None

    def build_section_hierarchy(self, blocks: List[LayoutBlock]) -> List[Dict[str, Any]]:
        """
        Processes a list of blocks belonging to a chapter, tagging each block
        with its current active section and subsection hierarchy path.
        """
        annotated_blocks = []
        current_section = "General"
        current_subsection = ""

        for block in blocks:
            header_info = self.detect_section_header(block.text)
            if header_info:
                sec_no, sec_title = header_info
                
                # Check if it's a subsection (contains two dots, e.g. 1.1.2)
                dots_count = sec_no.count(".")
                if dots_count == 2:
                    current_subsection = f"{sec_no} {sec_title}"
                else:
                    current_section = f"{sec_no} {sec_title}"
                    current_subsection = ""  # reset subsection on new main section
            
            # Map structural path
            path = current_section
            if current_subsection:
                path += f" > {current_subsection}"
                
            annotated_blocks.append({
                "block": block,
                "section_path": path,
                "section_no": current_subsection.split(" ")[0] if current_subsection else current_section.split(" ")[0]
            })

        return annotated_blocks
