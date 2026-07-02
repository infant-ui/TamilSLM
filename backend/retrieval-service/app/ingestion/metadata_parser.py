# services/retrieval-service/app/ingestion/metadata_parser.py
import os
import re
from pydantic import BaseModel, Field
from typing import Optional

class BookMetadata(BaseModel):
    class_level: int = Field(..., description="Grade level of the book (e.g. 6, 7, 8)")
    subject: str = Field(..., description="Subject name (e.g., science, maths, social_science)")
    medium: str = Field(..., description="tamil or english medium")
    language: str = Field(..., description="ta or en code")
    content_type: str = Field(..., description="textbook, guide, previous_year, or teacher_notes")
    term: int = Field(0, description="1, 2, 3, or 0 for full year")
    year: int = Field(2024, description="Year of publication")
    publisher: Optional[str] = Field("Tamil Nadu Textbook and Educational Services Corporation", description="Publisher name")
    edition: Optional[str] = Field("Unknown Edition", description="Book edition details")
    filename: str = Field(..., description="Original filename")
    relative_path: str = Field(..., description="Relative file path from data root")

class MetadataParser:
    def __init__(self):
        # Broad patterns to capture flexible filenames
        self.term_pattern = re.compile(
            r"class[_\s]?(?P<class>\d+)[_\s]?(?P<subject>[a-z_]+)[_\s]?term[_\s]?(?P<term>[1-3])[_\s]?(?P<medium>tamil|english)[_\s]?(?P<type>textbook|guide|previous[_\s-]?year|teacher[_\s-]?notes)",
            re.IGNORECASE
        )
        self.fullyear_pattern = re.compile(
            r"class[_\s]?(?P<class>\d+)[_\s]?(?P<subject>[a-z_]+)[_\s]?fullyear[_\s]?(?P<medium>tamil|english)[_\s]?(?P<type>textbook|guide|previous[_\s-]?year|teacher[_\s-]?notes)",
            re.IGNORECASE
        )
        self.prev_pattern = re.compile(
            r"class[_\s]?(?P<class>\d+)[_\s]?(?P<subject>[a-z_]+)[_\s]?(?P<year>\d{4})[_\s]?(?P<medium>tamil|english)[_\s]?(?P<type>textbook|guide|previous[_\s-]?year|teacher[_\s-]?notes)",
            re.IGNORECASE
        )

    def parse_from_filename(self, filename: str, relative_path: str) -> Optional[BookMetadata]:
        # Try path-based parsing first since the directory layout is structured and reliable
        parts = [p.strip().lower() for p in relative_path.replace("\\", "/").split("/") if p.strip()]
        
        class_idx = -1
        class_level = None
        for i, part in enumerate(parts):
            match = re.match(r"^class[_\s-]?(\d+)$", part)
            if match:
                class_level = int(match.group(1))
                class_idx = i
                break
                
        if class_level is not None and class_idx != -1:
            # We found a class folder! Structure: .../class_X/<subject>/<medium>/<content_type>/[optional term]/[filename]
            # 1. Subject (immediately follows class folder)
            subject = "science"
            if len(parts) > class_idx + 1:
                subject = parts[class_idx + 1]
                
            # 2. Medium (follows subject)
            medium = "english"
            if len(parts) > class_idx + 2:
                raw_medium = parts[class_idx + 2]
                if raw_medium in ["tamil", "english"]:
                    medium = raw_medium
                else:
                    # fallback check if any segment contains medium keywords
                    for part in parts[class_idx + 2:]:
                        if part in ["tamil", "english"]:
                            medium = part
                            break
                            
            # 3. Content Type (follows medium)
            content_type = "textbook"
            if len(parts) > class_idx + 3:
                raw_type = parts[class_idx + 3]
                if "textbook" in raw_type:
                    content_type = "textbook"
                elif "guide" in raw_type:
                    content_type = "guide"
                elif "prev" in raw_type or "year" in raw_type:
                    content_type = "previous_year"
                elif "teacher" in raw_type:
                    content_type = "teacher_notes"
                elif "firecrawl" in raw_type:
                    content_type = "firecrawl_education"
                    
            # 4. Term (look in path segments)
            term = 0
            for part in parts:
                term_match = re.search(r"term[_\s-]?([1-3])", part)
                if term_match:
                    term = int(term_match.group(1))
                    break
            # Fallback check on filename
            if term == 0:
                term_match = re.search(r"term[_\s-]?([1-3])", filename.lower())
                if term_match:
                    term = int(term_match.group(1))
                    
            # 5. Year (default to 2024, check filename and path)
            year = 2024
            year_match = re.search(r"\b(20\d{2})\b", filename)
            if year_match:
                year = int(year_match.group(1))
            else:
                for part in parts:
                    ym = re.search(r"\b(20\d{2})\b", part)
                    if ym:
                        year = int(ym.group(1))
                        break
                        
            # 6. Publisher (heuristic extraction)
            publisher = "Tamil Nadu Textbook and Educational Services Corporation"
            if "samacheer" in filename.lower() or "samacheer" in relative_path.lower():
                publisher = "Samacheer Kalvi"
            elif "cbse" in filename.lower() or "cbse" in relative_path.lower():
                publisher = "CBSE"
                
            # 7. Edition (heuristic extraction)
            edition = "2024 Edition"
            if year:
                edition = f"{year} Edition"
            if "reprint" in filename.lower():
                edition += " (Reprint)"
                
            return BookMetadata(
                class_level=class_level,
                subject=subject,
                medium=medium,
                language="ta" if medium == "tamil" else "en",
                content_type=content_type,
                term=term,
                year=year,
                publisher=publisher,
                edition=edition,
                filename=filename,
                relative_path=relative_path
            )
            
        # Filename matching fallback if folder structure does not contain class_X folder
        filename_lower = filename.lower()
        match = self.term_pattern.match(filename_lower) or self.fullyear_pattern.match(filename_lower) or self.prev_pattern.match(filename_lower)
        
        if match:
            gd = match.groupdict()
            medium = gd.get("medium", "english").lower()
            subject = gd.get("subject", "science").lower()
            term_val = int(gd.get("term", 0)) if "term" in gd else 0
            year_val = int(gd.get("year", 2024)) if "year" in gd else 2024
            
            raw_type = gd.get("type", "textbook").lower()
            content_type = "textbook"
            if "guide" in raw_type:
                content_type = "guide"
            elif "previous" in raw_type or "prev" in raw_type:
                content_type = "previous_year"
            elif "teacher" in raw_type:
                content_type = "teacher_notes"
                
            publisher = "Tamil Nadu Textbook and Educational Services Corporation"
            if "samacheer" in filename_lower:
                publisher = "Samacheer Kalvi"
                
            return BookMetadata(
                class_level=int(gd["class"]),
                subject=subject,
                medium=medium,
                language="ta" if medium == "tamil" else "en",
                content_type=content_type,
                term=term_val,
                year=year_val,
                publisher=publisher,
                edition=f"{year_val} Edition",
                filename=filename,
                relative_path=relative_path
            )
            
        return None
