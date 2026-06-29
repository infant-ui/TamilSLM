# services/retrieval-service/app/retrieval/reranker.py
import logging
from typing import List
from app.api.schemas import ChunkResult
from sentence_transformers import CrossEncoder
from app.ingestion.hardware_detector import get_hardware_level

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
