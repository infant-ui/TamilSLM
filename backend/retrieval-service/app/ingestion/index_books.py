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
from app.ingestion.encoder_utils import load_patched_encoder, self_retrieval_gate

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
    # Phase 1 fix: chunk_id is derived from this document_id. It must be the
    # real file hash, set by the caller BEFORE this function runs -- never a
    # placeholder. (Previously book_metadata had no "document_id" key at all
    # at this point in the pipeline, so every chunk silently fell back to the
    # literal string "unknown", producing ids like "unknown_tb_0" that were
    # NOT unique even within a single document, let alone across the corpus:
    # chunk_count in CurriculumChunker.chunk_textbook_blocks/chunk_guide_qa is
    # scoped to a single call, and that function is called once PER CHAPTER,
    # so "unknown_tb_0" was reused by chapter 1's first chunk, chapter 2's
    # first chunk, etc., in addition to colliding across every other book.
    # Measured impact on the live cache this replaces: 3,583 English chunks
    # shared only 555 distinct chunk_ids, 1,856 of them "unknown_tb_0".)
    doc_id = book_metadata.get("document_id")
    if not doc_id:
        raise ValueError(
            f"book_metadata is missing 'document_id' for {pdf_path} -- refusing to ingest with a "
            f"placeholder chunk_id. Compute the file hash and set book_metadata['document_id'] "
            f"before calling process_book_pipeline()."
        )

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

        # Phase 1 fix: one running counter per page, shared across table,
        # figure, and text/guide chunks created for THIS page, so the final
        # chunk_id (assigned below as f"{doc_id}_{page_number}_{counter}")
        # is guaranteed unique within the document regardless of how many
        # chapters or content types land on the same page.
        page_chunk_idx = 0

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
                        chunk_id=f"{doc_id}_{page_idx+1}_{page_chunk_idx}",
                        text=table_text,
                        metadata=chunk_metadata
                    ))
                    page_chunk_idx += 1
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
                        chunk_id=f"{doc_id}_{page_idx+1}_{page_chunk_idx}",
                        text=fig_text,
                        metadata=chunk_metadata
                    ))
                    page_chunk_idx += 1
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
                chunk.metadata["document_id"] = doc_id

                is_valid, reason = validator.validate_chunk(chunk.text, chunk.metadata)
                if is_valid:
                    # Phase 1 fix: override whatever placeholder id the chunker assigned
                    # (chunk_count there resets per-chapter, see comment above) with the
                    # real scheme: book_id (file hash) + page number + a counter that is
                    # unique across the whole page, shared with table/figure chunks.
                    chunk.chunk_id = f"{doc_id}_{page_idx+1}_{page_chunk_idx}"
                    page_chunk_idx += 1
                    all_chunks.append(chunk)
                else:
                    print(f"⚠️ Skipping invalid chunk on Page {page_idx+1}: {reason}")

    chunk_ids = [c.chunk_id for c in all_chunks]
    assert len(set(chunk_ids)) == len(chunk_ids), (
        f"Duplicate chunk_id(s) produced for {pdf_path} (doc_id={doc_id}): "
        f"{len(chunk_ids)} chunks, {len(set(chunk_ids))} unique ids. This must never happen -- "
        f"refusing to return a corpus with colliding chunk identities."
    )
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

    # Phase 1 promotion gate: a corpus with colliding chunk_ids must never reach the
    # live cache. hybrid_retriever.py's RRF fusion and chunk_map are keyed by chunk_id,
    # so a collision here silently collapses distinct chunks into one another --
    # this is the root cause that was previously measured to make the hybrid
    # pipeline score near zero while plain BM25 (which never keys by chunk_id)
    # scored normally. Fail loudly and refuse to write the cache rather than
    # silently shipping a broken index.
    for label, chunk_list in (("english", en_chunks), ("tamil", ta_chunks)):
        ids = [c["chunk_id"] for c in chunk_list]
        if len(set(ids)) != len(ids):
            dupes = {i: c for i, c in __import__("collections").Counter(ids).items() if c > 1}
            raise AssertionError(
                f"Refusing to write {label} cache: {len(ids)} chunks but only {len(set(ids))} "
                f"unique chunk_ids. Top duplicates: {sorted(dupes.items(), key=lambda kv: -kv[1])[:5]}"
            )

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

def run_self_retrieval_gate_on_cache(data_root: str, device: str = "cpu") -> dict:
    """
    Loads the compiled cache (data/processed/cache/*) plus a fresh, freshly-patched
    encoder, and runs the Phase 1 mandatory promotion gate against both languages.
    Returns {"english": {...}, "tamil": {...}, "passed": bool}.
    """
    cache_dir = os.path.join(data_root, "processed", "cache")
    encoder = load_patched_encoder(device)
    result = {"passed": True}
    for lang_key, chunks_fname, emb_fname in [("english", "english_chunks.pkl", "english_embeddings.npy"),
                                               ("tamil", "tamil_chunks.pkl", "tamil_embeddings.npy")]:
        with open(os.path.join(cache_dir, chunks_fname), "rb") as f:
            chunks = pickle.load(f)
        embeddings = np.load(os.path.join(cache_dir, emb_fname))
        gate = self_retrieval_gate(chunks, embeddings, encoder, sample_size=150, label=lang_key)
        result[lang_key] = gate
        result["passed"] = result["passed"] and gate["passed"]
        status = "PASSED" if gate["passed"] else "FAILED"
        print(f"[self-retrieval gate] {lang_key}: {status} -- pass_rate={gate['pass_rate']:.3f}, "
              f"own_cosine_min={gate['own_cosine_min']:.4f}, rank_mean={gate['rank_mean']:.1f}, "
              f"n_rank1={gate['n_rank1']}/{gate['n_sampled']}")
    return result


def rebuild_existing_corpus(data_root: str, registry_path: str, device: str = "cpu") -> dict:
    """
    Phase 1 migration path: fixes chunk_ids and re-embeds the ALREADY-EXTRACTED
    per-book chunk JSON files (data/processed/chunks/**/*_chunks.json) without
    re-running PDF extraction/OCR (which is unchanged by this fix and expensive
    to redo). For each book already in the manifest:
      1. Reassigns every chunk_id using the real scheme (document_id = the
         manifest's file hash for that book, grouped by page_number, with a
         per-page running index) -- replacing the "unknown_tb_N" placeholders.
      2. Backfills metadata["document_id"], which was previously absent entirely.
      3. Re-embeds all chunk texts with the Phase 1 patched encoder (position_ids
         arange + rotary buffers zeroed) and overwrites the per-book embeddings file.
    Then calls compile_indices() to rebuild the merged cache (which now also
    enforces the global chunk_id-uniqueness gate before writing), and runs the
    mandatory self-retrieval gate against the rebuilt cache. Returns a dict
    with 'gate' (self_retrieval_gate result) for the caller to act on; the
    caller must not consider the new cache production-ready unless
    gate['passed'] is True.
    """
    with open(registry_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    documents = manifest.get("documents", {})

    print(f"⏳ Loading Embedding Model (Phase 1 patched) on {device}...")
    embed_model = load_patched_encoder(device)

    rebuilt, skipped = 0, 0
    for file_hash, doc in documents.items():
        if doc.get("indexed_status") != "indexed":
            continue
        rel_path = doc.get("file_path")
        clean_rel_path = rel_path.replace(".pdf", "")
        chunks_file = os.path.join(data_root, "processed", "chunks", f"{clean_rel_path}_chunks.json")
        embeds_file = os.path.join(data_root, "processed", "embeddings", f"{clean_rel_path}_embeddings.npy")
        if not os.path.exists(chunks_file):
            print(f"⚠️ No chunk file for {rel_path}, skipping.")
            skipped += 1
            continue

        with open(chunks_file, "r", encoding="utf-8") as f:
            file_chunks = json.load(f)
        if not file_chunks:
            skipped += 1
            continue

        # Reassign chunk_id. Chunks are already in page order (each book was
        # processed page-by-page by process_book_pipeline), so grouping by
        # page_number and counting within each group reproduces exactly what
        # the fixed process_book_pipeline would assign on a fresh run.
        page_counters: dict = {}
        for c in file_chunks:
            pg = c["metadata"]["page_number"]
            idx_on_page = page_counters.get(pg, 0)
            c["chunk_id"] = f"{file_hash}_{pg}_{idx_on_page}"
            c["metadata"]["document_id"] = file_hash
            page_counters[pg] = idx_on_page + 1

        ids = [c["chunk_id"] for c in file_chunks]
        assert len(set(ids)) == len(ids), f"Duplicate chunk_id after reassignment in {rel_path}"

        with open(chunks_file, "w", encoding="utf-8") as f:
            json.dump(file_chunks, f, ensure_ascii=False, indent=2)

        texts = [c["text"] for c in file_chunks]
        embeddings = embed_model.encode(texts, normalize_embeddings=True, batch_size=16)
        np.save(embeds_file, embeddings)

        rebuilt += 1
        print(f"✅ Rebuilt {len(file_chunks)} chunks for {rel_path} ({rebuilt} done, {skipped} skipped)")

    print(f"⏳ Recompiling merged cache from {rebuilt} rebuilt book(s)...")
    compile_indices(data_root, registry_path)

    print("⏳ Running mandatory self-retrieval promotion gate...")
    gate = run_self_retrieval_gate_on_cache(data_root, device)
    if not gate["passed"]:
        print("❌ SELF-RETRIEVAL GATE FAILED. The rebuilt cache is NOT safe to treat as production: "
              "fix the encoder/embedding pipeline and re-run --rebuild-cache before trusting these results.")
    else:
        print("✅ Self-retrieval gate passed. Rebuilt cache is self-consistent.")
    return {"rebuilt": rebuilt, "skipped": skipped, "gate": gate}


def main():
    parser = argparse.ArgumentParser(description="Production-Grade Ingestion and indexing pipeline for TamilEdu-SLM.")
    parser.add_argument("--class-level", type=int, choices=[6, 7, 8], help="Target class level to index")
    parser.add_argument("--all", action="store_true", help="Index all new/modified books")
    parser.add_argument("--reindex-changed", action="store_true", help="Force rebuild changed books")
    parser.add_argument("--rebuild-cache", action="store_true",
                         help="Phase 1 migration: fix chunk_ids and re-embed already-extracted chunks "
                              "(data/processed/chunks/**) without re-running PDF extraction/OCR, then "
                              "recompile the cache and run the mandatory self-retrieval gate.")
    args = parser.parse_args()

    # Startup Dependency Check
    log_ocr_status()

    # Paths Setup
    data_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data"))
    os.makedirs(data_root, exist_ok=True)
    registry_dir = os.path.join(data_root, "registry")
    os.makedirs(registry_dir, exist_ok=True)
    registry_path = os.path.join(registry_dir, "manifest.json")

    if args.rebuild_cache:
        hw_level = get_hardware_level()
        device = "cuda" if hw_level == "LEVEL_2_GPU" else "cpu"
        result = rebuild_existing_corpus(data_root, registry_path, device)
        sys.exit(0 if result["gate"]["passed"] else 1)

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
    # (Phase 1: shared loader -- see encoder_utils.py for exactly what's patched and why.)
    print("⏳ Loading Embedding Model (Alibaba-NLP/gte-multilingual-base)...")
    hw_level = get_hardware_level()
    device = "cuda" if hw_level == "LEVEL_2_GPU" else "cpu"
    embed_model = load_patched_encoder(device)

    manifest = scanner.load_manifest()

    for book in to_process:
        full_pdf_path = os.path.join(data_root, book.relative_path)
        print(f"📄 Processing: {book.filename}...")

        # Phase 1 fix: compute the real document_id (file hash) BEFORE chunking, and
        # inject it into the metadata dict passed to process_book_pipeline, so every
        # chunk_id generated during this run is built from the real hash -- never the
        # "unknown" placeholder (see process_book_pipeline's docstring comment).
        file_hash = scanner.get_file_sha256(full_pdf_path)
        book_dict = book.model_dump()
        book_dict["document_id"] = file_hash

        try:
            # Run Ingestion Pipeline
            chunks, ocr_used = process_book_pipeline(
                full_pdf_path, book_dict, cleaner, analyzer, ocr, validator, chunker
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

            # Update Manifest Registry (file_hash computed once, above, before chunking)
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

    # Phase 1 mandatory promotion gate (see encoder_utils.self_retrieval_gate docstring)
    gate = run_self_retrieval_gate_on_cache(data_root, device)
    if not gate["passed"]:
        print("❌ SELF-RETRIEVAL GATE FAILED after full ingestion run -- investigate before trusting this cache.")

    # Trigger out-of-band evaluation suite
    try:
        from app.evaluation.evaluator import run_auto_evaluation
        run_auto_evaluation()
    except Exception as e:
        print(f"⚠️ Auto-evaluation trigger failed: {str(e)}")

if __name__ == "__main__":
    main()
