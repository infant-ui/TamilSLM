import os
import json
import re
import numpy as np
from datetime import datetime
import shutil
import subprocess

from celery import Celery
from celery.exceptions import Ignore
import redis

from app.ingestion.pdf_cleaner import PDFCleaner
from app.ingestion.layout_analyzer import LayoutAnalyzer
from app.ingestion.ocr_cleaner import OCRCleaner
from app.ingestion.chunk_validator import ChunkValidator
from app.ingestion.chunker import CurriculumChunker
from app.ingestion.index_books import process_book_pipeline, compile_indices
from sentence_transformers import SentenceTransformer

celery_app = Celery(
    "ingestion_tasks",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/1"),
    backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/2")
)

_embedding_model = None
def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("Alibaba-NLP/gte-multilingual-base", trust_remote_code=True)
    return _embedding_model

@celery_app.task(bind=True)
def process_upload_task(self, temp_path: str, meta_dict: dict, data_root: str):
    self.update_state(state='PROCESSING')
    
    try:
        dest_rel_dir = os.path.dirname(meta_dict["relative_path"])
        dest_abs_dir = os.path.join(data_root, dest_rel_dir)
        os.makedirs(dest_abs_dir, exist_ok=True)
        dest_abs_path = os.path.join(dest_abs_dir, meta_dict["filename"])
        
        ocr_temp_path = temp_path
        ocrmypdf_bin = shutil.which("ocrmypdf")
        if ocrmypdf_bin:
            try:
                temp_dir = os.path.dirname(temp_path)
                processed_pdf_path = os.path.join(temp_dir, f"ocr_{meta_dict['filename']}")
                ocr_lang = "tam" if meta_dict["medium"] == "tamil" else "eng"
                if meta_dict["content_type"] == "guide": ocr_lang = "eng+tam"
                
                subprocess.run(
                    ["ocrmypdf", "--skip-text", "--lang", ocr_lang, temp_path, processed_pdf_path],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                if os.path.exists(processed_pdf_path):
                    ocr_temp_path = processed_pdf_path
            except Exception as e:
                print(f"⚠️ OCRmyPDF failed: {e}. Falling back to standard pipeline...")
                ocr_temp_path = temp_path
                
        shutil.move(ocr_temp_path, dest_abs_path)
        if ocr_temp_path != temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
                
        cleaner = PDFCleaner(output_img_dir=os.path.join(data_root, "processed", "images"))
        analyzer = LayoutAnalyzer()
        ocr_cleaner = OCRCleaner()
        validator = ChunkValidator()
        chunker = CurriculumChunker()
        
        chunks, ocr_used = process_book_pipeline(
            dest_abs_path, meta_dict, cleaner, analyzer, ocr_cleaner, validator, chunker
        )
        
        if not chunks:
            raise ValueError("No valid textbook chunks could be extracted from PDF.")
            
        model = get_embedding_model()
        texts_to_embed = [c.text for c in chunks]
        embeddings = model.encode(texts_to_embed, normalize_embeddings=True)
        
        clean_rel_path = meta_dict['relative_path'].replace(".pdf", "")
        chunks_dir = os.path.join(data_root, "processed", "chunks", os.path.dirname(clean_rel_path))
        embeds_dir = os.path.join(data_root, "processed", "embeddings", os.path.dirname(clean_rel_path))
        os.makedirs(chunks_dir, exist_ok=True)
        os.makedirs(embeds_dir, exist_ok=True)
        
        chunks_file = os.path.join(chunks_dir, f"{os.path.basename(clean_rel_path)}_chunks.json")
        embeds_file = os.path.join(embeds_dir, f"{os.path.basename(clean_rel_path)}_embeddings.npy")
        
        with open(chunks_file, "w", encoding="utf-8") as f:
            json.dump([c.model_dump() for c in chunks], f, ensure_ascii=False, indent=2)
        np.save(embeds_file, embeddings)
        
        # Manifest
        redis_host = os.environ.get("REDIS_HOST", "redis")
        r = redis.Redis(host=redis_host, port=6379, db=0)
        registry_path = os.path.join(data_root, "registry", "manifest.json")
        os.makedirs(os.path.dirname(registry_path), exist_ok=True)
        
        with r.lock("manifest_lock", timeout=60):
            manifest = {"last_updated": None, "total_documents": 0, "documents": {}}
            if os.path.exists(registry_path):
                try:
                    with open(registry_path, "r", encoding="utf-8") as f:
                        manifest = json.load(f)
                except Exception:
                    pass
            
            sha256 = re.sub(r"[^a-zA-Z0-9]", "_", meta_dict['filename'])
            manifest["documents"][sha256] = {
                "document_id": sha256,
                "file_path": meta_dict['relative_path'],
                "filename": meta_dict['filename'],
                "file_hash": sha256,
                "modified_time": datetime.now().isoformat(),
                "class_level": meta_dict['class_level'],
                "subject": meta_dict['subject'],
                "language": meta_dict['language'],
                "medium": meta_dict['medium'],
                "content_type": meta_dict['content_type'],
                "term": meta_dict['term'],
                "year": meta_dict['year'],
                "publisher": meta_dict['publisher'],
                "edition": meta_dict['edition'],
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

        compile_indices(data_root, registry_path)

        return {
            "message": "Success", 
            "chunks_count": len(chunks),
            "ocr_applied": ocr_used or (ocr_temp_path != temp_path)
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        self.update_state(state='FAILED', meta={'error': str(e)})
        raise Ignore()
