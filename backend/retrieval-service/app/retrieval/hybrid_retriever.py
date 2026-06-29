# services/retrieval-service/app/retrieval/hybrid_retriever.py
import math
import numpy as np
import logging
from typing import List, Dict, Any, Tuple
from app.api.schemas import RetrieveRequest, ChunkResult
from sklearn.metrics.pairwise import cosine_similarity
from app.ingestion.hardware_detector import get_hardware_level
import os
import pickle
import anyio

logger = logging.getLogger("retrieval.hybrid_retriever")

class SimpleBM25:
    """
    In-memory BM25 index for sparse retrieval over text chunks.
    Allows sparse indexing without external database requirements.
    """
    def __init__(self, corpus: List[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = len(corpus)
        self.avg_doc_len = 0
        self.doc_lens = []
        self.doc_freqs = {}
        self.idf = {}
        self.doc_term_freqs = []

        if self.corpus_size == 0:
            return

        total_words = 0
        for doc in corpus:
            tokens = self._tokenize(doc)
            self.doc_lens.append(len(tokens))
            total_words += len(tokens)
            
            # Count terms in doc
            term_freq = {}
            for token in tokens:
                term_freq[token] = term_freq.get(token, 0) + 1
            self.doc_term_freqs.append(term_freq)
            
            # Update doc frequency
            for token in term_freq:
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1

        self.avg_doc_len = total_words / self.corpus_size

        # Compute IDF
        for term, freq in self.doc_freqs.items():
            # Standard BM25 IDF formula
            self.idf[term] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1.0)

    def _tokenize(self, text: str) -> List[str]:
        # Minimal bilingual tokenizer (splits on words, lowercases)
        return re.findall(r"\b\w+\b", text.lower())

    def get_scores(self, query: str) -> np.ndarray:
        scores = np.zeros(self.corpus_size)
        query_tokens = self._tokenize(query)
        
        for token in query_tokens:
            if token not in self.idf:
                continue
            idf_val = self.idf[token]
            for doc_idx in range(self.corpus_size):
                tf = self.doc_term_freqs[doc_idx].get(token, 0)
                doc_len = self.doc_lens[doc_idx]
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_len))
                scores[doc_idx] += idf_val * (numerator / denominator)
                
        return scores

# Import re for regex tokenization in BM25
import re

class HybridRetriever:
    def __init__(self, services_cache: dict):
        self.cache = services_cache
        self.device = "cuda" if get_hardware_level() == "LEVEL_2_GPU" else "cpu"
        
        # Load BM25 offline index from cache/disk
        self.bm25_indices = self.cache.get("bm25_indices")
        if not self.bm25_indices:
            data_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data"))
            bm25_path = os.path.join(data_root, "processed", "cache", "bm25_index.pkl")
            if os.path.exists(bm25_path):
                try:
                    logger.info(f"Loading offline BM25 index from {bm25_path}...")
                    with open(bm25_path, "rb") as f:
                        self.bm25_indices = pickle.load(f)
                    self.cache["bm25_indices"] = self.bm25_indices
                except Exception as e:
                    logger.error(f"Failed to load offline BM25 index: {e}")
            
            # Fallback if still not loaded (e.g. first run without offline generation completed)
            if not self.bm25_indices:
                logger.warning("BM25 offline index not found. Building on-the-fly...")
                en_chunks = self.cache.get("en_chunks", [])
                ta_chunks = self.cache.get("ta_chunks", [])
                self.bm25_indices = {
                    "en": SimpleBM25([c["text"] for c in en_chunks]) if en_chunks else SimpleBM25([]),
                    "ta": SimpleBM25([c["text"] for c in ta_chunks]) if ta_chunks else SimpleBM25([])
                }
                self.cache["bm25_indices"] = self.bm25_indices

    def filter_candidates(self, chunks: List[dict], req: RetrieveRequest, target_medium: str) -> List[Tuple[int, dict]]:
        """
        Pre-filtering stage: screens chunks by metadata (class, subject, term, medium)
        before running vector or keyword comparisons. Returns (original_index, chunk).
        """
        valid_indices = []
        for idx, chunk in enumerate(chunks):
            meta = chunk.get("metadata", {})
            
            # 1. Grade filter (optional)
            if req.class_id is not None and meta.get("class_level") != req.class_id:
                continue
            # 2. Subject filter (optional)
            if req.subject is not None and meta.get("subject") != req.subject:
                continue
            # 3. Medium (Language) filter
            if meta.get("medium") != target_medium:
                continue
            # 4. Term matching for class 6 and 7 (optional)
            if req.class_id is not None and req.term is not None:
                if req.class_id in [6, 7] and meta.get("term") != req.term:
                    continue
                # 5. Term 0 matching for class 8
                if req.class_id == 8 and meta.get("term") != 0:
                    continue
            # 6. Check if content type is allowed
            if meta.get("content_type", "textbook") not in req.allowed_content_types:
                continue

            valid_indices.append((idx, chunk))
            
        return valid_indices

    def reciprocal_rank_fusion(self, dense_results: List[str], sparse_results: List[str], k: int = 60) -> List[Tuple[str, float]]:
        """
        Reciprocal Rank Fusion (RRF) merges ranking indexes.
        """
        rrf_scores = {}
        
        # Dense ranking
        for rank, chunk_id in enumerate(dense_results):
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (1.0 / (k + rank + 1))
            
        # Sparse ranking
        for rank, chunk_id in enumerate(sparse_results):
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (1.0 / (k + rank + 1))
            
        # Sort chunks by RRF score descending
        sorted_rrf = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)
        return sorted_rrf

    async def retrieve(self, req: RetrieveRequest, query_vector: np.ndarray) -> List[ChunkResult]:
        """
        Asynchronously retrieves relevant document chunks using thread pool offloading for matrix math.
        """
        return await anyio.to_thread.run_sync(self._retrieve_sync, req, query_vector)

    def _retrieve_sync(self, req: RetrieveRequest, query_vector: np.ndarray) -> List[ChunkResult]:
        """
        Synchronous core retrieval logic containing CPU-heavy matrix operations.
        """
        preferred_medium = req.preferred_medium.lower()
        lang_key = "ta" if preferred_medium == "tamil" else "en"
        
        all_chunks = self.cache.get(f"{lang_key}_chunks", [])
        all_embeddings = self.cache.get(f"{lang_key}_embeddings")

        if not all_chunks or all_embeddings is None or len(all_chunks) == 0:
            return []

        # 1. Pre-filter by metadata
        filtered_pairs = self.filter_candidates(all_chunks, req, preferred_medium)
        if not filtered_pairs:
            return []

        filtered_indices = [p[0] for p in filtered_pairs]
        filtered_chunks = [p[1] for p in filtered_pairs]

        # 2. Dense Cosine Search (CPU-heavy NumPy calculations)
        filtered_embeddings = all_embeddings[filtered_indices]
        dense_similarities = cosine_similarity(query_vector.reshape(1, -1), filtered_embeddings)[0]
        
        dense_ranked_pairs = sorted(
            zip(filtered_chunks, dense_similarities), 
            key=lambda x: x[1], 
            reverse=True
        )
        dense_ranked_ids = [pair[0]["chunk_id"] for pair in dense_ranked_pairs]

        # 3. Sparse BM25 Search (using offline pre-loaded index, CPU-heavy)
        bm25_scores = self.bm25_indices[lang_key].get_scores(req.question)
        filtered_bm25_scores = [bm25_scores[idx] for idx in filtered_indices]
        
        sparse_ranked_pairs = sorted(
            zip(filtered_chunks, filtered_bm25_scores), 
            key=lambda x: x[1], 
            reverse=True
        )
        sparse_ranked_ids = [pair[0]["chunk_id"] for pair in sparse_ranked_pairs]

        # 4. RRF Score Fusion
        fused_rankings = self.reciprocal_rank_fusion(dense_ranked_ids, sparse_ranked_ids, k=60)

        # 5. Construct results mapped to original format
        chunk_map = {c["chunk_id"]: c for c in filtered_chunks}
        
        results = []
        for chunk_id, rrf_score in fused_rankings[:req.top_k * 2]:  # Keep double top_k for Reranker stage
            chunk = chunk_map[chunk_id]
            meta = chunk["metadata"]
            c_type = meta.get("content_type", "textbook")
            
            results.append(ChunkResult(
                chunk_id=chunk["chunk_id"],
                text=chunk["text"],
                score=float(rrf_score), # Store fused rank score
                source_filename=meta.get("filename", "unknown"),
                source_path=meta.get("relative_path", "unknown"),
                class_level=meta.get("class_level", req.class_id),
                term=meta.get("term", req.term),
                content_type=c_type,
                chapter_title=meta.get("chapter_title", "Unknown Chapter"),
                retrieval_tier=c_type,
                page_number=int(meta.get("page_number", 0)),
                section_no=str(meta.get("section_no", "unknown"))
            ))
            
        return results
