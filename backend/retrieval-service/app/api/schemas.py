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
    # Phase 2: opt-in genuine cross-corpus fusion for bilingual/code-mixed queries,
    # replacing the previous behaviour of picking exactly one corpus via preferred_medium
    # (there was no fixed-interleave or other cross-corpus merge to "fix" here -- the
    # original audit found, and this phase re-confirmed, that no such logic existed
    # anywhere in this codebase; this is new capability, not a patch). Default False so
    # the existing single-corpus path (preferred_medium) is completely unchanged unless
    # a caller opts in.
    cross_corpus_fusion: bool = Field(False, description="Retrieve from BOTH corpora and "
                                       "fuse via normalized scores instead of picking one via preferred_medium")

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
    # Phase 2: raw per-signal scores, populated by the cross-corpus fusion path so the
    # normalization that combines them is inspectable/testable rather than opaque.
    # Both default to 0.0 for the existing single-corpus path, which doesn't set them.
    dense_score: float = Field(0.0, description="Raw cosine similarity (shared embedding space, "
                                "comparable across corpora without normalization)")
    bm25_score_raw: float = Field(0.0, description="Raw BM25 score before the saturating "
                                   "squash used to make it comparable across corpora")
    fusion_pool: Optional[str] = Field(None, description="Provenance tag for cross-corpus "
                                        "fusion: 'en_original', 'ta_original', or 'ta_transliterated'")

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
