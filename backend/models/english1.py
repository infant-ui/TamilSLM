import sys
import os

# Set UTF-8 encoding for stdout/stderr to prevent charmap encoding errors under Windows/exec
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def log(*args, **kwargs):
    # Print to stderr if running as backend child process to keep stdout clean for the final answer
    if len(sys.argv) > 1:
        print(*args, file=sys.stderr, **kwargs)
    else:
        print(*args, **kwargs)

log("🚀 Python script started")
log("Arguments:", sys.argv)
# =======================
# LOW MEMORY SETTINGS
# =======================
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

# =======================
# IMPORTS
# =======================
import sys
import fitz
import nltk
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# =======================
# LOAD MODEL (ONLY ONCE)
# =======================
log("Loading model...", flush=True)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# =======================
# PDF PATH (CHANGE THIS)
# =======================
pdf_path = os.path.join(os.path.dirname(__file__), "science_english.pdf")

# =======================
# FUNCTIONS
# =======================
def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text")
    return text

def split_chunks(text, chunk_size=300):
    sentences = text.split(". ")
    chunks = []
    chunk = ""

    for s in sentences:
        if len(chunk) + len(s) < chunk_size:
            chunk += " " + s
        else:
            chunks.append(chunk.strip())
            chunk = s

    if chunk:
        chunks.append(chunk.strip())

    return chunks

import pickle

# =======================
# PREPROCESS (WITH CACHE)
# =======================
cache_dir = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(cache_dir, exist_ok=True)
chunks_cache = os.path.join(cache_dir, "english_chunks.pkl")
embeddings_cache = os.path.join(cache_dir, "english_embeddings.npy")

if os.path.exists(chunks_cache) and os.path.exists(embeddings_cache):
    log("Loading PDF chunks and embeddings from cache...", flush=True)
    with open(chunks_cache, "rb") as f:
        chunks = pickle.load(f)
    embeddings = np.load(embeddings_cache)
else:
    log("Processing PDF...", flush=True)
    text = extract_text(pdf_path)
    chunks = split_chunks(text)
    log("Creating embeddings (this will run once and cache)...", flush=True)
    embeddings = embedding_model.encode(chunks)
    with open(chunks_cache, "wb") as f:
        pickle.dump(chunks, f)
    np.save(embeddings_cache, embeddings)

import ollama

# =======================
# QUERY RUNNER / LOOP
# =======================
def process_query(query):
    if not query:
        return ""
    query_embedding = embedding_model.encode([query])
    sims = cosine_similarity(query_embedding, embeddings)[0]
    top_idx = sims.argsort()[-3:][::-1]
    results = [chunks[i] for i in top_idx]
    context = " ".join(results)
    
    try:
        # Synthesize a natural answer using the local mistral model
        prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer the question concisely using only the context provided above."
        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
    except Exception as e:
        return context

if len(sys.argv) > 1:
    # Run once when arguments are passed via child_process.exec
    query = sys.argv[1]
    try:
        ans = process_query(query)
        print(ans, flush=True)
    except Exception as e:
        print("ERROR:", str(e), flush=True)
else:
    print("READY", flush=True)
    # Fallback to interactive stdin loop
    while True:
        try:
            query = sys.stdin.readline().strip()
            if not query:
                continue
            ans = process_query(query)
            print(ans, flush=True)
        except Exception as e:
            print("ERROR:", str(e), flush=True)