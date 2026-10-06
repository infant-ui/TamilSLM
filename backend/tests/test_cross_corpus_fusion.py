"""
Phase 2 regression test: a uniformly-stronger corpus must win the cross-corpus fusion.

This is exactly the test the Phase 2 brief asked for -- "constructs a case where one
corpus's candidates are uniformly stronger and asserts the fused ranking reflects
that" -- and it is the test that would have caught the old fixed-interleave failure
mode immediately (a positional interleave ignores relevance entirely, so it would
have put a Tamil result in the top slots regardless of how weak every Tamil
candidate's actual score was).
"""
import os
import sys

import numpy as np
import pytest

RETRIEVAL_SERVICE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "retrieval-service"))
sys.path.insert(0, RETRIEVAL_SERVICE_DIR)

from app.retrieval.hybrid_retriever import HybridRetriever, SimpleBM25  # noqa: E402
from app.api.schemas import RetrieveRequest  # noqa: E402


def _make_chunk(chunk_id, text, page_number, medium):
    return {
        "chunk_id": chunk_id,
        "text": text,
        "metadata": {
            "class_level": 6, "subject": "science", "medium": medium, "term": 1,
            "content_type": "textbook", "page_number": page_number, "filename": f"{chunk_id}.pdf",
            "relative_path": f"books/{chunk_id}.pdf", "chapter_title": "Unit 1",
        },
    }


def _build_cache(en_texts, ta_texts, en_vecs, ta_vecs):
    en_chunks = [_make_chunk(f"en_{i}", t, i + 1, "english") for i, t in enumerate(en_texts)]
    ta_chunks = [_make_chunk(f"ta_{i}", t, i + 1, "tamil") for i, t in enumerate(ta_texts)]
    cache = {
        "en_chunks": en_chunks, "en_embeddings": np.array(en_vecs, dtype=np.float32),
        "ta_chunks": ta_chunks, "ta_embeddings": np.array(ta_vecs, dtype=np.float32),
        "bm25_indices": {
            "en": SimpleBM25(en_texts),
            "ta": SimpleBM25(ta_texts),
        },
    }
    return cache


def test_uniformly_stronger_corpus_wins_fusion():
    # English corpus: 3 chunks whose text densely repeats the exact query term, AND
    # whose embeddings point in the same direction as the query vector (high cosine).
    # Tamil corpus: 3 chunks with unrelated text (zero BM25 overlap with the query) and
    # embeddings pointing in an unrelated/opposite direction (low or negative cosine).
    en_texts = [
        "photosynthesis photosynthesis photosynthesis occurs in the leaves of green plants",
        "photosynthesis is the process plants use photosynthesis to make food using sunlight",
        "chlorophyll absorbs light for photosynthesis in the chloroplast of the plant cell",
    ]
    ta_texts = [
        "ganita ennikkai ஒரு எண்களின் தொகுப்பு கணிதம் பற்றி ஒன்றும் இல்லை",
        "pakuththaari surutham vatta amaippu வடிவியல் பற்றிய ஒரு பாடம்",
        "ethirmarai sattam நியூட்டனின் விதிகள் பற்றிய விளக்கம்",
    ]
    query_vec = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
    en_vecs = [[0.95, 0.05, 0.0, 0.0], [0.9, 0.1, 0.0, 0.0], [0.92, 0.08, 0.0, 0.0]]
    ta_vecs = [[-0.9, 0.0, 0.1, 0.0], [-0.8, 0.0, 0.2, 0.0], [-0.85, 0.0, 0.15, 0.0]]

    cache = _build_cache(en_texts, ta_texts, en_vecs, ta_vecs)
    retriever = HybridRetriever(cache)

    req = RetrieveRequest(
        question="photosynthesis photosynthesis photosynthesis",
        detected_language="bilingual", class_id=6, subject="science", term=1,
        preferred_medium="english",  # irrelevant for the cross-corpus path, but required by the schema
        allowed_content_types=["textbook", "guide"], top_k=5,
    )

    results, diagnostics = retriever.retrieve_cross_corpus_sync(req, query_vec)

    assert len(results) > 0, "fusion returned no results at all"
    assert all(r.fusion_pool == "en_original" for r in results[:3]), (
        f"expected the uniformly-stronger English pool to occupy the top slots, got "
        f"fusion_pool values {[r.fusion_pool for r in results[:3]]}"
    )
    # The top result's combined score should clearly exceed every Tamil-pool candidate's.
    ta_scores = [r.score for r in results if r.fusion_pool != "en_original"]
    if ta_scores:
        assert results[0].score > max(ta_scores), (
            "top fused result should outscore every candidate from the weaker corpus"
        )


def test_fusion_changes_when_corpus_strength_flips():
    """
    Same shape as above, but with corpus strength reversed: asserts the merge is
    actually driven by score, not by some hidden positional bias toward one corpus
    (e.g. "English always first" would pass the first test by accident but fail this
    one, which is exactly the regression a fixed-interleave bug would exhibit).
    """
    en_texts = ["unrelated boring passage about rivers and mountains and geography topics"] * 3
    ta_texts = [
        "வெப்பநிலை வெப்பநிலை வெப்பநிலை ஒரு பொருளின் சூடு அல்லது குளிர்ச்சியை அளவிடும்",
        "வெப்பநிலை அளவிடுவதற்கு தெர்மாமீட்டர் எனப்படும் கருவி பயன்படுத்தப்படுகிறது வெப்பநிலை",
        "வெப்ப ஆற்றல் வெப்பநிலை மாற்றத்திற்கு காரணமாக அமைகிறது",
    ]
    query_vec = np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float32)
    en_vecs = [[0.1, -0.9, 0.0, 0.0], [0.0, -0.85, 0.1, 0.0], [0.05, -0.88, 0.0, 0.0]]
    ta_vecs = [[0.0, 0.95, 0.05, 0.0], [0.0, 0.9, 0.1, 0.0], [0.0, 0.92, 0.08, 0.0]]

    cache = _build_cache(en_texts, ta_texts, en_vecs, ta_vecs)
    retriever = HybridRetriever(cache)

    req = RetrieveRequest(
        question="வெப்பநிலை வெப்பநிலை வெப்பநிலை", detected_language="bilingual",
        class_id=6, subject="science", term=1, preferred_medium="tamil",
        allowed_content_types=["textbook", "guide"], top_k=5,
    )
    results, diagnostics = retriever.retrieve_cross_corpus_sync(req, query_vec)

    assert len(results) > 0
    assert all(r.fusion_pool == "ta_original" for r in results[:3]), (
        f"expected the now-uniformly-stronger Tamil pool to occupy the top slots, got "
        f"fusion_pool values {[r.fusion_pool for r in results[:3]]}"
    )


if __name__ == "__main__":
    import sys as _sys
    _sys.exit(pytest.main([__file__, "-v"]))
