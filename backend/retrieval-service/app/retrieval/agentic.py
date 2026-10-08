# services/retrieval-service/app/retrieval/agentic.py
#
# Phase 4, steps 1-2: query decomposition and confidence-gated iterative retrieval.
# Deliberately NO LLM calls in this module -- both signals are derived from data the
# hybrid retriever already computes (ranked id lists) or from cheap string heuristics,
# so a single-hop, high-confidence query (the common case) pays zero extra latency
# beyond one more dict lookup and one regex scan.
import re
from typing import List, Optional

# English and Tamil coordinating conjunctions that plausibly join two separate
# question clauses. Intentionally short and specific (not a general conjunction list)
# to keep false positives down -- "salt and pepper" inside a single clause should NOT
# trigger decomposition, which is why this is combined with a per-clause length check
# in detect_compound_question rather than used alone.
_CONJUNCTION_SPLIT_RE = re.compile(
    r"\s+(?:and also|as well as|and|மற்றும்|அதோடு|அதே போல)\s+", re.IGNORECASE
)
_ENUMERATION_RE = re.compile(r"(?:^|\s)(\d+)[.)]\s")
MIN_SUBQUESTION_CHARS = 12  # below this, a conjunction split is probably joining nouns/adjectives, not clauses
_CONTEXT_HEADER_RE = re.compile(r"^\[Context:\s*(.*?)\]")


def extract_context_header(chunk_text: str) -> Optional[str]:
    """Pulls the "[Context: X]" heading ingestion already stamps on every chunk
    (see the 'General' placeholder seen throughout this corpus), if present."""
    if not chunk_text:
        return None
    m = _CONTEXT_HEADER_RE.match(chunk_text.strip())
    return m.group(1).strip() if m else None


def detect_compound_question(question: str) -> Optional[List[str]]:
    """Returns a list of 2+ sub-questions if `question` looks compound/multi-part,
    else None (meaning: treat as single-hop, skip decomposition entirely).

    Three cheap signals, checked in order of how unambiguous they are:
      1. More than one '?' -- the strongest signal, nearly unambiguous.
      2. Explicit enumeration ("1. ... 2. ...") -- unambiguous when present.
      3. A splitting conjunction, ONLY if both resulting halves are long enough to be
         plausible independent clauses (filters out "photosynthesis and respiration").
    None of these call a model: this is a pure string heuristic, by design (see module
    docstring and the Phase 4 instruction not to add latency to the single-hop common case).
    """
    q = question.strip()
    if not q:
        return None

    if q.count("?") >= 2:
        parts = [p.strip() + "?" for p in q.split("?") if p.strip()]
        if len(parts) >= 2:
            return parts

    enum_matches = list(_ENUMERATION_RE.finditer(q))
    if len(enum_matches) >= 2:
        bounds = [m.start() for m in enum_matches] + [len(q)]
        parts = [q[bounds[i]:bounds[i + 1]].strip() for i in range(len(bounds) - 1)]
        parts = [p for p in parts if len(p) >= MIN_SUBQUESTION_CHARS]
        if len(parts) >= 2:
            return parts

    split = _CONJUNCTION_SPLIT_RE.split(q, maxsplit=1)
    if len(split) == 2:
        left, right = split[0].strip(), split[1].strip()
        if len(left) >= MIN_SUBQUESTION_CHARS and len(right) >= MIN_SUBQUESTION_CHARS:
            return [left, right]

    return None


def retrieval_confidence(dense_ranked_ids: List[str], sparse_ranked_ids: List[str], top_n: int = 5) -> float:
    """Jaccard overlap of the top-N dense-only and BM25-only id sets from the SAME
    candidate pool already computed by _execute_retrieve_for_medium -- no extra
    retrieval call, just reusing numbers that exist either way.

    Rationale: when dense and sparse genuinely agree on what's relevant, fusion is
    probably trustworthy. When they disagree a lot (low overlap), the fused top-k is
    more likely to be an artifact of the RRF formula than a real consensus -- that's
    the case worth spending one extra retrieval round on. This is a relative,
    per-query signal, not a language-based one (the Tamil RRF reweight already showed
    that gating on language instead of the actual per-query signal would fire needless
    extra rounds for every Tamil query just because that bucket is noisier on average).
    """
    if not dense_ranked_ids or not sparse_ranked_ids:
        return 0.0
    d = set(dense_ranked_ids[:top_n])
    s = set(sparse_ranked_ids[:top_n])
    union = d | s
    if not union:
        return 0.0
    return len(d & s) / len(union)


def expand_query_cheap(original_question: str, top_chunk_context_header: Optional[str]) -> str:
    """One extra retrieval round's "query rewrite/expansion" -- deliberately NOT an LLM
    call (see module docstring): on this CPU-only hardware an LLM rewrite would cost
    roughly as much as the entire rest of the retrieval pass, for a gate that should
    fire occasionally, not routinely. Instead, append the first-pass top hit's own
    "[Context: <section>]" heading (already stored on every chunk at ingestion time) to
    the original query -- a free, real signal about which sub-topic the corpus itself
    associates with the closest match, used to broaden the second BM25/dense pass.
    Falls back to the unmodified question if no header is available (e.g. the hit was a
    "[Context: General]" placeholder, which carries no extra information).
    """
    if not top_chunk_context_header or top_chunk_context_header.strip().lower() in ("general", ""):
        return original_question
    return f"{original_question} {top_chunk_context_header}".strip()
