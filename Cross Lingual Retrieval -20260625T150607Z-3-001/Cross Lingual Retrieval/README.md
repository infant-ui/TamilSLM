# 🔬 Cross-lingual Science RAG — Fully Offline Edition

Ask science questions in **English or Tamil** — answered by a **local Phi3 model via Ollama**.  
No API key, no internet required after the one-time setup.

---

## Stack

| Component | Technology |
|---|---|
| LLM | Phi3 via [Ollama](https://ollama.com) (local) |
| Embeddings | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (local) |
| Vector search | FAISS (CPU) |
| Translation | `argostranslate` (local, offline after one-time download) |
| Language detection | `langdetect` |
| UI | Gradio |

---

## Setup

### 1 — Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2 — Install & start Ollama

```bash
# Install Ollama (Linux/macOS)
curl -fsSL https://ollama.com/install.sh | sh

# Pull phi3 (one-time, ~2 GB)
ollama pull phi3

# Start the Ollama server (keep this running in a terminal)
ollama serve
```

### 3 — Install offline translation models (one-time)

This only needs the internet **once** to download the translation packages (~100 MB).  
After this step, all translation is 100% offline.

```bash
python -c "from translator import install_language_packages; install_language_packages()"
```

### 4 — Add your documents

- PDFs → `data/pdfs/`
- Plain text → `data/texts/`

A sample Tamil science text is already in `data/texts/`.

### 5 — Build the FAISS index

```bash
python build_index.py
```

### 6 — Launch the web UI

```bash
python app.py
# Open http://localhost:7860
```

Or use the CLI:

```bash
python query_cli.py "What is photosynthesis?"
python query_cli.py "ஒளிச்சேர்க்கை என்றால் என்ன?"
python query_cli.py --interactive
```

---

## Using a different local model

Edit `rag_pipeline.py` and change:

```python
OLLAMA_MODEL = "phi3"   # change to e.g. "mistral", "llama3", "gemma"
```

Any model you have pulled with `ollama pull <name>` will work.

---

## How cross-lingual retrieval works

1. Your query is detected as **English or Tamil** (langdetect).
2. If Tamil → translated to English offline (argostranslate) for retrieval.
3. Top-K semantically similar chunks are retrieved from the FAISS index.  
   The multilingual embedding model maps Tamil & English to the same vector space,
   so Tamil queries naturally find English documents.
4. Phi3 generates an answer in English using the retrieved context.
5. If the original query was Tamil → the answer is translated back to Tamil offline.

---

## File structure

```
rag_project/
├── app.py              ← Gradio web UI
├── query_cli.py        ← CLI interface
├── rag_pipeline.py     ← RAG orchestration (uses Ollama)
├── embedder.py         ← FAISS index build & retrieval
├── document_loader.py  ← PDF & text chunking
├── translator.py       ← Offline Tamil<->English (argostranslate)
├── build_index.py      ← One-time index builder
├── requirements.txt
├── data/
│   ├── pdfs/           ← Put your PDFs here
│   └── texts/          ← Put your .txt files here
├── embeddings/         ← Auto-created by build_index.py
└── outputs/            ← Auto-created, stores Q&A sessions as JSON
```
