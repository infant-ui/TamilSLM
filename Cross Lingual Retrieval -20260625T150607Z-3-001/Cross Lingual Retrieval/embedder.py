"""
embedder.py
-----------
Retrieval design:
  Tamil query  → Tamil book chunks  + Web chunks  (English book hidden)
  English query → English book chunks + Web chunks  (Tamil book hidden)

FIX 1 — Web threshold lowered (0.38 → 0.30) so physics/web content is fetched.
FIX 2 — Tamil retrieval: relaxed fallback threshold for web chunks when Tamil
         book chunks are scarce.
FIX 3 — "explain more" pagination: seen_ids set passed in → already-shown
         chunks are skipped, returning genuinely NEW content each time.
"""

import os
import re
import pickle
from pathlib import Path
from typing import List, Dict, Set

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

EMBED_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
INDEX_DIR  = "embeddings"
INDEX_FILE = os.path.join(INDEX_DIR, "faiss.index")
META_FILE  = os.path.join(INDEX_DIR, "metadata.pkl")

# FIX 1: lowered web threshold so physics-learning-material content is found
THRESHOLD_BOOK  = 0.28
THRESHOLD_TAMIL = 0.28
THRESHOLD_WEB   = 0.30   # was 0.38


# ---------------------------------------------------------------------------
# Model / index helpers
# ---------------------------------------------------------------------------

def get_model() -> SentenceTransformer:
    print(f"[INFO] Loading embedding model: {EMBED_MODEL_NAME}")
    return SentenceTransformer(EMBED_MODEL_NAME)

def embed_chunks(chunks, model, batch_size=64):
    texts = [c["text"] for c in chunks]
    print(f"[INFO] Embedding {len(texts)} chunks …")
    emb = model.encode(texts, batch_size=batch_size, show_progress_bar=True,
                       convert_to_numpy=True, normalize_embeddings=True)
    return emb.astype("float32") #Converts data type to float32

def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)#no compression, exact search (accurate but slower for huge data)
#IP (Inner Product) → uses dot product similarity
    index.add(embeddings)
    print(f"[INFO] FAISS: {index.ntotal} vectors, dim={dim}")
    return index

def save_index(index, metadata):
    Path(INDEX_DIR).mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, INDEX_FILE)
    with open(META_FILE, "wb") as f:
        pickle.dump(metadata, f)
    print(f"[INFO] Saved index → {INDEX_FILE}")

def load_index():
    if not os.path.exists(INDEX_FILE):
        raise FileNotFoundError(f"No index at '{INDEX_FILE}'. Run build_index.py first.")
    index = faiss.read_index(INDEX_FILE)
    with open(META_FILE, "rb") as f:
        metadata = pickle.load(f)
    print(f"[INFO] Loaded index: {index.ntotal} vectors")
    return index, metadata

def build_index(chunks):
    model = get_model()
    emb   = embed_chunks(chunks, model)
    index = build_faiss_index(emb)
    save_index(index, chunks)
    return index, chunks, model


# ---------------------------------------------------------------------------
# Bucket classifier
# ---------------------------------------------------------------------------

def _bucket(chunk: Dict) -> str:
    """
    'web'   — source starts with 'add/'
    'tamil' — source contains 'tamil'
    'book'  — everything else (English textbook)
    """
    src = chunk.get("source", "").lower().replace("\\", "/")
    if src.startswith("add/") or src == "add":
        return "web"
    if "tamil" in src:
        return "tamil"
    return "book"


# ---------------------------------------------------------------------------
# Tamil chunk quality filter
# ---------------------------------------------------------------------------

def _tamil_char_ratio(text: str) -> float:#how much of the text is Tamil.
    """Return fraction of chars that are Tamil Unicode (U+0B80–U+0BFF)."""
    if not text:
        return 0.0
    tamil_chars = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
    return tamil_chars / len(text)

def _is_junk_tamil_chunk(text: str, min_tamil_ratio: float = 0.15) -> bool:
    """
    Returns True if a Tamil chunk is too noisy to be useful.
    Criteria:
    - Tamil char ratio below threshold (chunk is mostly numbers/symbols)
    - Too many consecutive digit/symbol lines (OCR table garbage)
    """
    ratio = _tamil_char_ratio(text)
    if ratio < min_tamil_ratio:
        return True
    # Count lines that are mostly non-Tamil (numbers, symbols, pipe chars)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines:
        return True
    junk_lines = sum( #Have very little Tamil (<10%)
        1 for l in lines
        if len(l) > 0 and _tamil_char_ratio(l) < 0.10 and len(l) > 3
    )
    if junk_lines / len(lines) > 0.6: #If more than 60% lines are junk → discard chunk
        return True
    return False

def _clean_tamil_text(text: str) -> str:
    """Remove junk lines from Tamil chunk, keep lines with meaningful Tamil content."""
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Keep line if it has enough Tamil characters or is a short label
        if _tamil_char_ratio(stripped) >= 0.10 or len(stripped) < 10:
            cleaned.append(stripped)
    return ' '.join(cleaned) if cleaned else text


# ---------------------------------------------------------------------------
# Relevant sentence extractor
# ---------------------------------------------------------------------------

STOP_WORDS = {
    "what","is","the","a","an","of","in","and","or","to","are","how","does",
    "do","give","explain","define","tell","me","about","its","their","for",
    "with","from","by","on","at","be","was","were","has","have","had","it",
    "என்றால்","என்ன","கொடு","சொல்","விவரி","பற்றி","என்பது","ஆகும்","உள்ள",
    "மற்றும்","ஒரு","இது","அது","இந்த","அந்த","என","ஆன","கள்","கள",
}

def _extract_relevant_sentences(text: str, query_en: str, window: int = 5, is_tamil: bool = False) -> str:
    """
    Extract the most relevant sentences from chunk text.
    FIX (Tamil): OCR Tamil text lacks clean sentence boundaries (.!?), so
    sentence-windowing cuts the excerpt short. For Tamil chunks, return the
    full cleaned text so the LLM and UI both see everything. Cap at 1200
    chars to avoid bloating the prompt.
    """
    # ── Tamil: skip sentence splitting; return full cleaned text ────────────
    if is_tamil:
        return text[:1200] if len(text) > 1200 else text #Full text (max 1200 characters)

    # ── English: original keyword-window logic ───────────────────────────────
    keywords = [w.lower() for w in re.findall(r'[a-zA-Z]+', query_en)
                if w.lower() not in STOP_WORDS and len(w) > 2]

    sentences = re.split(r'(?<=[.!?\n।\u0964\u0965])\s+', text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10] #remove short sentences

    if not sentences:
        return text[:800]

    if not keywords:
        return " ".join(sentences[:window])

    scores = []
    for s in sentences:
        s_lower = s.lower()
        score = sum(1 for kw in keywords if kw in s_lower)
        if re.search(r'\b(is|are|called|defined|means|refers|classified|types|examples?)\b', s_lower):
            score += 0.5
        if re.search(r'(என்பது|எனப்படும்|ஆகும்|என்றால்|குறிக்கும்|விதி|சூத்திரம்)', s):
            score += 0.5
        scores.append(score)

    best_idx = int(np.argmax(scores)) #Picks sentence with highest relevance

    if scores[best_idx] == 0:
        return " ".join(sentences[:window])

    start = max(0, best_idx - 1)
    end   = min(len(sentences), best_idx + window)
    return " ".join(sentences[start:end])


# ---------------------------------------------------------------------------
# retrieve_structured — language-aware, with seen_ids for "explain more"
# ---------------------------------------------------------------------------

def retrieve_structured(
    query:      str,
    index,
    metadata:   List[Dict],
    model,
    top_k:      int = 3,
    query_lang: str = "en",
    query_en:   str = "",
    seen_ids:   Set[str] = None,
    web_only:   bool = False,   # FIX 4: True for "explain more" — web chunks only
) -> Dict:
    """
    Tamil query  → retrieve from: tamil bucket + web bucket
    English query → retrieve from: book  bucket + web bucket

    FIX 3: seen_ids — already-shown chunks are skipped so "explain more"
           returns genuinely new content.
    FIX 4: web_only=True — ONLY web chunks returned (used for "explain more").
    """
    if seen_ids is None:
        seen_ids = set()

    kw_query  = query_en or query
    use_tamil = (query_lang == "ta")
    target_primary = "tamil" if use_tamil else "book"

    q_emb = model.encode(
        [query], convert_to_numpy=True, normalize_embeddings=True,
    ).astype("float32")

    # Over-fetch to have room after filtering seen_ids
    over_fetch = min(top_k * 60, index.ntotal)
    scores_arr, indices_arr = index.search(q_emb, over_fetch)

    primary_chunks: List[Dict] = []
    web_chunks:     List[Dict] = []

    for score, idx in zip(scores_arr[0], indices_arr[0]):
        if idx == -1:
            continue
        score  = float(score)
        chunk  = dict(metadata[idx])
        bucket = _bucket(chunk)
        chunk_id = chunk.get("chunk_id", f"idx_{idx}")

        # Skip already-shown chunks
        if chunk_id in seen_ids:
            continue

        # FIX 4: "explain more" → skip ALL book/tamil chunks; only web allowed
        if web_only and bucket != "web":
            continue

        # Skip the OTHER book bucket entirely (language routing)
        if not web_only:
            if bucket == "book"  and use_tamil:     continue
            if bucket == "tamil" and not use_tamil: continue

        # Apply threshold
        if bucket == "web":
            if score < THRESHOLD_WEB: continue
        else:
            thresh = THRESHOLD_TAMIL if bucket == "tamil" else THRESHOLD_BOOK
            if score < thresh: continue

        chunk["score"]         = score
        chunk["chunk_id"]      = chunk_id

        # FIX: For Tamil chunks, clean OCR junk lines and skip if chunk is too noisy
        raw_text = chunk["text"]
        if bucket == "tamil":
            if _is_junk_tamil_chunk(raw_text):
                print(f"      [SKIP junk Tamil chunk] score={score:.3f} id={chunk_id}")
                continue
            chunk["text"] = _clean_tamil_text(raw_text)

        chunk["relevant_text"] = _extract_relevant_sentences(
            chunk["text"], kw_query, is_tamil=(bucket == "tamil")
        )

        if not web_only and bucket == target_primary and len(primary_chunks) < top_k:
            primary_chunks.append(chunk)
        elif bucket == "web" and len(web_chunks) < top_k:
            web_chunks.append(chunk)

        if len(primary_chunks) >= top_k and len(web_chunks) >= top_k:
            break

    # FIX 2: Tamil query — if web chunks are scarce, relax threshold to get more
    if use_tamil and len(web_chunks) < top_k:
        relaxed_threshold = THRESHOLD_WEB - 0.08
        existing_web_ids  = {c.get("chunk_id") for c in web_chunks}
        for score, idx in zip(scores_arr[0], indices_arr[0]):
            if idx == -1 or len(web_chunks) >= top_k:
                break
            score    = float(score)
            chunk    = dict(metadata[idx])
            bucket   = _bucket(chunk)
            chunk_id = chunk.get("chunk_id", f"idx_{idx}")
            if bucket != "web":
                continue
            if chunk_id in seen_ids or chunk_id in existing_web_ids:
                continue
            if score < relaxed_threshold:
                continue
            chunk["score"]         = score
            chunk["chunk_id"]      = chunk_id
            chunk["relevant_text"] = _extract_relevant_sentences(
                chunk["text"], kw_query, is_tamil=False
            )
            web_chunks.append(chunk)
            existing_web_ids.add(chunk_id)

    # Interleave: primary[0], web[0], primary[1], web[1] …
    combined: List[Dict] = []
    for i in range(max(len(primary_chunks), len(web_chunks))):
        if i < len(primary_chunks):
            combined.append(primary_chunks[i])
        if i < len(web_chunks):
            combined.append(web_chunks[i])

    label = "Tamil Book" if use_tamil else "English Book"
    return {
        "primary_chunks": primary_chunks,
        "web_chunks":      web_chunks,
        "combined":        combined,
        "primary_label":   label,
    }


# ---------------------------------------------------------------------------
# Legacy shim
# ---------------------------------------------------------------------------

def retrieve(query, index, metadata, model, top_k=5, lang_filter=None):
    result = retrieve_structured(query, index, metadata, model,
                                  top_k=top_k, query_en=query)
    return result["combined"]
