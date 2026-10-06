# services/retrieval-service/app/retrieval/reranker.py
import logging
import math
from typing import List, Tuple
from app.api.schemas import ChunkResult
from sentence_transformers import CrossEncoder
from app.ingestion.hardware_detector import get_hardware_level
from scipy.stats import spearmanr

logger = logging.getLogger("retrieval.reranker")

class CrossEncoderReranker:
    def __init__(self, threshold: float = 0.35):
        self.threshold = threshold
        self.hw_level = get_hardware_level()
        self.device = "cuda" if self.hw_level == "LEVEL_2_GPU" else "cpu"
        self.model = None

        logger.info(f"Loading CrossEncoder Reranker on {self.device}...")
        try:
            # Load Alibaba GTE Multilingual Reranker
            self.model = CrossEncoder(
                "Alibaba-NLP/gte-multilingual-reranker-base", 
                device=self.device,
                trust_remote_code=True
            )
        except Exception as e:
            logger.warning(
                f"Failed to load cross-encoder model: {str(e)}. "
                f"Retrieval will run without reranker scoring."
            )

    def rerank(self, query: str, candidates: List[ChunkResult], top_k: int) -> List[ChunkResult]:
        """
        Reranks retrieved candidate chunks based on cross-attention matching.
        """
        if not candidates or self.model is None:
            return candidates[:top_k]

        # 1. Prepare inputs for CrossEncoder: list of (query, document) pairs
        pairs = []
        for c in candidates:
            # Inject structural path context if available to help the cross-encoder
            doc_context = f"Chapter: {c.chapter_title} | Section: {c.source_filename}\n{c.text}"
            pairs.append((query, doc_context))

        try:
            # Predict similarity scores
            scores = self.model.predict(pairs)
            
            # Update scores on candidates
            for idx, score in enumerate(scores):
                candidates[idx].score = float(score)

            # 2. Sort by rerank score descending
            reranked = sorted(candidates, key=lambda x: x.score, reverse=True)

            # 3. Apply Threshold filtering
            # Discard blocks that have a score below the matching threshold (0.35)
            filtered = [c for c in reranked if c.score >= self.threshold]

            logger.info(
                f"Reranking completed. Output count: {len(filtered)} "
                f"(Discarded {len(reranked) - len(filtered)} below threshold {self.threshold})"
            )

            return filtered[:top_k]

        except Exception as e:
            logger.error(f"Error during cross-encoder reranking: {str(e)}")
            # Fail gracefully: return original RRF ranked results truncated to top_k
            return candidates[:top_k]

    def rerank_with_trust(self, query: str, candidates: List[ChunkResult], top_k: int,
                           min_trust_for_threshold: float = 0.3) -> Tuple[List[ChunkResult], dict]:
        """
        Phase 2: replaces the always-fully-trust-the-reranker behavior of rerank() with a
        continuous, per-query trust score, rather than the blunt on/off bypass described
        in the Phase 2 brief. That bypass ("if Tamil-dominant, skip the reranker entirely")
        does NOT exist anywhere in this codebase -- confirmed in the original audit and
        re-confirmed before writing this -- so this is new logic, not a patch.

        Trust = max(0, Spearman rank-correlation) between the PRE-rerank order (the fused
        order candidates arrive in) and the reranker's own proposed order, computed fresh
        for every call:
          - High trust (reranker makes small, plausible adjustments to the fused order):
            behaves like rerank() -- use the reranked order, apply the usual confidence
            threshold.
          - Low/negative trust (reranker reshuffles wildly relative to the fused signal --
            the historical failure pattern was a short, keyword-dense chunk jumping to
            rank 1): down-weight the reranker's influence on the final order via a blend,
            and stop applying its absolute-score threshold too (a reranker whose ordering
            isn't trustworthy for this query has no reason to have a trustworthy
            confidence calibration either).

        This is also a diagnostic: a low trust score on a query whose PRE-rerank ranking
        was already poor tells you the reranker isn't making things worse (it's deferring
        to the upstream signal) -- the problem is upstream in retrieval/fusion, not here.

        Returns (results, diagnostics); diagnostics includes "trust" for exactly that use.
        """
        if not candidates or self.model is None:
            return candidates[:top_k], {"trust": None, "reason": "no_candidates_or_no_model"}

        # Capture the pre-rerank order/scores BEFORE anything below mutates candidates'
        # .score in place (as rerank() does) -- otherwise the "pre" signal is unrecoverable.
        original_order = list(candidates)
        original_scores = [c.score for c in candidates]
        original_ids = [c.chunk_id for c in original_order]
        pre_rank_of_id = {cid: i for i, cid in enumerate(original_ids)}

        pairs = [(query, f"Chapter: {c.chapter_title} | Section: {c.source_filename}\n{c.text}") for c in candidates]
        try:
            scores = self.model.predict(pairs)
        except Exception as e:
            logger.error(f"Error during cross-encoder reranking: {e}")
            return candidates[:top_k], {"trust": None, "reason": f"predict_failed: {e}"}

        rerank_score_of_id = {cid: float(s) for cid, s in zip(original_ids, scores)}
        for c in candidates:
            c.score = rerank_score_of_id[c.chunk_id]
        post_order = sorted(candidates, key=lambda x: x.score, reverse=True)
        post_ids = [c.chunk_id for c in post_order]

        if len(post_ids) >= 3:
            pre_ranks_in_post_order = [pre_rank_of_id[cid] for cid in post_ids]
            post_ranks = list(range(len(post_ids)))
            corr, _ = spearmanr(pre_ranks_in_post_order, post_ranks)
            corr = 0.0 if corr is None or math.isnan(corr) else float(corr)
        else:
            corr = 1.0  # too few candidates for a meaningful correlation -- default to trusting rerank

        trust = max(0.0, corr)

        def _minmax(vals):
            """Per-call min-max over THIS candidate set only -- valid here (unlike the
            cross-corpus fusion path) because both signals being compared are for the
            exact same query and the exact same candidate pool, not different corpora."""
            lo, hi = min(vals), max(vals)
            if hi - lo < 1e-9:
                return [0.5] * len(vals)  # all-equal scores: no signal to normalize, treat as tied
            return [(v - lo) / (hi - lo) for v in vals]

        fused_norm = dict(zip(original_ids, _minmax(original_scores)))
        rerank_norm = dict(zip(original_ids, _minmax([rerank_score_of_id[cid] for cid in original_ids])))

        blended_score_of_id = {cid: trust * rerank_norm[cid] + (1 - trust) * fused_norm[cid] for cid in original_ids}
        for c in candidates:
            c.score = blended_score_of_id[c.chunk_id]
        final_order = sorted(candidates, key=lambda x: x.score, reverse=True)

        threshold_applied = trust >= min_trust_for_threshold
        if threshold_applied:
            filtered = [c for c in final_order if rerank_score_of_id[c.chunk_id] >= self.threshold]
        else:
            # Low trust: don't apply the reranker's own confidence threshold either --
            # fall back to the (already upstream-filtered) fused candidate set.
            filtered = final_order

        diagnostics = {
            "trust": trust, "spearman_raw": corr, "n_candidates": len(candidates),
            "threshold_applied": threshold_applied,
            "n_discarded_by_threshold": (len(final_order) - len(filtered)) if threshold_applied else 0,
        }
        return filtered[:top_k], diagnostics
