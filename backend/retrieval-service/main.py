# services/retrieval-service/main.py
import os
import time
import pickle
import sys
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import anyio
from sentence_transformers import SentenceTransformer
from contextlib import asynccontextmanager

# Set UTF-8 encoding for stdout/stderr to prevent charmap encoding errors under Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# Low memory/CPU usage limits for local execution
# os.environ["OMP_NUM_THREADS"] = "1"
# os.environ["OPENBLAS_NUM_THREADS"] = "1"
# os.environ["MKL_NUM_THREADS"] = "1"

# Global Singletons
services_cache = {}

# Import our Pydantic schemas, hybrid retriever, reranker, and prompt builder
from app.api.schemas import RetrieveRequest, RetrieveResponse, ChunkResult
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.reranker import CrossEncoderReranker
from app.retrieval.prompt_builder import PromptBuilder
from app.ingestion.hardware_detector import get_hardware_level

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⏳ Starting up Retrieval Service...")
    
    # 1. Setup paths
    data_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    custom_cache_dir = os.path.join(data_root, "processed", "cache")
    
    en_custom_chunks = os.path.join(custom_cache_dir, "english_chunks.pkl")
    en_custom_embeds = os.path.join(custom_cache_dir, "english_embeddings.npy")
    ta_custom_chunks = os.path.join(custom_cache_dir, "tamil_chunks.pkl")
    ta_custom_embeds = os.path.join(custom_cache_dir, "tamil_embeddings.npy")

    # Baseline paths (fallback)
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
    baseline_cache_dir = os.path.join(models_dir, "cache")
    
    en_baseline_chunks = os.path.join(baseline_cache_dir, "english_chunks.pkl")
    en_baseline_embeds = os.path.join(baseline_cache_dir, "english_embeddings.npy")
    ta_baseline_chunks = os.path.join(baseline_cache_dir, "tamil_chunks.pkl")
    ta_baseline_embeds = os.path.join(baseline_cache_dir, "tamil_embeddings.npy")
    
    # 2. Load models
    hw_level = get_hardware_level()
    device = "cuda" if hw_level == "LEVEL_2_GPU" else "cpu"
    print(f"Loading GTE Multilingual model on {device}...")
    
    # Standardize both Tamil and English embeddings on Alibaba GTE Multilingual Base
    gte_model = SentenceTransformer('Alibaba-NLP/gte-multilingual-base', device=device, trust_remote_code=True)
    try:
        import torch
        embeddings_module = gte_model[0].auto_model.embeddings
        if hasattr(embeddings_module, "position_ids"):
            dev = embeddings_module.position_ids.device
            correct_pos_ids = torch.arange(embeddings_module.position_ids.size(0), dtype=torch.long, device=dev)
            embeddings_module.position_ids.copy_(correct_pos_ids)
            print("🔧 Successfully patched GTE Multilingual position_ids buffer in API server!")
    except Exception as e:
        print(f"⚠️ Failed to patch GTE Multilingual position_ids in API server: {e}")
        
    services_cache["en_model"] = gte_model
    services_cache["ta_model"] = gte_model

    # 3. Load English textbook chunks and embeddings
    en_loaded = False
    if os.path.exists(en_custom_chunks) and os.path.exists(en_custom_embeds):
        try:
            print("Loading English textbook chunks and embeddings from CUSTOM cache...")
            with open(en_custom_chunks, "rb") as f:
                en_chunks = pickle.load(f)
            en_embeddings = np.load(en_custom_embeds)
            if len(en_chunks) > 0:
                services_cache["en_chunks"] = en_chunks
                services_cache["en_embeddings"] = en_embeddings
                en_loaded = True
                print(f"Loaded {len(en_chunks)} English chunks from CUSTOM cache.")
        except Exception as e:
            print(f"⚠️ Error loading custom English cache: {e}")

    if not en_loaded and os.path.exists(en_baseline_chunks) and os.path.exists(en_baseline_embeds):
        try:
            print("Loading English textbook chunks from BASELINE cache...")
            with open(en_baseline_chunks, "rb") as f:
                en_chunks_raw = pickle.load(f)
            en_embeddings = np.load(en_baseline_embeds)
            
            # Map baseline simple list of strings to new chunk metadata structure
            en_chunks = []
            for i, text in enumerate(en_chunks_raw):
                en_chunks.append({
                    "chunk_id": f"baseline_en_{i}",
                    "text": text,
                    "metadata": {
                        "document_id": "science_english.pdf",
                        "file_path": "books/class_6/science/english/textbook/term_1/science_english.pdf",
                        "filename": "science_english.pdf",
                        "class_level": 6,
                        "subject": "science",
                        "language": "en",
                        "medium": "english",
                        "content_type": "textbook",
                        "term": 1,
                        "year": 2024,
                        "chapter_title": "Baseline Textbook",
                        "content_role": "concept",
                        "page_number": 1,
                        "section_no": "1.1"
                    }
                })
            
            services_cache["en_chunks"] = en_chunks
            services_cache["en_embeddings"] = en_embeddings
            en_loaded = True
            print(f"Loaded {len(en_chunks)} English chunks from BASELINE cache.")
        except Exception as e:
            print(f"⚠️ Error loading baseline English cache: {e}")

    if not en_loaded:
        print("⚠️ No English chunks or embeddings found! Starting with empty English index.")
        services_cache["en_chunks"] = []
        services_cache["en_embeddings"] = np.empty((0, 768))

    # 4. Load Tamil textbook chunks and embeddings
    ta_loaded = False
    if os.path.exists(ta_custom_chunks) and os.path.exists(ta_custom_embeds):
        try:
            print("Loading Tamil textbook chunks and embeddings from CUSTOM cache...")
            with open(ta_custom_chunks, "rb") as f:
                ta_chunks = pickle.load(f)
            ta_embeddings = np.load(ta_custom_embeds)
            if len(ta_chunks) > 0:
                services_cache["ta_chunks"] = ta_chunks
                services_cache["ta_embeddings"] = ta_embeddings
                ta_loaded = True
                print(f"Loaded {len(ta_chunks)} Tamil chunks from CUSTOM cache.")
        except Exception as e:
            print(f"⚠️ Error loading custom Tamil cache: {e}")

    if not ta_loaded and os.path.exists(ta_baseline_chunks) and os.path.exists(ta_baseline_embeds):
        try:
            print("Loading Tamil textbook chunks from BASELINE cache...")
            with open(ta_baseline_chunks, "rb") as f:
                ta_chunks_raw = pickle.load(f)
            ta_embeddings = np.load(ta_baseline_embeds)
            
            # Map baseline simple list of strings to new chunk metadata structure
            ta_chunks = []
            for i, text in enumerate(ta_chunks_raw):
                ta_chunks.append({
                    "chunk_id": f"baseline_ta_{i}",
                    "text": text,
                    "metadata": {
                        "document_id": "tamil_science_textbook.txt",
                        "file_path": "books/class_6/science/tamil/textbook/term_1/tamil_science_textbook.txt",
                        "filename": "tamil_science_textbook.txt",
                        "class_level": 6,
                        "subject": "science",
                        "language": "ta",
                        "medium": "tamil",
                        "content_type": "textbook",
                        "term": 1,
                        "year": 2024,
                        "chapter_title": "Baseline Textbook",
                        "content_role": "concept",
                        "page_number": 1,
                        "section_no": "1.1"
                    }
                })
            
            services_cache["ta_chunks"] = ta_chunks
            services_cache["ta_embeddings"] = ta_embeddings
            ta_loaded = True
            print(f"Loaded {len(ta_chunks)} Tamil chunks from BASELINE cache.")
        except Exception as e:
            print(f"⚠️ Error loading baseline Tamil cache: {e}")

    if not ta_loaded:
        print("⚠️ No Tamil chunks or embeddings found! Starting with empty Tamil index.")
        services_cache["ta_chunks"] = []
        services_cache["ta_embeddings"] = np.empty((0, 768))

    # 5. Validate and re-generate embeddings if dimensions mismatch
    if services_cache.get("en_chunks") and services_cache.get("en_embeddings") is not None:
        en_embeds = services_cache["en_embeddings"]
        if en_embeds.ndim > 1 and en_embeds.shape[0] > 0 and en_embeds.shape[1] != 768:
            print(f"⚠️ Dimension mismatch in English embeddings (got {en_embeds.shape[1]}, expected 768). Re-generating on-the-fly...")
            texts = [c["text"] for c in services_cache["en_chunks"]]
            new_embeds = gte_model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
            services_cache["en_embeddings"] = new_embeds
            
            try:
                os.makedirs(custom_cache_dir, exist_ok=True)
                with open(en_custom_chunks, "wb") as f:
                    pickle.dump(services_cache["en_chunks"], f)
                np.save(en_custom_embeds, new_embeds)
                print("💾 Successfully saved re-encoded English chunks & embeddings to CUSTOM cache.")
            except Exception as e:
                print(f"⚠️ Failed to save English custom cache: {e}")

    if services_cache.get("ta_chunks") and services_cache.get("ta_embeddings") is not None:
        ta_embeds = services_cache["ta_embeddings"]
        if ta_embeds.ndim > 1 and ta_embeds.shape[0] > 0 and ta_embeds.shape[1] != 768:
            print(f"⚠️ Dimension mismatch in Tamil embeddings (got {ta_embeds.shape[1]}, expected 768). Re-generating on-the-fly...")
            texts = [c["text"] for c in services_cache["ta_chunks"]]
            new_embeds = gte_model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
            services_cache["ta_embeddings"] = new_embeds
            
            try:
                os.makedirs(custom_cache_dir, exist_ok=True)
                with open(ta_custom_chunks, "wb") as f:
                    pickle.dump(services_cache["ta_chunks"], f)
                np.save(ta_custom_embeds, new_embeds)
                print("💾 Successfully saved re-encoded Tamil chunks & embeddings to CUSTOM cache.")
            except Exception as e:
                print(f"⚠️ Failed to save Tamil custom cache: {e}")

    # Initialize priority retriever, cross-encoder reranker, and prompt builder
    services_cache["retriever"] = HybridRetriever(services_cache)
    services_cache["reranker"] = CrossEncoderReranker()
    services_cache["prompt_builder"] = PromptBuilder()

    print("✅ Retrieval Service Initialized successfully.")
    yield
    print("🧹 Cleaning up models...")
    services_cache.clear()

app = FastAPI(lifespan=lifespan)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/retrieve", response_model=RetrieveResponse)
async def retrieve(req: RetrieveRequest):
    t_start = time.time()
    
    preferred_medium = req.preferred_medium.lower()
    
    # Check if retriever is ready
    retriever = services_cache.get("retriever")
    reranker = services_cache.get("reranker")
    prompt_builder = services_cache.get("prompt_builder")
    
    if not retriever or not reranker or not prompt_builder:
        raise HTTPException(status_code=500, detail="Retriever components not initialized.")

    # 1. Compute query vector using the GTE Multilingual model
    model = services_cache.get("ta_model") # both point to GTE Multilingual
    if not model:
        raise HTTPException(status_code=500, detail="Embedding model not loaded.")
        
    query_vector = model.encode([req.question], normalize_embeddings=True)[0]

    # 2. Query hybrid search (Cosine dense + BM25 sparse + RRF)
    candidates = await retriever.retrieve(req, query_vector)
    
    # 3. Cross-Encoder Rerank with confidence thresholding (0.35)
    reranked_results = await anyio.to_thread.run_sync(reranker.rerank, req.question, candidates, req.top_k)
    
    # 4. Generate grounded system prompts for local Qwen
    system_prompt, user_msg = prompt_builder.build_prompt(req.question, reranked_results)
    
    # Calculate execution diagnostics
    t_end = time.time()
    execution_time_ms = int((t_end - t_start) * 1000)
    
    lang_key = "ta" if preferred_medium == "tamil" else "en"
    total_scanned = len(services_cache.get(f"{lang_key}_chunks", []))

    return RetrieveResponse(
        query=req.question,
        medium=preferred_medium,
        results=reranked_results,
        fallback_applied=False,
        diagnostics={
            "execution_time_ms": execution_time_ms,
            "scanned_nodes_count": total_scanned,
            "system_prompt": system_prompt,
            "user_prompt": user_msg
        }
    )

@app.post("/retrieve/debug")
async def retrieve_debug(req: RetrieveRequest):
    res = await retrieve(req)
    pref_lang = req.preferred_medium.lower()
    lang_key = "ta" if pref_lang == "tamil" else "en"
    return {
        "status": "success",
        "diagnostic_metrics": {
            "num_chunks_available": len(services_cache.get(f"{lang_key}_chunks", [])),
            "dimensions": int(services_cache.get(f"{lang_key}_embeddings").shape[1]) if services_cache.get(f"{lang_key}_embeddings") is not None else 0
        },
        "response": res
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
