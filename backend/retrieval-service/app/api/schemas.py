# services/retrieval-service/app/api/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class RetrieveRequest(BaseModel):
    question: str = Field(..., description="User's query")
    detected_language: str = Field("english", description="english or tamil")
    class_id: Optional[int] = Field(None, description="Grade (6, 7, 8)")
    subject: str = Field("auto", description="Topic filter (e.g. science, maths, auto)")
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
    # Expanded metadata fields for Citation Verification
    subject: str = Field("science", description="Subject of the book")
    language: str = Field("en", description="ta or en code")
    rank: int = Field(1, description="Rank in retrieval results")
    source: Optional[str] = Field("textbook", description="Source content category")
    publisher: Optional[str] = Field("Tamil Nadu Textbook and Educational Services Corporation", description="Publisher name")
    edition: Optional[str] = Field("Unknown Edition", description="Edition information")

class RetrieveResponse(BaseModel):
    query: str
    medium: str
    results: List[ChunkResult]
    fallback_applied: bool = False
    diagnostics: dict

class FeedbackRequest(BaseModel):
    session_id: str = Field(..., description="Active session ID")
    query: str = Field(..., description="User question")
    answer: str = Field(..., description="AI response text")
    rating: str = Field(..., description="'correct' or 'incorrect'")
    suggested_explanation: Optional[str] = Field(None, description="Teacher correction text")
    citation_errors: Optional[bool] = Field(False, description="Whether citations are incorrect")
    flagged_citations: Optional[List[str]] = Field(None, description="List of wrong chunk ids")
    improved_response: Optional[str] = Field(None, description="Optional custom revision")

class DashboardResponse(BaseModel):
    status: str
    retrieval_metrics: Dict[str, Any] = Field(..., description="Aggregate accuracy metrics")
    system_resources: Dict[str, Any] = Field(..., description="CPU, RAM, GPU usage stats")
    teacher_feedback: Dict[str, Any] = Field(..., description="Aggregate thumbs ratings stats")
