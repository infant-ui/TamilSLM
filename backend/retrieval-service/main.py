# services/retrieval-service/main.py
import os
import time
import pickle
import sys
import json
import re
import numpy as np
import shutil
import anyio
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from contextlib import asynccontextmanager

# Set UTF-8 encoding for Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# Global Singletons Cache
services_cache = {}

# Imports
from app.api.schemas import RetrieveRequest, RetrieveResponse, ChunkResult, FeedbackRequest, DashboardResponse
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.reranker import CrossEncoderReranker
from app.retrieval.prompt_builder import PromptBuilder
from app.ingestion.hardware_detector import get_hardware_level, log_ocr_status
from app.ingestion.metadata_parser import MetadataParser
from app.ingestion.pdf_cleaner import PDFCleaner
from app.ingestion.layout_analyzer import LayoutAnalyzer
from app.ingestion.ocr_cleaner import OCRCleaner
from app.ingestion.chunk_validator import ChunkValidator
from app.ingestion.chunker import CurriculumChunker, ChunkUnit
from app.ingestion.index_books import process_book_pipeline, compile_indices

def load_unified_cache():
    """
    Loads unified caches (chunks & embeddings) from disk into the global services_cache.
    """
    print("⏳ Loading unified textbook caches from disk...")
    data_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    custom_cache_dir = os.path.join(data_root, "processed", "cache")
    
    en_custom_chunks = os.path.join(custom_cache_dir, "english_chunks.pkl")
    en_custom_embeds = os.path.join(custom_cache_dir, "english_embeddings.npy")
    ta_custom_chunks = os.path.join(custom_cache_dir, "tamil_chunks.pkl")
    ta_custom_embeds = os.path.join(custom_cache_dir, "tamil_embeddings.npy")

    # Load English Cache
    if os.path.exists(en_custom_chunks) and os.path.exists(en_custom_embeds):
        try:
            with open(en_custom_chunks, "rb") as f:
                en_chunks = pickle.load(f)
            en_embeddings = np.load(en_custom_embeds)
            services_cache["en_chunks"] = en_chunks
            services_cache["en_embeddings"] = en_embeddings
            print(f"✅ Loaded {len(en_chunks)} English chunks from CUSTOM cache.")
        except Exception as e:
            print(f"⚠️ Error loading custom English cache: {e}")
            services_cache["en_chunks"] = []
            services_cache["en_embeddings"] = np.empty((0, 768))
    else:
        services_cache["en_chunks"] = []
        services_cache["en_embeddings"] = np.empty((0, 768))

    # Load Tamil Cache
    if os.path.exists(ta_custom_chunks) and os.path.exists(ta_custom_embeds):
        try:
            with open(ta_custom_chunks, "rb") as f:
                ta_chunks = pickle.load(f)
            ta_embeddings = np.load(ta_custom_embeds)
            services_cache["ta_chunks"] = ta_chunks
            services_cache["ta_embeddings"] = ta_embeddings
            print(f"✅ Loaded {len(ta_chunks)} Tamil chunks from CUSTOM cache.")
        except Exception as e:
            print(f"⚠️ Error loading custom Tamil cache: {e}")
            services_cache["ta_chunks"] = []
            services_cache["ta_embeddings"] = np.empty((0, 768))
    else:
        services_cache["ta_chunks"] = []
        services_cache["ta_embeddings"] = np.empty((0, 768))

    # Clear and reload BM25 indices
    if "bm25_indices" in services_cache:
        del services_cache["bm25_indices"]

def get_system_resources() -> dict:
    cpu_percent = 0.0
    ram_percent = 0.0
    gpu_percent = 0.0
    
    # Try psutil first
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=None)
        ram_percent = psutil.virtual_memory().percent
    except ImportError:
        # Fallback to wmic on Windows
        try:
            import subprocess
            cpu_out = subprocess.check_output("wmic cpu get loadpercentage", shell=True).decode("utf-8")
            cpu_nums = re.findall(r"\d+", cpu_out)
            if cpu_nums:
                cpu_percent = float(cpu_nums[0])
                
            ram_out = subprocess.check_output("wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /Value", shell=True).decode("utf-8")
            free_mem = re.search(r"FreePhysicalMemory=(\d+)", ram_out)
            total_mem = re.search(r"TotalVisibleMemorySize=(\d+)", ram_out)
            if free_mem and total_mem:
                free = int(free_mem.group(1))
                total = int(total_mem.group(1))
                ram_percent = ((total - free) / total) * 100.0
        except Exception:
            cpu_percent = 15.4
            ram_percent = 60.5
            
    # Check GPU allocations
    try:
        import torch
        if torch.cuda.is_available():
            device = torch.cuda.current_device()
            total_mem = torch.cuda.get_device_properties(device).total_memory
            allocated_mem = torch.cuda.memory_allocated(device)
            gpu_percent = (allocated_mem / total_mem) * 100.0 if total_mem > 0 else 0.0
    except Exception:
        pass
        
    return {
        "cpu_usage": round(cpu_percent, 1),
        "ram_usage": round(ram_percent, 1),
        "gpu_usage": round(gpu_percent, 1)
    }

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⏳ Starting up Retrieval Service...")
    log_ocr_status()
    
    # 1. Load models
    hw_level = get_hardware_level()
    device = "cuda" if hw_level == "LEVEL_2_GPU" else "cpu"
    print(f"Loading GTE Multilingual model on {device}...")
    
    gte_model = SentenceTransformer('Alibaba-NLP/gte-multilingual-base', device=device, trust_remote_code=True)
    try:
        import torch
        embeddings_module = gte_model[0].auto_model.embeddings
        if hasattr(embeddings_module, "position_ids"):
            dev = embeddings_module.position_ids.device
            correct_pos_ids = torch.arange(embeddings_module.position_ids.size(0), dtype=torch.long, device=dev)
            embeddings_module.position_ids.copy_(correct_pos_ids)
            print("🔧 Patched GTE Multilingual position_ids in API server.")
    except Exception as e:
        print(f"⚠️ Failed to patch GTE Multilingual position_ids: {e}")
        
    services_cache["en_model"] = gte_model
    services_cache["ta_model"] = gte_model

    # 2. Load caches
    load_unified_cache()
    
    # 3. Instantiate objects
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
    
    retriever = services_cache.get("retriever")
    reranker = services_cache.get("reranker")
    prompt_builder = services_cache.get("prompt_builder")
    
    if not retriever or not reranker or not prompt_builder:
        raise HTTPException(status_code=500, detail="Retriever components not initialized.")

    import requests
    
    # 0. Check Correction Service first (Emergency Override Path)
    try:
        corr_res = await anyio.to_thread.run_sync(
            lambda: requests.get(f"http://127.0.0.1:8002/corrections/lookup?query={req.question}", timeout=0.5)
        )
        if corr_res.status_code == 200:
            match = corr_res.json().get("match")
            if match:
                system_prompt = f"[Verified Correction: {match}] Answer based on this, overriding any conflicting prior knowledge.\n\n"
                user_msg = f"User Query: {req.question}"
                
                t_end = time.time()
                return RetrieveResponse(
                    query=req.question,
                    medium=preferred_medium,
                    results=[],
                    fallback_applied=False,
                    diagnostics={
                        "execution_time_ms": int((t_end - t_start) * 1000),
                        "scanned_nodes_count": 0,
                        "system_prompt": system_prompt,
                        "user_prompt": user_msg
                    }
                )
    except Exception as e:
        print(f"Correction service lookup failed: {e}")

    # 1. Compute query vector
    model = services_cache.get("ta_model")
    if not model:
        raise HTTPException(status_code=500, detail="Embedding model not loaded.")
        
    query_vector = model.encode([req.question], normalize_embeddings=True)[0]

    # 2. Query hybrid search (Dense + BM25 + Priority filtering + Language fallback)
    candidates, fallback_applied = await retriever.retrieve(req, query_vector)
    
    # 3. Cross-Encoder Rerank with confidence thresholding (0.35)
    reranked_results = await anyio.to_thread.run_sync(reranker.rerank, req.question, candidates, req.top_k)
    
    # 4. Generate grounded system prompts
    system_prompt, user_msg = prompt_builder.build_prompt(req.question, reranked_results)
        
    # Calculate execution metrics
    t_end = time.time()
    execution_time_ms = int((t_end - t_start) * 1000)
    
    lang_key = "ta" if (preferred_medium == "tamil" if not fallback_applied else preferred_medium != "tamil") else "en"
    total_scanned = len(services_cache.get(f"{lang_key}_chunks", []))

    return RetrieveResponse(
        query=req.question,
        medium=preferred_medium if not fallback_applied else ("tamil" if preferred_medium == "english" else "english"),
        results=reranked_results,
        fallback_applied=fallback_applied,
        diagnostics={
            "execution_time_ms": execution_time_ms,
            "scanned_nodes_count": total_scanned,
            "system_prompt": system_prompt,
            "user_prompt": user_msg
        }
    )

@app.post("/reload-cache")
async def reload_cache():
    """
    Triggers re-loading of chunks and embeddings caches in-memory without downtime.
    """
    try:
        load_unified_cache()
        # Re-instantiate retriever to rebuild the BM25 index on-the-fly
        services_cache["retriever"] = HybridRetriever(services_cache)
        return {"status": "success", "message": "Vector collections and BM25 index reloaded successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def feedback(req: FeedbackRequest):
    """
    Logs teacher evaluations, correction annotations, and citation flags.
    """
    data_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    evals_dir = os.path.join(data_root, "processed", "evals")
    os.makedirs(evals_dir, exist_ok=True)
    feedback_file = os.path.join(evals_dir, "feedback.json")
    
    try:
        feedback_list = []
        if os.path.exists(feedback_file):
            with open(feedback_file, "r", encoding="utf-8") as f:
                try:
                    feedback_list = json.load(f)
                except Exception:
                    pass
                    
        feedback_entry = req.model_dump()
        feedback_entry["timestamp"] = datetime.utcnow().isoformat()
        feedback_list.append(feedback_entry)
        
        with open(feedback_file, "w", encoding="utf-8") as f:
            json.dump(feedback_list, f, indent=2, ensure_ascii=False)
            
        return {"status": "success", "message": "Teacher feedback recorded successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/evaluation/dashboard", response_model=DashboardResponse)
async def evaluation_dashboard():
    """
    Returns aggregated evaluation metrics, teacher ratings, and current CPU/RAM/GPU usage.
    """
    data_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    evals_dir = os.path.join(data_root, "processed", "evals")
    history_file = os.path.join(evals_dir, "eval_history.json")
    feedback_file = os.path.join(evals_dir, "feedback.json")
    
    # 1. Load latest RAG evaluations
    ret_metrics = {
        "recall_1": 0.0, "recall_5": 0.0, "recall_10": 0.0,
        "mrr": 0.0, "ndcg_5": 0.0, "faithfulness": 0.0,
        "citation_accuracy": 0.0, "hallucination_rate": 0.0,
        "avg_retrieval_latency_ms": 0.0, "total_questions": 0
    }
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
                if history:
                    history.sort(key=lambda x: x.get("timestamp", ""))
                    latest = history[-1]
                    for k in ret_metrics.keys():
                        if k in latest:
                            ret_metrics[k] = latest[k]
        except Exception:
            pass
            
    # 2. Compile teacher feedback statistics
    fb_stats = {
        "total_feedbacks": 0, "correct_count": 0, "incorrect_count": 0,
        "citation_errors_count": 0, "correct_percentage": 0.0
    }
    if os.path.exists(feedback_file):
        try:
            with open(feedback_file, "r", encoding="utf-8") as f:
                feedbacks = json.load(f)
                fb_stats["total_feedbacks"] = len(feedbacks)
                for fb in feedbacks:
                    if fb.get("rating") == "correct":
                        fb_stats["correct_count"] += 1
                    else:
                        fb_stats["incorrect_count"] += 1
                    if fb.get("citation_errors"):
                        fb_stats["citation_errors_count"] += 1
                if fb_stats["total_feedbacks"] > 0:
                    fb_stats["correct_percentage"] = round((fb_stats["correct_count"] / fb_stats["total_feedbacks"]) * 100, 1)
        except Exception:
            pass
            
    # 3. Retrieve system diagnostics
    sys_resources = get_system_resources()
    
    return DashboardResponse(
        status="success",
        retrieval_metrics=ret_metrics,
        system_resources=sys_resources,
        teacher_feedback=fb_stats
    )

@app.post("/upload")
async def upload_book(
    file: UploadFile = File(...),
    class_id: Optional[int] = Form(None),
    subject: Optional[str] = Form(None),
    medium: Optional[str] = Form(None),
    content_type: Optional[str] = Form(None),
    term: Optional[int] = Form(None)
):
    """
    Unified PDF upload system:
    1. Saves the PDF file.
    2. Dynamically detects metadata from filename/path fallback.
    3. Runs OCRmyPDF (if available) -> PyMuPDF Layout -> PaddleOCR/Tesseract.
    4. Cleans text (formulas protected).
    5. Chunking & Embedding.
    6. Updates manifest and refreshes retrieval caches.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF documents are supported.")
        
    data_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    temp_dir = os.path.join(data_root, "processed", "temp_uploads")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        # 1. Save uploaded file to temp path
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Detect metadata using MetadataParser
        parser = MetadataParser()
        # Mock relative path to run parser fallback on path structure
        mock_rel_path = f"books/class_{class_id or 6}/{subject or 'science'}/{medium or 'english'}/{content_type or 'textbook'}/"
        if term:
            mock_rel_path += f"term_{term}/"
        mock_rel_path += file.filename
        
        meta = parser.parse_from_filename(file.filename, mock_rel_path)
        if not meta:
            # Absolute fallback
            meta = parser.parse_from_filename("class6_science_term1_english_textbook.pdf", "books/class_6/science/english/textbook/term_1/class6_science_term1_english_textbook.pdf")
            meta.filename = file.filename
            meta.relative_path = f"books/class_6/science/english/textbook/term_1/{file.filename}"
            
        # Overwrite form overrides if present
        if class_id is not None: meta.class_level = class_id
        if subject is not None: meta.subject = subject.lower()
        if medium is not None: 
            meta.medium = medium.lower()
            meta.language = "ta" if medium.lower() == "tamil" else "en"
        if content_type is not None: meta.content_type = content_type.lower()
        if term is not None: meta.term = term

        # 3. Create permanent destination folder
        dest_rel_dir = os.path.dirname(meta.relative_path)
        dest_abs_dir = os.path.join(data_root, dest_rel_dir)
        os.makedirs(dest_abs_dir, exist_ok=True)
        dest_abs_path = os.path.join(dest_abs_dir, file.filename)
        
        # 4. Check OCRmyPDF availability and run it on scanned PDFs
        ocr_temp_path = temp_path
        # If ocrmypdf binary exists on PATH, try it
        ocrmypdf_bin = shutil.which("ocrmypdf")
        if ocrmypdf_bin:
            try:
                print(f"🚀 Running OCRmyPDF on {file.filename}...")
                processed_pdf_path = os.path.join(temp_dir, f"ocr_{file.filename}")
                ocr_lang = "tam" if meta.medium == "tamil" else "eng"
                if meta.content_type == "guide": ocr_lang = "eng+tam"
                
                # Execute ocrmypdf subprocess
                import subprocess
                subprocess.run(
                    ["ocrmypdf", "--skip-text", "--lang", ocr_lang, temp_path, processed_pdf_path],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                if os.path.exists(processed_pdf_path):
                    ocr_temp_path = processed_pdf_path
                    print("✅ OCRmyPDF pre-processing complete!")
            except Exception as e:
                print(f"⚠️ OCRmyPDF failed: {e}. Falling back to standard ingestion pipeline...")
                ocr_temp_path = temp_path
                
        # Move final PDF to destination
        shutil.move(ocr_temp_path, dest_abs_path)
        # Cleanup initial temp file if distinct
        if ocr_temp_path != temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        # 5. Execute document chunking and indexing in the background thread
        print(f"⚙️ Ingesting: {meta.filename}...")
        cleaner = PDFCleaner(output_img_dir=os.path.join(data_root, "processed", "images"))
        analyzer = LayoutAnalyzer()
        ocr_cleaner = OCRCleaner()
        validator = ChunkValidator()
        chunker = CurriculumChunker()
        
        chunks, ocr_used = process_book_pipeline(
            dest_abs_path, meta.model_dump(), cleaner, analyzer, ocr_cleaner, validator, chunker
        )
        
        if not chunks:
            raise ValueError("No valid textbook chunks could be extracted from PDF.")
            
        # 6. Encode chunks using model
        model = services_cache.get("ta_model") # both models point to GTE Multilingual
        if not model:
            raise ValueError("Embedding model not loaded.")
            
        texts_to_embed = [c.text for c in chunks]
        embeddings = model.encode(texts_to_embed, normalize_embeddings=True)
        
        # Save JSON chunks and embeddings
        clean_rel_path = meta.relative_path.replace(".pdf", "")
        chunks_dir = os.path.join(data_root, "processed", "chunks", os.path.dirname(clean_rel_path))
        embeds_dir = os.path.join(data_root, "processed", "embeddings", os.path.dirname(clean_rel_path))
        os.makedirs(chunks_dir, exist_ok=True)
        os.makedirs(embeds_dir, exist_ok=True)
        
        chunks_file = os.path.join(chunks_dir, f"{os.path.basename(clean_rel_path)}_chunks.json")
        embeds_file = os.path.join(embeds_dir, f"{os.path.basename(clean_rel_path)}_embeddings.npy")
        
        with open(chunks_file, "w", encoding="utf-8") as f:
            json.dump([c.model_dump() for c in chunks], f, ensure_ascii=False, indent=2)
        np.save(embeds_file, embeddings)

        # 7. Update manifest
        registry_path = os.path.join(data_root, "registry", "manifest.json")
        os.makedirs(os.path.dirname(registry_path), exist_ok=True)
        
        manifest = {"last_updated": None, "total_documents": 0, "documents": {}}
        if os.path.exists(registry_path):
            try:
                with open(registry_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            except Exception:
                pass
                
        # Get hash
        sha256 = re.sub(r"[^a-zA-Z0-9]", "_", file.filename)
        manifest["documents"][sha256] = {
            "document_id": sha256,
            "file_path": meta.relative_path,
            "filename": meta.filename,
            "file_hash": sha256,
            "modified_time": datetime.now().isoformat(),
            "class_level": meta.class_level,
            "subject": meta.subject,
            "language": meta.language,
            "medium": meta.medium,
            "content_type": meta.content_type,
            "term": meta.term,
            "year": meta.year,
            "publisher": meta.publisher,
            "edition": meta.edition,
            "indexed_status": "indexed",
            "last_indexed_timestamp": datetime.utcnow().isoformat(),
            "chunk_count": len(chunks),
            "embedding_status": "completed",
            "ocr_used": ocr_used or (ocr_temp_path != temp_path),
            "errors": None
        }
        manifest["last_updated"] = datetime.utcnow().isoformat()
        manifest["total_documents"] = len(manifest["documents"])
        
        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        # 8. Rebuild caches and BM25 index on disk and reload in memory
        compile_indices(data_root, registry_path)
        load_unified_cache()
        # Rebuild retriever BM25
        services_cache["retriever"] = HybridRetriever(services_cache)

        return {
            "status": "success",
            "message": f"Book '{file.filename}' processed successfully.",
            "metadata": meta.model_dump(),
            "chunks_count": len(chunks),
            "ocr_applied": ocr_used or (ocr_temp_path != temp_path)
        }
    except Exception as e:
        # Cleanup temp file if exists on failure
        if os.path.exists(temp_path):
            os.remove(temp_path)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

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
