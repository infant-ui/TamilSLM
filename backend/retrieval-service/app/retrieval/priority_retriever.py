# services/retrieval-service/app/retrieval/priority_retriever.py
import numpy as np
from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity
from app.api.schemas import RetrieveRequest, ChunkResult

class PriorityRetriever:
    def __init__(self, services_cache: dict):
        self.cache = services_cache

    def filter_and_rank(self, query_vector: np.ndarray, chunks: List[dict], embeddings: np.ndarray, 
                        req: RetrieveRequest, target_medium: str) -> List[dict]:
        # Filter chunks by class, subject, term, and medium
        valid_indices = []
        for idx, chunk in enumerate(chunks):
            meta = chunk.get("metadata", {})
            
            # Basic Hard Filters
            if meta.get("class_level") != req.class_id:
                continue
            if meta.get("subject") != req.subject:
                continue
            if meta.get("medium") != target_medium:
                continue
            
            # Enforce Term matching (only for Class 6 and 7)
            if req.class_id in [6, 7] and meta.get("term") != req.term:
                continue
            # Class 8 enforces term = 0 (full year)
            if req.class_id == 8 and meta.get("term") != 0:
                continue

            valid_indices.append(idx)

        if not valid_indices:
            return []

        # Slice relevant embeddings and calculate similarity
        filtered_embeddings = embeddings[valid_indices]
        similarities = cosine_similarity(query_vector, filtered_embeddings)[0]

        ranked_results = []
        for i, val_idx in enumerate(valid_indices):
            chunk = chunks[val_idx]
            ranked_results.append({
                "chunk": chunk,
                "score": float(similarities[i])
            })
        
        # Sort by similarity score descending
        ranked_results.sort(key=lambda x: x["score"], reverse=True)
        return ranked_results

    def retrieve_by_priority(self, req: RetrieveRequest, query_vector: np.ndarray) -> tuple[List[ChunkResult], bool]:
        """
        Returns a tuple of (results, fallback_applied)
        """
        preferred_medium = req.preferred_medium.lower()
        lang_key = "ta" if preferred_medium == "tamil" else "en"
        all_chunks = self.cache.get(f"{lang_key}_chunks", [])
        all_embeddings = self.cache.get(f"{lang_key}_embeddings")

        fallback_applied = False
        final_results = []

        if all_chunks and all_embeddings is not None and len(all_chunks) > 0:
            final_results = self._retrieve_for_medium(req, query_vector, all_chunks, all_embeddings, preferred_medium)

        # Fallback language check if allowed and preferred medium has no results
        if not final_results and req.fallback_language_allowed:
            fallback_medium = "english" if preferred_medium == "tamil" else "tamil"
            fallback_lang_key = "ta" if fallback_medium == "tamil" else "en"
            
            fallback_chunks = self.cache.get(f"{fallback_lang_key}_chunks", [])
            fallback_embeddings = self.cache.get(f"{fallback_lang_key}_embeddings")
            
            if fallback_chunks and fallback_embeddings is not None and len(fallback_chunks) > 0:
                print(f"🔄 Applying language fallback from {preferred_medium} to {fallback_medium}...")
                fallback_applied = True
                
                # Compute query vector for the fallback language
                if fallback_medium == "english":
                    model = self.cache.get("en_model")
                    if model:
                        fallback_query_vector = model.encode([req.question])
                    else:
                        fallback_query_vector = query_vector
                else: # tamil
                    model = self.cache.get("ta_model")
                    if model:
                        fallback_query_vector = model.encode(["query: " + req.question], normalize_embeddings=True)
                    else:
                        fallback_query_vector = query_vector

                final_results = self._retrieve_for_medium(req, fallback_query_vector, fallback_chunks, fallback_embeddings, fallback_medium)

        return final_results, fallback_applied

    def _retrieve_for_medium(self, req: RetrieveRequest, query_vector: np.ndarray, 
                             chunks: List[dict], embeddings: np.ndarray, medium: str) -> List[ChunkResult]:
        # Get filtered and ranked candidates
        candidates = self.filter_and_rank(query_vector, chunks, embeddings, req, medium)
        
        # Separate candidates into structural tiers
        textbooks = []
        guides = []
        prev_years = []

        for item in candidates:
            chunk = item["chunk"]
            score = item["score"]
            meta = chunk["metadata"]
            c_type = meta.get("content_type", "textbook")

            result = ChunkResult(
                chunk_id=chunk["chunk_id"],
                text=chunk["text"],
                score=score,
                source_filename=meta["filename"],
                source_path=meta["relative_path"],
                class_level=meta["class_level"],
                term=meta["term"],
                content_type=c_type,
                chapter_title=meta.get("chapter_title", "Unknown Chapter"),
                retrieval_tier=c_type,
                page_number=int(meta.get("page_number", 0)),
                section_no=str(meta.get("section_no", "unknown"))
            )

            if c_type == "textbook":
                textbooks.append(result)
            elif c_type == "guide":
                guides.append(result)
            elif c_type == "previous_year" or meta.get("content_type") == "previous_year":
                prev_years.append(result)

        # Merge results based on priority requirements
        merged_results = []
        
        # Priority Tier 1: Current Textbook
        if "textbook" in req.allowed_content_types:
            merged_results.extend(textbooks)
        
        # Priority Tier 2: Current Guide
        if "guide" in req.allowed_content_types and len(merged_results) < req.top_k:
            merged_results.extend(guides)

        # Priority Tier 3: Previous Year Materials (if requested)
        if req.include_previous_years and len(merged_results) < req.top_k:
            merged_results.extend(prev_years)

        # Truncate to top_k limit
        return merged_results[:req.top_k]
