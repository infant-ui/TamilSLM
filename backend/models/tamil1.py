import sys
import os
import re

# Set UTF-8 encoding for stdout/stderr to prevent charmap encoding errors under Windows/exec
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# =======================
# LOW MEMORY SETTINGS
# =======================
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

# =======================
# LOAD MODEL
# =======================
# E5 model is specifically used for multilingual/Tamil RAG in tamil.ipynb
embedding_model = SentenceTransformer("intfloat/multilingual-e5-base")

# =======================
# FIND TAMIL DATASET
# =======================
possible_paths = [
    os.path.join(os.path.dirname(__file__), "tamil_science_textbook.txt"),
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "Cross Lingual Retrieval -20260625T150607Z-3-001", "Cross Lingual Retrieval", "data", "texts", "tamil_science_textbook.txt"),
    os.path.join(os.path.dirname(__file__), "..", "..", "Embedding-20260625T150608Z-3-001", "Embedding", "data", "tamil_book_output.txt")
]

tamil_text_path = None
for p in possible_paths:
    if os.path.exists(p):
        tamil_text_path = p
        break

if tamil_text_path:
    with open(tamil_text_path, "r", encoding="utf-8") as f:
        text = f.read()
else:
    # Fallback default text if file is not found
    text = "தமிழ் அறிவியல் புத்தகத் தகவல் கிடைக்கவில்லை."

# =======================
# CHUNKING
# =======================
def split_chunks(text, chunk_size=300):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    chunk = ""
    for s in sentences:
        if len(chunk) + len(s) < chunk_size:
            chunk += " " + s
        else:
            if chunk.strip():
                chunks.append(chunk.strip())
            chunk = s
    if chunk.strip():
        chunks.append(chunk.strip())
    return chunks

import pickle

# =======================
# PREPROCESS (WITH CACHE)
# =======================
cache_dir = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(cache_dir, exist_ok=True)
chunks_cache = os.path.join(cache_dir, "tamil_chunks.pkl")
embeddings_cache = os.path.join(cache_dir, "tamil_embeddings.npy")

if os.path.exists(chunks_cache) and os.path.exists(embeddings_cache):
    with open(chunks_cache, "rb") as f:
        chunks = pickle.load(f)
    embeddings = np.load(embeddings_cache)
else:
    chunks = split_chunks(text)
    # E5 models require "passage: " prefix for text chunks
    prefixed_chunks = ["passage: " + c for c in chunks]
    embeddings = embedding_model.encode(prefixed_chunks, normalize_embeddings=True)
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
    # E5 models require "query: " prefix for queries
    query_embedding = embedding_model.encode(["query: " + query], normalize_embeddings=True)
    sims = cosine_similarity(query_embedding, embeddings)[0]
    top_idx = sims.argsort()[-3:][::-1]
    results = [chunks[i] for i in top_idx]
    context = " ".join(results)
    
    try:
        # Synthesize a natural answer in Tamil using the local llama3.1 model
        prompt = f"விவரம்:\n{context}\n\nகேள்வி: {query}\n\nமேலே உள்ள விவரத்தை மட்டும் பயன்படுத்தி கேள்விக்கு தமிழில் சுருக்கமாக பதிலளிக்கவும்."
        response = ollama.chat(
            model="llama3.1",
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
