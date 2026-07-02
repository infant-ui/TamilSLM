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

    def detect_subjects(self, question: str, available_subjects: List[str]) -> List[str]:
        """
        Vocabulary-based keyword matching to detect if the query is Science, Mathematics, or both.
        """
        math_indicators = [
            # English
            r"\bsolve\b", r"\bevaluate\b", r"\bsimplify\b", r"\bratio\b", r"\bpercentage\b", r"\bfraction\b",
            r"\bequation\b", r"\balgebra\b", r"\bgeometry\b", r"\btriangle\b", r"\bcircle\b", r"\brectangle\b",
            r"\bsquare\b", r"\bperimeter\b", r"\barea\b", r"\bvolume\b", r"\bmean\b", r"\bmedian\b", r"\bmode\b",
            r"\bprobability\b", r"\bderivative\b", r"\bintegral\b", r"\bmatrix\b", r"\bdeterminant\b", r"\bvector\b",
            r"\bnumber\b", r"\binteger\b", r"\bprime\b", r"\bcomposite\b", r"\bfactor\b", r"\bmultiple\b",
            r"\blcm\b", r"\bhcf\b", r"\bgcd\b", r"\broot\b", r"\bpower\b", r"\bexponent\b", r"\btheorem\b",
            r"\bcoordinate\b", r"\bgraph\b", r"\baxis\b", r"\bangle\b", r"\bdegree\b", r"\bradius\b", r"\bdiameter\b",
            r"\btrigonometry\b", r"\bsine\b", r"\bcosine\b", r"\btangent\b", r"\bformula\b", r"\bmath\b", r"\bmaths\b",
            r"\bmathematics\b", r"\baddition\b", r"\bsubtraction\b", r"\bmultiplication\b", r"\bdivision\b", r"\bsum\b",
            # Tamil
            r"மதிப்பு\s*காண்க", r"தீர்வு", r"சுருக்குக", r"விகிதம்", r"விழுக்காடு", r"சதவீதம்", r"பின்னம்",
            r"சமன்பாடு", r"இயற்கணிதம்", r"வடிவியல்", r"முக்கோணம்", r"வட்டம்", r"செவ்வகம்", r"சதுரம்",
            r"சுற்றளவு", r"பரப்பளவு", r"கனஅளவு", r"சராசரி", r"நிகழ்தகவு", r"காரணி", r"பெருக்கல்",
            r"மீ\.பொ\.வ", r"மீ\.பொ\.க", r"மீ\.சி\.ம", r"கோணம்", r"ஆரம்", r"விட்டம்", r"சுற்றளவு",
            r"வரைபடம்", r"கூட்டல்", r"கழித்தல்", r"பெருக்கல்", r"வகுத்தல்", r"எண்", r"எண்கள்",
            # Patterns
            r"\d+[\+\-\*\/÷\=\<\>\%\^\√]\d+", r"[x-z]\s*[\+\-\*\/÷\=\<\>\%\^\√]", r"[\+\-\*\/÷\=\<\>\%\^\√]\s*[x-z]",
            r"\b\d+\s*x\b", r"\bx\s*[\+\-]\s*y\b"
        ]
        
        science_indicators = [
            # English
            r"\bcell\b", r"\borgan\b", r"\btissue\b", r"\bplant\b", r"\banimal\b", r"\bspecies\b", r"\bforce\b",
            r"\bgravity\b", r"\benergy\b", r"\blight\b", r"\bsound\b", r"\bheat\b", r"\btemperature\b", r"\batom\b",
            r"\bmolecule\b", r"\belement\b", r"\bcompound\b", r"\breaction\b", r"\bacid\b", r"\bbase\b", r"\bsalt\b",
            r"\bmetal\b", r"\bfriction\b", r"\bvelocity\b", r"\bacceleration\b", r"\bmass\b", r"\bweight\b",
            r"\bdensity\b", r"\bpressure\b", r"\belectricity\b", r"\bmagnet\b", r"\bcircuit\b", r"\blens\b",
            r"\bmirror\b", r"\breflection\b", r"\brefraction\b", r"\bspectrum\b", r"\bfossil\b", r"\bcoal\b",
            r"\bpetroleum\b", r"\bpollution\b", r"\benvironment\b", r"\becosystem\b", r"\bbiodiversity\b",
            r"\bphotosynthesis\b", r"\brespiration\b", r"\bdigestion\b", r"\bcirculation\b", r"\bnervous\b",
            r"\bdisease\b", r"\bvirus\b", r"\bbacteria\b", r"\bfungi\b", r"\bnutrient\b", r"\bvitamin\b",
            r"\bmineral\b", r"\bhormone\b", r"\bgene\b", r"\bchromosome\b", r"\bdna\b", r"\brna\b", r"\bscience\b",
            r"\bphysics\b", r"\bchemistry\b", r"\bbiology\b",
            # Tamil
            r"செல்", r"திசு", r"உறுப்பு", r"தாவரம்", r"விலங்கு", r"விசை", r"ஈர்ப்பு", r"ஆற்றல்", r"ஒளி",
            r"ஒலி", r"வெப்பம்", r"வெப்பநிலை", r"அணு", r"மூலக்கூறு", r"தனிமம்", r"சேர்மம்", r"வினை",
            r"அமிலம்", r"காரம்", r"உப்பு", r"உலோகம்", r"அலோகம்", r"உராய்வு", r"திசைவேகம்", r"முடுக்கம்",
            r"நிறை", r"எடை", r"அடர்த்தி", r"அழுத்தம்", r"மின்சாரம்", r"காந்தம்", r"மின்சுற்று", r"ஆடி",
            r"பிரதிபலிப்பு", r"விலகல்", r"நிறமாலை", r"மட்கும்", r"சுற்றுச்சூழல்", r"சுவாசம்", r"செரிமானம்",
            r"இரத்த ஓட்டம்", r"நரம்பு", r"நோய்", r"வைரஸ்", r"பாக்டீரியா", r"ஊட்டச்சத்து", r"வைட்டமின்",
            r"அறிவியல்", r"இயற்பியல்", r"வேதியியல்", r"உயிரியல்"
        ]
        
        q_lower = question.lower()
        is_math = any(re.search(pat, q_lower) for pat in math_indicators)
        is_science = any(re.search(pat, q_lower) for pat in science_indicators)
        
        detected = []
        if is_math:
            # support both math and maths spellings
            detected.extend(["math", "maths", "mathematics"])
        if is_science:
            detected.append("science")
            
        if not detected:
            # Fallback to search all available subjects dynamically
            return available_subjects
            
        return detected

    def filter_candidates(self, chunks: List[dict], req: RetrieveRequest, target_medium: str, allowed_subjects: List[str], active_content_types: List[str]) -> List[Tuple[int, dict]]:
        """
        Pre-filtering stage: screens chunks by metadata (class, subject, term, medium)
        """
        valid_indices = []
        for idx, chunk in enumerate(chunks):
            meta = chunk.get("metadata", {})
            
            # 1. Medium (Language) filter
            if meta.get("medium") != target_medium:
                continue
            # 2. Grade filter (optional)
            if req.class_id is not None and meta.get("class_level") != req.class_id:
                continue
            # 3. Subject filter
            chunk_sub = meta.get("subject", "science").lower()
            if chunk_sub not in allowed_subjects and not any(s in chunk_sub for s in allowed_subjects):
                continue
            # 4. Term matching for class 6 and 7 (optional)
            if req.class_id is not None and req.term is not None:
                if req.class_id in [6, 7] and meta.get("term") != req.term:
                    continue
                if req.class_id == 8 and meta.get("term") != 0:
                    continue
            # 5. Check if content type is allowed
            if meta.get("content_type", "textbook") not in active_content_types:
                continue

            valid_indices.append((idx, chunk))
            
        return valid_indices

    def reciprocal_rank_fusion(self, dense_results: List[str], sparse_results: List[str], k: int = 60) -> List[Tuple[str, float]]:
        rrf_scores = {}
        for rank, chunk_id in enumerate(dense_results):
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (1.0 / (k + rank + 1))
        for rank, chunk_id in enumerate(sparse_results):
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (1.0 / (k + rank + 1))
        return sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)

    async def retrieve(self, req: RetrieveRequest, query_vector: np.ndarray) -> Tuple[List[ChunkResult], bool]:
        """
        Asynchronously retrieves relevant document chunks, returning (results, fallback_applied).
        """
        return await anyio.to_thread.run_sync(self._retrieve_sync, req, query_vector)

    def _retrieve_sync(self, req: RetrieveRequest, query_vector: np.ndarray) -> Tuple[List[ChunkResult], bool]:
        preferred_medium = req.preferred_medium.lower()
        
        # 1. Primary Retrieve
        results = self._execute_retrieve_for_medium(req, query_vector, preferred_medium)
        fallback_applied = False
        
        # 2. Bilingual Fallback Retrieve if allowed and primary search yielded no results
        if not results and req.fallback_language_allowed:
            fallback_medium = "english" if preferred_medium == "tamil" else "tamil"
            results = self._execute_retrieve_for_medium(req, query_vector, fallback_medium)
            if results:
                fallback_applied = True
                
        return results, fallback_applied

    def _execute_retrieve_for_medium(self, req: RetrieveRequest, query_vector: np.ndarray, medium: str) -> List[ChunkResult]:
        lang_key = "ta" if medium == "tamil" else "en"
        
        all_chunks = self.cache.get(f"{lang_key}_chunks", [])
        all_embeddings = self.cache.get(f"{lang_key}_embeddings")

        if not all_chunks or all_embeddings is None or len(all_chunks) == 0:
            return []

        # Gather unique subjects present in the index
        available_subjects = list(set(c["metadata"].get("subject", "science").lower() for c in all_chunks if c.get("metadata")))
        
        # Determine allowed subjects based on query / request
        if req.subject and req.subject != "auto":
            req_sub = req.subject.lower()
            if req_sub in ["math", "maths", "mathematics"]:
                allowed_subjects = ["maths", "math", "mathematics"]
            else:
                allowed_subjects = [req_sub]
        else:
            allowed_subjects = self.detect_subjects(req.question, available_subjects)

        # Detect assessment intent and expand content types dynamically
        is_assessment = any(kw in req.question.lower() for kw in ["quiz", "test", "practice", "exercise", "exam", "questions", "pyq", "தேர்வு", "பயிற்சி", "வினாடி வினா"])
        active_content_types = list(req.allowed_content_types)
        if is_assessment:
            for t in ["previous_year", "teacher_notes", "firecrawl_education", "textbook", "guide"]:
                if t not in active_content_types:
                    active_content_types.append(t)

        # 1. Pre-filter candidates
        filtered_pairs = self.filter_candidates(all_chunks, req, medium, allowed_subjects, active_content_types)
        if not filtered_pairs:
            return []

        filtered_indices = [p[0] for p in filtered_pairs]
        filtered_chunks = [p[1] for p in filtered_pairs]

        # 2. Dense Cosine Search
        filtered_embeddings = all_embeddings[filtered_indices]
        dense_similarities = cosine_similarity(query_vector.reshape(1, -1), filtered_embeddings)[0]
        
        dense_ranked_pairs = sorted(
            zip(filtered_chunks, dense_similarities), 
            key=lambda x: x[1], 
            reverse=True
        )
        dense_ranked_ids = [pair[0]["chunk_id"] for pair in dense_ranked_pairs]

        # 3. Sparse BM25 Search
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
        chunk_map = {c["chunk_id"]: c for c in filtered_chunks}
        
        # 5. Source Prioritization & Supplemental Merging
        # Categories: Textbooks (1), Guides (2), PYQs (3), Teacher Notes (4), Firecrawl/Other (5)
        primary_results = []   # Textbooks & Guides
        secondary_results = [] # PYQs, Teacher Notes, and crawled content
        
        for chunk_id, rrf_score in fused_rankings:
            chunk = chunk_map[chunk_id]
            meta = chunk["metadata"]
            c_type = meta.get("content_type", "textbook")
            
            # Find dense score for citation/metrics
            dense_score = 0.0
            for p in dense_ranked_pairs:
                if p[0]["chunk_id"] == chunk_id:
                    dense_score = float(p[1])
                    break

            result = ChunkResult(
                chunk_id=chunk["chunk_id"],
                text=chunk["text"],
                score=float(rrf_score),
                source_filename=meta.get("filename", "unknown"),
                source_path=meta.get("relative_path", "unknown"),
                class_level=int(meta.get("class_level", req.class_id or 6)),
                term=int(meta.get("term", req.term or 0)),
                content_type=c_type,
                chapter_title=meta.get("chapter_title", "Unknown Chapter"),
                retrieval_tier=c_type,
                page_number=int(meta.get("page_number", 0)),
                section_no=str(meta.get("section_no", "unknown")),
                subject=meta.get("subject", "science"),
                language=meta.get("language", "en" if medium == "english" else "ta"),
                rank=1,  # Will assign final rank below
                source=meta.get("source", c_type),
                publisher=meta.get("publisher", "Tamil Nadu Textbook and Educational Services Corporation"),
                edition=meta.get("edition", "Unknown Edition")
            )
            
            if c_type in ["textbook", "guide"]:
                primary_results.append(result)
            else:
                secondary_results.append(result)

        # Merge based on priority:
        # Textbook & Guide content is returned first. 
        # PYQ, Notes, and Firecrawl (secondary) only supplement when primary results are insufficient
        final_results = []
        final_results.extend(primary_results)
        
        # Supplement from secondary sources if textbooks/guides alone don't reach target top_k * 2
        # (keeping enough candidates for reranking)
        needed = (req.top_k * 2) - len(final_results)
        if needed > 0 and secondary_results:
            final_results.extend(secondary_results[:needed])
            
        # Re-assign 1-indexed ranks to the final output list
        for idx, res in enumerate(final_results):
            res.rank = idx + 1
            
        return final_results[:req.top_k * 2]
