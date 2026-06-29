import os
import json
import pickle
import numpy as np
import sys
from datetime import datetime

# Set UTF-8 encoding for stdout/stderr to prevent charmap encoding errors under Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# Set path and import SimpleBM25
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.retrieval.hybrid_retriever import SimpleBM25

def compile_offline():
    data_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data"))
    chunks_base_dir = os.path.join(data_root, "processed", "chunks")
    embeds_base_dir = os.path.join(data_root, "processed", "embeddings")
    cache_dir = os.path.join(data_root, "processed", "cache")
    registry_dir = os.path.join(data_root, "registry")
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(registry_dir, exist_ok=True)

    en_chunks = []
    en_embeddings_list = []
    ta_chunks = []
    ta_embeddings_list = []

    documents_manifest = {}
    embed_model = None

    # Traverse processed chunks
    for root, dirs, files in os.walk(chunks_base_dir):
        for file in files:
            if not file.endswith("_chunks.json"):
                continue
            
            # Paths
            chunks_file = os.path.join(root, file)
            rel_path = os.path.relpath(chunks_file, chunks_base_dir)
            clean_rel_path = rel_path.replace("_chunks.json", "")
            
            embeds_file = os.path.join(embeds_base_dir, clean_rel_path + "_embeddings.npy")
            if not os.path.exists(embeds_file):
                print(f"⚠️ Embeddings missing for {chunks_file}, looking for {embeds_file}")
                continue

            with open(chunks_file, "r", encoding="utf-8") as f:
                file_chunks = json.load(f)
            file_embeds = np.load(embeds_file)

            if len(file_embeds) > 0 and (file_embeds.ndim < 2 or file_embeds.shape[1] != 768):
                print(f"⚠️ Dimension mismatch in {file} (got {file_embeds.shape[1] if file_embeds.ndim > 1 else '1D'}, expected 768). Re-generating on-the-fly...")
                if embed_model is None:
                    print("⏳ Loading GTE Multilingual model...")
                    from sentence_transformers import SentenceTransformer
                    embed_model = SentenceTransformer('Alibaba-NLP/gte-multilingual-base', device='cpu', trust_remote_code=True)
                    try:
                        import torch
                        embeddings_module = embed_model[0].auto_model.embeddings
                        if hasattr(embeddings_module, "position_ids"):
                            correct_pos_ids = torch.arange(embeddings_module.position_ids.size(0), dtype=torch.long, device=embeddings_module.position_ids.device)
                            embeddings_module.position_ids.copy_(correct_pos_ids)
                            print("🔧 Successfully patched GTE Multilingual position_ids buffer!")
                    except Exception as e:
                        print(f"⚠️ Failed to patch: {e}")
                
                texts = [c["text"] for c in file_chunks]
                file_embeds = embed_model.encode(texts, normalize_embeddings=True)
                np.save(embeds_file, file_embeds)
                print(f"💾 Saved corrected embeddings to {embeds_file}")

            if len(file_chunks) != len(file_embeds):
                print(f"⚠️ Mismatch for {chunks_file} (chunks: {len(file_chunks)}, embeds: {len(file_embeds)})")
                continue

            # Determine medium / language
            # Determine based on path
            path_lower = chunks_file.lower()
            medium = "tamil" if "tamil" in path_lower or "_ta_" in path_lower else "english"

            if medium == "english":
                en_chunks.extend(file_chunks)
                en_embeddings_list.append(file_embeds)
            else:
                ta_chunks.extend(file_chunks)
                ta_embeddings_list.append(file_embeds)

            # Build fake manifest entry
            doc_id = "doc_" + file.replace("_chunks.json", "")
            documents_manifest[doc_id] = {
                "document_id": doc_id,
                "file_path": f"books/{clean_rel_path}.pdf",
                "filename": f"{clean_rel_path.split(os.sep)[-1]}.pdf",
                "file_hash": doc_id,
                "modified_time": datetime.utcnow().isoformat(),
                "class_level": 6,
                "subject": "science",
                "language": "en" if medium == "english" else "ta",
                "medium": medium,
                "content_type": "textbook",
                "term": 1,
                "year": 2024,
                "indexed_status": "indexed",
                "last_indexed_timestamp": datetime.utcnow().isoformat(),
                "chunk_count": len(file_chunks),
                "embedding_status": "completed",
                "ocr_used": False,
                "errors": None
            }
            print(f"[FOUND] {len(file_chunks)} chunks for {file} ({medium})")

    # Save aggregated caches
    en_chunks_path = os.path.join(cache_dir, "english_chunks.pkl")
    en_embeddings_path = os.path.join(cache_dir, "english_embeddings.npy")
    if en_embeddings_list:
        en_embeddings = np.vstack(en_embeddings_list)
        with open(en_chunks_path, "wb") as f:
            pickle.dump(en_chunks, f)
        np.save(en_embeddings_path, en_embeddings)
        print(f"💾 Saved English unified cache. Chunks: {len(en_chunks)}, Embeddings: {en_embeddings.shape}")
    else:
        print("⚠️ No English chunks found!")

    ta_chunks_path = os.path.join(cache_dir, "tamil_chunks.pkl")
    ta_embeddings_path = os.path.join(cache_dir, "tamil_embeddings.npy")
    if ta_embeddings_list:
        ta_embeddings = np.vstack(ta_embeddings_list)
        with open(ta_chunks_path, "wb") as f:
            pickle.dump(ta_chunks, f)
        np.save(ta_embeddings_path, ta_embeddings)
        print(f"💾 Saved Tamil unified cache. Chunks: {len(ta_chunks)}, Embeddings: {ta_embeddings.shape}")
    else:
        print("⚠️ No Tamil chunks found!")

    # Compute and save BM25 offline matrices
    print("⏳ Building offline BM25 matrices...")
    bm25_indices = {
        "en": SimpleBM25([c["text"] for c in en_chunks]) if en_chunks else SimpleBM25([]),
        "ta": SimpleBM25([c["text"] for c in ta_chunks]) if ta_chunks else SimpleBM25([])
    }
    bm25_path = os.path.join(cache_dir, "bm25_index.pkl")
    with open(bm25_path, "wb") as f:
        pickle.dump(bm25_indices, f)
    print(f"💾 Saved BM25 Indices Cache to {bm25_path}")

    # Save manifest registry
    manifest = {
        "documents": documents_manifest,
        "last_updated": datetime.utcnow().isoformat(),
        "total_documents": len(documents_manifest)
    }
    registry_path = os.path.join(registry_dir, "manifest.json")
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"💾 Manifest registry saved to {registry_path}")

if __name__ == "__main__":
    compile_offline()
