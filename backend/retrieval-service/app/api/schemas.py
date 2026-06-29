# services/retrieval-service/app/api/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

class RetrieveRequest(BaseModel):
    question: str = Field(..., description="User's science query")
    detected_language: str = Field("english", description="english or tamil")
    class_id: Optional[int] = Field(None, description="Grade (6, 7, 8)")
    subject: str = Field("science", description="Topic filter")
    term: Optional[int] = Field(None, description="1, 2, 3, or 0 (Class 8 full-year)")
    preferred_medium: str = Field(..., description="english or tamil")
    allowed_content_types: List[str] = Field(["textbook", "guide"], description="Tiers allowed to search")
    include_previous_years: bool = Field(False, description="Search previous year materials")
    fallback_language_allowed: bool = Field(False, description="Fallback if target medium lacks hits")
    top_k: int = Field(3, description="Chunks count to return")

class ChunkResult(BaseModel):
    chunk_id: str
    text: str
    score: float
    source_filename: str
    source_path: str
    class_level: int
    term: int
    content_type: str
    chapter_title: str
    retrieval_tier: str = Field(..., description="textbook, guide, or previous_year")
    page_number: int
    section_no: str

class RetrieveResponse(BaseModel):
    query: str
    medium: str
    results: List[ChunkResult]
    fallback_applied: bool = False
    diagnostics: dict
