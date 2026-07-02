# services/retrieval-service/app/ingestion/index_books.py
import os
import sys
import argparse
import json
import fitz  # PyMuPDF
import numpy as np
import pickle
from datetime import datetime
from sentence_transformers import SentenceTransformer

from app.ingestion.book_scanner import BookScanner
from app.ingestion.hardware_detector import log_ocr_status, run_diagnostics, get_hardware_level
from app.ingestion.pdf_cleaner import PDFCleaner
from app.ingestion.layout_analyzer import LayoutAnalyzer
from app.ingestion.ocr_cleaner import OCRCleaner
from app.ingestion.chapter_parser import ChapterParser
from app.ingestion.section_parser import SectionParser
from app.ingestion.logical_block_builder import LogicalBlockBuilder
from app.ingestion.chunk_validator import ChunkValidator
from app.ingestion.chunker import CurriculumChunker, ChunkUnit, ScienceChunker

# Set UTF-8 encoding for stdout/stderr to prevent charmap encoding errors under Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def process_book_pipeline(pdf_path: str, book_metadata: dict, cleaner: PDFCleaner, 
                          analyzer: LayoutAnalyzer, ocr: OCRCleaner, validator: ChunkValidator, 
                          chunker: CurriculumChunker) -> tuple[list, bool]:
    """
    Complete end-to-end Document Intelligence pipeline for a single book.
    """
    doc = fitz.open(pdf_path)
    all_chunks = []
    ocr_used = False
    
    chapter_parser = ChapterParser()
    section_parser = SectionParser()
    block_builder = LogicalBlockBuilder()

    # Dynamic target language selection based on book metadata
    book_lang = book_metadata.get("language", "english")
    ocr_lang = "tam" if book_lang == "tamil" else "eng"
    if book_metadata.get("content_type") == "guide":
        # Guides can contain mixed languages for bilingual explanations
        ocr_lang = "eng+tam"

    # Iterate through pages
    for page_idx, page in enumerate(doc):
        # Skip blank pages
        if cleaner.is_blank_page(page):
            continue
            
        # 1. Searchable check
        is_searchable = analyzer.is_page_searchable(page)
        
        page_text_blocks = []
        
        if is_searchable:
            # Extract text elements and clean them using geometry thresholds
            page_text_blocks = cleaner.clean_page_text_blocks(page)
        else:
            # OCR Pipeline: Run PaddleOCR/Tesseract on page segments
            ocr_used = True
            page_rect = page.rect
            # Segment the full page into reading blocks using CPU/GPU layout analysis
            layout_blocks = analyzer.segment_page(page, [], temp_img_path=None)
            
            for l_block in layout_blocks:
                # Perform OCR on each block bounding box
                text, conf = ocr.perform_ocr_on_bbox(page, l_block.bbox, lang=ocr_lang)
                if text.strip():
                    page_text_blocks.append({
                        "bbox": l_block.bbox,
                        "text": text,
                        "bbox_type": l_block.type
                    })
        
        # 2. Extract Figures and Tables (Multimodal Roadmap)
        try:
            figures_and_tables = cleaner.extract_figures_and_tables(page, page_idx + 1)
            for item in figures_and_tables:
                if item["type"] == "table":
                    table_text = f"[Table Reference (Page {page_idx+1})]\n\n{item['content']}"
                    chunk_metadata = {
                        **book_metadata,
                        "page_number": page_idx + 1,
                        "chapter_no": "0",
                        "chapter_title": "Tables and Diagrams",
                        "ocr_processed": not is_searchable,
                        "content_role": "table",
                        "bbox": list(item["bbox"]),
                        "source": book_metadata.get("content_type", "textbook")
                    }
                    all_chunks.append(ChunkUnit(
                        chunk_id=f"{book_metadata.get('document_id', 'unknown')}_tbl_{page_idx+1}_{len(all_chunks)}",
                        text=table_text,
                        metadata=chunk_metadata
                    ))
                elif item["type"] == "figure":
                    fig_ocr_text, _ = ocr.perform_ocr_on_bbox(page, item["bbox"], lang=ocr_lang)
                    fig_text = f"[Figure Reference (Page {page_idx+1}) Caption: {item['caption']}]\n[Diagram Text: {fig_ocr_text}]"
                    chunk_metadata = {
                        **book_metadata,
                        "page_number": page_idx + 1,
                        "chapter_no": "0",
                        "chapter_title": "Tables and Diagrams",
                        "ocr_processed": True,
                        "content_role": "figure",
                        "bbox": list(item["bbox"]),
                        "image_path": item["image_path"],
                        "source": book_metadata.get("content_type", "textbook")
                    }
                    all_chunks.append(ChunkUnit(
                        chunk_id=f"{book_metadata.get('document_id', 'unknown')}_fig_{page_idx+1}_{len(all_chunks)}",
                        text=fig_text,
                        metadata=chunk_metadata
                    ))
        except Exception as e:
            print(f"⚠️ Warning: Failed to extract tables/figures on Page {page_idx+1}: {e}")

        if not page_text_blocks:
            continue
            
        # 3. Layout Analysis (Column sorting & reading order resolution)
        sorted_layout_blocks = analyzer.segment_page(page, page_text_blocks)
        
        # 4. Chapter & Section parsing
        chapters = chapter_parser.split_by_chapters(sorted_layout_blocks)
        
        # 5. Logical Block & Contextual Chunking
        for chap in chapters:
            chap_no = chap["chapter_no"]
            chap_title = chap["chapter_title"]
            
            # Map sections
            section_mapped = section_parser.build_section_hierarchy(chap["blocks"])
            # Form concepts
            logical_blocks = block_builder.build_logical_blocks(section_mapped)
            
            # Construct final context-aware chunks
            if book_metadata.get("content_type") == "guide":
                raw_text = "\n\n".join(b.text for b in logical_blocks)
                page_chunks = chunker.chunk_guide_qa(raw_text, book_metadata)
            else:
                page_chunks = chunker.chunk_textbook_blocks(logical_blocks, book_metadata)
                
            # Add metadata details and validate each chunk
            for chunk in page_chunks:
                # Inject page metadata
                chunk.metadata["page_number"] = page_idx + 1
                chunk.metadata["chapter_no"] = chap_no
                chunk.metadata["chapter_title"] = chap_title
                chunk.metadata["ocr_processed"] = not is_searchable
                chunk.metadata["source"] = book_metadata.get("content_type", "textbook")
                
                is_valid, reason = validator.validate_chunk(chunk.text, chunk.metadata)
                if is_valid:
                    all_chunks.append(chunk)
                else:
                    print(f"⚠️ Skipping invalid chunk on Page {page_idx+1}: {reason}")

    return all_chunks, ocr_used

def compile_indices(data_root: str, registry_path: str):
    print("⏳ Compiling unified indices from registry...")
    if not os.path.exists(registry_path):
        print("⚠️ No registry manifest found. Cannot compile.")
        return

    with open(registry_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    documents = manifest.get("documents", {})
    
    en_chunks = []
    en_embeddings_list = []
    ta_chunks = []
    ta_embeddings_list = []

    for file_hash, doc in documents.items():
        if doc.get("indexed_status") != "indexed":
            continue

        rel_path = doc.get("file_path")
        clean_rel_path = rel_path.replace(".pdf", "")
        
        chunks_file = os.path.join(data_root, "processed", "chunks", f"{clean_rel_path}_chunks.json")
        embeds_file = os.path.join(data_root, "processed", "embeddings", f"{clean_rel_path}_embeddings.npy")

        if not os.path.exists(chunks_file) or not os.path.exists(embeds_file):
            print(f"⚠️ Chunks/embeddings missing for {rel_path}, skipping compilation.")
            continue

        with open(chunks_file, "r", encoding="utf-8") as f:
            file_chunks = json.load(f)
        
        file_embeds = np.load(embeds_file)

        if len(file_chunks) != len(file_embeds):
            print(f"⚠️ Chunk and embedding count mismatch for {rel_path}, skipping.")
            continue

        medium = doc.get("medium")
        if medium == "english":
            en_chunks.extend(file_chunks)
            en_embeddings_list.append(file_embeds)
        elif medium == "tamil":
            ta_chunks.extend(file_chunks)
            ta_embeddings_list.append(file_embeds)

    cache_dir = os.path.join(data_root, "processed", "cache")
    os.makedirs(cache_dir, exist_ok=True)

    # Standardize output dimensions to 768 (GTE Multilingual size)
    # Save English Cache
    en_chunks_path = os.path.join(cache_dir, "english_chunks.pkl")
    en_embeddings_path = os.path.join(cache_dir, "english_embeddings.npy")
    if en_embeddings_list:
        en_embeddings = np.vstack(en_embeddings_list)
        with open(en_chunks_path, "wb") as f:
            pickle.dump(en_chunks, f)
        np.save(en_embeddings_path, en_embeddings)
        print(f"✅ Saved English Cache: {len(en_chunks)} chunks, shape: {en_embeddings.shape}")
    else:
        with open(en_chunks_path, "wb") as f:
            pickle.dump([], f)
        np.save(en_embeddings_path, np.empty((0, 768)))

    # Save Tamil Cache
    ta_chunks_path = os.path.join(cache_dir, "tamil_chunks.pkl")
    ta_embeddings_path = os.path.join(cache_dir, "tamil_embeddings.npy")
    if ta_embeddings_list:
        ta_embeddings = np.vstack(ta_embeddings_list)
        with open(ta_chunks_path, "wb") as f:
            pickle.dump(ta_chunks, f)
        np.save(ta_embeddings_path, ta_embeddings)
        print(f"✅ Saved Tamil Cache: {len(ta_chunks)} chunks, shape: {ta_embeddings.shape}")
    else:
        with open(ta_chunks_path, "wb") as f:
            pickle.dump([], f)
        np.save(ta_embeddings_path, np.empty((0, 768)))

    # Compile and serialize BM25 indices offline
    from app.retrieval.hybrid_retriever import SimpleBM25
    bm25_indices = {
        "en": SimpleBM25([c["text"] for c in en_chunks]) if en_chunks else SimpleBM25([]),
        "ta": SimpleBM25([c["text"] for c in ta_chunks]) if ta_chunks else SimpleBM25([])
    }
    bm25_index_path = os.path.join(cache_dir, "bm25_index.pkl")
    with open(bm25_index_path, "wb") as f:
        pickle.dump(bm25_indices, f)
    print(f"✅ Saved BM25 Indices: English {len(en_chunks)} docs, Tamil {len(ta_chunks)} docs to {bm25_index_path}")

def main():
    parser = argparse.ArgumentParser(description="Production-Grade Ingestion and indexing pipeline for TamilEdu-SLM.")
    parser.add_argument("--class-level", type=int, choices=[6, 7, 8], help="Target class level to index")
    parser.add_argument("--all", action="store_true", help="Index all new/modified books")
    parser.add_argument("--reindex-changed", action="store_true", help="Force rebuild changed books")
    args = parser.parse_args()

    # Startup Dependency Check
    log_ocr_status()

    # Paths Setup
    data_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data"))
    os.makedirs(data_root, exist_ok=True)
    registry_dir = os.path.join(data_root, "registry")
    os.makedirs(registry_dir, exist_ok=True)
    registry_path = os.path.join(registry_dir, "manifest.json")
    
    scanner = BookScanner(data_root, registry_path)
    try:
        scan_summary = scanner.scan()
    except FileNotFoundError as e:
        print(f"❌ Error during scanning: {e}")
        sys.exit(1)
    
    print(f"📊 Scan Complete. New: {len(scan_summary.new_files)}, Modified: {len(scan_summary.modified_files)}, Invalid: {len(scan_summary.invalid_files)}")

    to_process = []
    if args.all or args.reindex_changed:
        to_process.extend(scan_summary.new_files)
        to_process.extend(scan_summary.modified_files)
    elif args.class_level:
        to_process.extend([f for f in scan_summary.new_files if f.class_level == args.class_level])
        to_process.extend([f for f in scan_summary.modified_files if f.class_level == args.class_level])
    else:
        print("⚠️ Specify --all or --class-level to process files.")
        compile_indices(data_root, registry_path)
        sys.exit(0)

    if not to_process:
        print("✅ Nothing to process. All indices match manifest hashes.")
        compile_indices(data_root, registry_path)
        # Trigger out-of-band evaluation after build check
        try:
            from app.evaluation.evaluator import run_auto_evaluation
            run_auto_evaluation()
        except ImportError:
            pass
        sys.exit(0)

    # Initialize Ingestion Processing Components
    print("⏳ Loading Pipeline Engines...")
    cleaner = PDFCleaner(output_img_dir=os.path.join(data_root, "processed", "images"))
    analyzer = LayoutAnalyzer()
    ocr = OCRCleaner()
    validator = ChunkValidator()
    chunker = ScienceChunker()

    # Initialize GTE Multilingual base model for both Tamil and English embeddings
    print("⏳ Loading Embedding Model (Alibaba-NLP/gte-multilingual-base)...")
    hw_level = get_hardware_level()
    device = "cuda" if hw_level == "LEVEL_2_GPU" else "cpu"
    embed_model = SentenceTransformer('Alibaba-NLP/gte-multilingual-base', device=device, trust_remote_code=True)
    
    # Fix corrupted position_ids buffer in GTE Multilingual model on CPU/Windows
    try:
        import torch
        embeddings_module = embed_model[0].auto_model.embeddings
        if hasattr(embeddings_module, "position_ids"):
            device = embeddings_module.position_ids.device
            correct_pos_ids = torch.arange(embeddings_module.position_ids.size(0), dtype=torch.long, device=device)
            embeddings_module.position_ids.copy_(correct_pos_ids)
            print("🔧 Successfully patched GTE Multilingual position_ids buffer!")
    except Exception as e:
        print(f"⚠️ Failed to patch GTE Multilingual position_ids: {e}")

    manifest = scanner.load_manifest()

    for book in to_process:
        full_pdf_path = os.path.join(data_root, book.relative_path)
        print(f"📄 Processing: {book.filename}...")
        
        try:
            # Run Ingestion Pipeline
            chunks, ocr_used = process_book_pipeline(
                full_pdf_path, book.model_dump(), cleaner, analyzer, ocr, validator, chunker
            )
            
            if not chunks:
                print(f"⚠️ No chunks extracted from {book.filename}")
                continue

            # Embed chunks using the GTE Multilingual model
            texts_to_embed = [c.text for c in chunks]
            embeddings = embed_model.encode(texts_to_embed, normalize_embeddings=True)

            # Save processed files
            clean_rel_path = book.relative_path.replace(".pdf", "")
            chunks_dir = os.path.join(data_root, "processed", "chunks", os.path.dirname(clean_rel_path))
            embeds_dir = os.path.join(data_root, "processed", "embeddings", os.path.dirname(clean_rel_path))
            
            os.makedirs(chunks_dir, exist_ok=True)
            os.makedirs(embeds_dir, exist_ok=True)
            
            chunks_file = os.path.join(chunks_dir, f"{os.path.basename(clean_rel_path)}_chunks.json")
            embeds_file = os.path.join(embeds_dir, f"{os.path.basename(clean_rel_path)}_embeddings.npy")
            
            with open(chunks_file, "w", encoding="utf-8") as f:
                json.dump([c.model_dump() for c in chunks], f, ensure_ascii=False, indent=2)
            np.save(embeds_file, embeddings)

            # Update Manifest Registry
            file_hash = scanner.get_file_sha256(full_pdf_path)
            manifest["documents"][file_hash] = {
                "document_id": file_hash,
                "file_path": book.relative_path,
                "filename": book.filename,
                "file_hash": file_hash,
                "modified_time": datetime.fromtimestamp(os.path.getmtime(full_pdf_path)).isoformat(),
                "class_level": book.class_level,
                "subject": book.subject,
                "language": book.language,
                "medium": book.medium,
                "content_type": book.content_type,
                "term": book.term,
                "year": book.year,
                "indexed_status": "indexed",
                "last_indexed_timestamp": datetime.utcnow().isoformat(),
                "chunk_count": len(chunks),
                "embedding_status": "completed",
                "ocr_used": ocr_used,
                "errors": None
            }
            
            print(f"✅ Indexed {len(chunks)} chunks for {book.filename}")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"❌ Failed to index {book.filename}: {str(e)}")
            file_hash = scanner.get_file_sha256(full_pdf_path)
            manifest["documents"][file_hash] = {
                "file_path": book.relative_path,
                "filename": book.filename,
                "file_hash": file_hash,
                "indexed_status": "failed",
                "errors": str(e)
            }

    # Write back manifest
    manifest["last_updated"] = datetime.utcnow().isoformat()
    manifest["total_documents"] = len(manifest["documents"])
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print("💾 Manifest registry updated.")
    
    # Run compiler
    compile_indices(data_root, registry_path)

    # Trigger out-of-band evaluation suite
    try:
        from app.evaluation.evaluator import run_auto_evaluation
        run_auto_evaluation()
    except Exception as e:
        print(f"⚠️ Auto-evaluation trigger failed: {str(e)}")

if __name__ == "__main__":
    main()
