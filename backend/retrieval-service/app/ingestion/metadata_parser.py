# services/retrieval-service/app/ingestion/metadata_parser.py
import os
import re
from pydantic import BaseModel, Field
from typing import Optional

class BookMetadata(BaseModel):
    class_level: int = Field(..., description="Grade level of the book (6, 7, 8)")
    subject: str = Field("science", description="Subject name")
    medium: str = Field(..., description="tamil or english medium")
    language: str = Field(..., description="ta or en code")
    content_type: str = Field(..., description="textbook, guide, or previous_year")
    term: int = Field(0, description="1, 2, 3, or 0 for full year")
    year: int = Field(2024, description="Year of publication")
    filename: str = Field(..., description="Original filename")
    relative_path: str = Field(..., description="Relative file path from data root")

class MetadataParser:
    def __init__(self):
        # Filename regex patterns
        # 1. Term books: class6_science_term1_tamil_textbook.pdf
        self.term_pattern = re.compile(
            r"^class(?P<class>[6-8])_(?P<subject>[a-z]+)_term(?P<term>[1-3])_(?P<medium>tamil|english)_(?P<type>textbook|guide)\.pdf$",
            re.IGNORECASE
        )
        # 2. Full-year books: class8_science_fullyear_tamil_textbook.pdf
        self.fullyear_pattern = re.compile(
            r"^class(?P<class>[6-8])_(?P<subject>[a-z]+)_fullyear_(?P<medium>tamil|english)_(?P<type>textbook|guide)\.pdf$",
            re.IGNORECASE
        )
        # 3. Previous-year books: class8_science_2023_tamil_textbook.pdf
        self.prev_pattern = re.compile(
            r"^class(?P<class>[6-8])_(?P<subject>[a-z]+)_(?P<year>\d{4})_(?P<medium>tamil|english)_(?P<type>textbook|guide)\.pdf$",
            re.IGNORECASE
        )

    def parse_from_filename(self, filename: str, relative_path: str) -> Optional[BookMetadata]:
        # Try matching term pattern
        match = self.term_pattern.match(filename)
        if match:
            gd = match.groupdict()
            medium = gd["medium"].lower()
            return BookMetadata(
                class_level=int(gd["class"]),
                subject=gd["subject"].lower(),
                medium=medium,
                language="ta" if medium == "tamil" else "en",
                content_type=gd["type"].lower(),
                term=int(gd["term"]),
                year=2024,
                filename=filename,
                relative_path=relative_path
            )

        # Try matching full year pattern
        match = self.fullyear_pattern.match(filename)
        if match:
            gd = match.groupdict()
            medium = gd["medium"].lower()
            return BookMetadata(
                class_level=int(gd["class"]),
                subject=gd["subject"].lower(),
                medium=medium,
                language="ta" if medium == "tamil" else "en",
                content_type=gd["type"].lower(),
                term=0,
                year=2024,
                filename=filename,
                relative_path=relative_path
            )

        # Try matching previous year pattern
        match = self.prev_pattern.match(filename)
        if match:
            gd = match.groupdict()
            medium = gd["medium"].lower()
            return BookMetadata(
                class_level=int(gd["class"]),
                subject=gd["subject"].lower(),
                medium=medium,
                language="ta" if medium == "tamil" else "en",
                content_type="previous_year",
                term=0,
                year=int(gd["year"]),
                filename=filename,
                relative_path=relative_path
            )

        # Robust Path-based parsing fallback
        parts = relative_path.replace("\\", "/").split("/")
        if len(parts) >= 5:
            try:
                class_level = None
                for part in parts:
                    if part.lower().startswith("class_"):
                        class_level = int(part.split("_")[1])
                        break
                
                if class_level is not None:
                    term = 0
                    for part in parts:
                        if part.lower().startswith("term_"):
                            term = int(part.split("_")[1])
                            break
                    
                    medium = "english"
                    for part in parts:
                        if part.lower() in ["tamil", "english"]:
                            medium = part.lower()
                            break
                    
                    content_type = "textbook"
                    for part in parts:
                        if part.lower() in ["textbook", "guide", "previous_year", "previous-year"]:
                            content_type = part.lower()
                            break
                    
                    subject = "science"
                    for part in parts:
                        if part.lower() in ["science"]:
                            subject = part.lower()
                            break
                    
                    year = 2024
                    year_match = re.search(r"\b(20\d{2})\b", filename)
                    if year_match:
                        year = int(year_match.group(1))
                        
                    return BookMetadata(
                        class_level=class_level,
                        subject=subject,
                        medium=medium,
                        language="ta" if medium == "tamil" else "en",
                        content_type=content_type,
                        term=term,
                        year=year,
                        filename=filename,
                        relative_path=relative_path
                    )
            except Exception:
                pass

        return None
