# Research

Experiments and reference material, renamed from the Google Drive export folders (`...-20260625T...-3-001`).

| Folder | Contents |
|---|---|
| `cross-lingual-retrieval/` | Cross-lingual retrieval experiments: PDFs, scripts, a FAISS index and metadata |
| `embedding/` | Tamil and English BERT embeddings, tokenizer, plots, scripts |
| `mindmap/` | Mind-map prediction scripts and models. **`backend/gateway` runs `research/mindmap/predict_json.py`**; keep the path stable |
| `papers/` | Reference papers (PDF) |
| `architecture/` | Architecture diagram sources |

Existing large binaries are still plain blobs except PDFs (LFS). New `.npy`, FAISS `.index`, `.pkl` and `.zip` files under `research/` go to Git LFS (see `.gitattributes`); run `git lfs pull` after cloning.
