# evaluation/scripts/evaluate_retrieval_full.py
"""
Full hybrid retrieval evaluation: Dense (GTE-multilingual-base embeddings) +
BM25 + Reciprocal Rank Fusion + CrossEncoder reranking (Alibaba-NLP/gte-
multilingual-reranker-base), run against the REAL production modules and the
REAL cached indices -- not a reimplementation.

WHY THIS CANNOT RUN IN A GENERIC SANDBOX:
It imports backend/retrieval-service/app/* directly, which pulls in
sentence-transformers/torch/scikit-learn/pydantic/fastapi, and it downloads
(or loads from your local Hugging Face cache) two real models. Run this with
your project's own interpreter -- the same one start.bat uses:

    From the repo root:
        .\\.venv\\Scripts\\python.exe evaluation\\scripts\\evaluate_retrieval_full.py
    (macOS/Linux dev machines: .venv/bin/python evaluation/scripts/evaluate_retrieval_full.py)

A NOTE ON A BUG THIS SCRIPT DELIBERATELY WORKS AROUND, WITHOUT MODIFYING IT:
app/evaluation/evaluator.py calls `self.retriever.retrieve(req, query_vector)`
where HybridRetriever.retrieve is `async def` (it internally wraps the real
work in anyio.to_thread.run_sync). Called without `await` and outside an
event loop, that line produces an unexecuted coroutine object, not a result --
passing it into the reranker as `candidates` would throw. This script avoids
the whole question by calling the private, synchronous `_retrieve_sync`
directly (the exact method that async wrapper delegates to), which is exactly
what happens by the time your live server processes a request, so behaviour
is faithful to production; only the concurrency wrapper is bypassed. We do
NOT edit hybrid_retriever.py or evaluator.py -- see final report for the
recommended fix.

Writes: evaluation/results/retrieval_full_results.json
"""
import json
import os
import sys
import time

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RETRIEVAL_SERVICE_DIR = os.path.join(REPO_ROOT, "backend", "retrieval-service")
sys.path.insert(0, RETRIEVAL_SERVICE_DIR)
sys.path.insert(0, os.path.dirname(__file__))

from metrics import (  # noqa: E402
    calculate_recall_at_k, calculate_precision_at_k, calculate_mrr, calculate_ndcg_at_k,
)

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "datasets", "gold_dataset.json")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")


def build_query_encoder():
    """Loads the REAL production embedding model via the shared encoder_utils loader
    (Phase 1: position_ids patch + rotary buffers zeroed), so eval results reflect
    exactly what's deployed -- and never drift from it, since main.py/index_books.py
    import this same function instead of each carrying their own copy of the patch."""
    from app.ingestion.hardware_detector import get_hardware_level
    from app.ingestion.encoder_utils import load_patched_encoder

    device = "cuda" if get_hardware_level() == "LEVEL_2_GPU" else "cpu"
    print(f"Loading Alibaba-NLP/gte-multilingual-base on {device} ...")
    return load_patched_encoder(device)


def build_services_cache():
    import pickle
    import numpy as np
    cache_dir = os.path.join(REPO_ROOT, "data", "processed", "cache")
    services_cache = {}
    for lang_key, chunks_fname, emb_fname in [
        ("en", "english_chunks.pkl", "english_embeddings.npy"),
        ("ta", "tamil_chunks.pkl", "tamil_embeddings.npy"),
    ]:
        with open(os.path.join(cache_dir, chunks_fname), "rb") as f:
            services_cache[f"{lang_key}_chunks"] = pickle.load(f)
        services_cache[f"{lang_key}_embeddings"] = np.load(os.path.join(cache_dir, emb_fname))
    return services_cache


def main():
    from app.retrieval.hybrid_retriever import HybridRetriever
    from app.retrieval.reranker import CrossEncoderReranker
    from app.api.schemas import RetrieveRequest

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    services_cache = build_services_cache()
    query_encoder = build_query_encoder()
    retriever = HybridRetriever(services_cache)

    print("Loading CrossEncoder reranker (Alibaba-NLP/gte-multilingual-reranker-base) ...")
    reranker = CrossEncoderReranker()
    # NOTE: app/retrieval/reranker.py (production) never applies the same
    # position_ids patch that main.py applies to the embedding model. The
    # underlying gte-multilingual-reranker-base model ships with a corrupted
    # position_ids buffer and raises IndexError on any real predict() call.
    # In production this is silently swallowed by CrossEncoderReranker.rerank()'s
    # try/except, which falls back to returning unreranked candidates -- i.e.
    # reranking is likely a silent no-op today. We patch it here, the same way
    # build_query_encoder() does for the embedder above, so this script can
    # measure what reranking *would* do if that patch were applied to
    # reranker.py. We do NOT edit reranker.py itself -- see final report.
    if reranker.model is not None:
        try:
            import torch
            pos_ids_buf = reranker.model.model.new.embeddings.position_ids
            dev = pos_ids_buf.device
            pos_ids_buf.copy_(torch.arange(pos_ids_buf.size(0), dtype=torch.long, device=dev))
            print("🔧 Patched CrossEncoder reranker position_ids (workaround for missing patch in reranker.py).")
        except Exception as e:
            print(f"Warning: reranker position_ids patch failed (non-fatal): {e}")
    # Sanity-check the raw score range the reranker actually produces on real
    # data, since the production threshold (0.35) assumes it's a calibrated
    # [0,1] probability -- this is exactly the assumption flagged in the
    # final report as unverified from static reading alone.
    if reranker.model is not None:
        try:
            probe_scores = reranker.model.predict([("What is motion?", "Motion is a change in position.")])
            print(f"[diagnostic] Raw CrossEncoder.predict() output on a trivial matching pair: {probe_scores} "
                  f"-- compare against the hardcoded 0.35 threshold in reranker.py")
        except Exception as e:
            print(f"[diagnostic] Raw CrossEncoder.predict() crashed even after the position_ids patch: {e!r} "
                  f"-- this means reranker.rerank()'s own try/except (reranker.py) is the only thing standing "
                  f"between this bug and a hard failure; in production reranking is silently a no-op. "
                  f"Continuing so per-item retrieval/rerank-fallback metrics can still be collected.")

    per_item = []
    for item in dataset["core"]:
        lang = item["lang"]
        corpora_to_try = {"english": ["english"], "tamil": ["tamil"],
                           "bilingual": ["english", "tamil"], "tanglish": ["english", "tamil"]}[lang]
        query_vector = query_encoder.encode([item["q"]], normalize_embeddings=True)[0]

        row = {"id": item["id"], "lang": lang, "unit": item["unit"], "expected_pages": item["pages"]}
        for medium in corpora_to_try:
            req = RetrieveRequest(
                question=item["q"], detected_language=lang, class_id=item["class_"],
                subject="auto", term=item["term"], preferred_medium=medium,
                allowed_content_types=["textbook", "guide"], top_k=10,
            )
            t0 = time.time()
            candidates, _fallback = retriever._retrieve_sync(req, query_vector)  # see module docstring
            pre_rerank_latency = (time.time() - t0) * 1000

            t1 = time.time()
            reranked = reranker.rerank(item["q"], candidates, top_k=10)
            rerank_latency = (time.time() - t1) * 1000

            def pages_of(chunk_results):
                return [c.page_number for c in chunk_results if c.page_number]

            pre_pages = pages_of(candidates)
            post_pages = pages_of(reranked)
            expected = item["pages"]

            def metrics_for(pages):
                return {
                    "recall_1": calculate_recall_at_k(pages, expected, 1),
                    "recall_3": calculate_recall_at_k(pages, expected, 3),
                    "recall_5": calculate_recall_at_k(pages, expected, 5),
                    "recall_10": calculate_recall_at_k(pages, expected, 10),
                    "precision_5": calculate_precision_at_k(pages, expected, 5),
                    "mrr": calculate_mrr(pages, expected),
                    "ndcg_5": calculate_ndcg_at_k(pages, expected, 5),
                }

            key = "english" if medium == "english" else "tamil"
            row[f"against_{key}_corpus"] = {
                "before_rerank": metrics_for(pre_pages),
                "after_rerank": metrics_for(post_pages),
                "pre_rerank_latency_ms": pre_rerank_latency,
                "rerank_latency_ms": rerank_latency,
                "n_candidates_before_rerank": len(candidates),
                "n_candidates_after_rerank": len(reranked),
                "top10_pages_after_rerank": post_pages[:10],
            }
        per_item.append(row)
        print(f"  done: {item['id']}")

    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(RESULTS_DIR, "retrieval_full_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"n_questions": len(per_item), "per_item": per_item}, f, ensure_ascii=False, indent=2)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
