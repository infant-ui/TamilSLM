"""
rag_pipeline.py
---------------
Core RAG pipeline with Tamil-aware routing.

ROUTING LOGIC:
  Tamil query  → retrieve Tamil + Web chunks → feed to Ollama llama3 (Tamil LLaMA)
  English query → retrieve English + Web chunks → feed to Ollama (English model)

Tamil answer generation uses the same approach as ret.py:
  - Chunks become the "input text" in the Tamil prompt
  - Ollama llama3 is called with a strict Tamil-only system prompt
  - No English output allowed in Tamil responses

get_client() returns a lightweight Anthropic client (used only for EN→TA query
translation when ANTHROPIC_API_KEY is set; otherwise falls back to a no-op).
"""

import os
import re
import json
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

import ollama

from embedder import retrieve_structured

# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

def detect_language(text: str) -> str:
    """
    Returns 'ta' if text contains Tamil Unicode characters, else 'en'.
    Tamil Unicode block: U+0B80–U+0BFF
    """
    tamil_chars = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
    ratio = tamil_chars / max(len(text), 1)
    return "ta" if ratio > 0.05 or tamil_chars >= 3 else "en"


# ---------------------------------------------------------------------------
# Query translation  (EN → TA for retrieval; TA → EN for English retrieval)
# ---------------------------------------------------------------------------

def translate_to_english(tamil_text: str, client) -> str:
    """
    Translate Tamil query to English so we can also run English retrieval.
    Uses Anthropic API if client is available; otherwise returns original.
    """
    if client is None:
        return tamil_text  # fallback: use Tamil text as-is for embedding

    try:
        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": (
                    f"Translate this Tamil science question to English. "
                    f"Return ONLY the English translation, nothing else.\n\n"
                    f"Tamil: {tamil_text}"
                )
            }]
        )
        return msg.content[0].text.strip()
    except Exception as e:
        print(f"[WARN] Translation failed: {e}")
        return tamil_text


# ---------------------------------------------------------------------------
# Ollama model selection  (separate models for Tamil and English)
# ---------------------------------------------------------------------------

# ── Hard-coded model names ───────────────────────────────────────────────────
# Tamil  → Tamil-LLaMA  (must be pulled: ollama pull Tamil-Llama-2-7b / aari-llama3)
# English → phi3        (must be pulled: ollama pull phi3)
#
# Change these two constants if your pulled model names differ:
TAMIL_MODEL_PREFERENCE = ["llama3","gemma","tinyllama", "phi3"]   # checked left-to-right
ENGLISH_MODEL_PREFERENCE = ["phi3", "phi", "mistral", "llama3"]

def _pick_model(preferences: list, fallback: str) -> str:
    """
    Match preference keywords against installed Ollama models.
    Returns the first installed model whose name contains a preference keyword.
    Falls back to `fallback` string if nothing matches.
    """
    try:
        available = [m["name"] for m in ollama.list().get("models", [])]
        print(f"[INFO] Installed Ollama models: {available}")
        for pref in preferences:
            for avail in available:
                if pref.lower() in avail.lower():
                    return avail
        if available:
            return available[0]
    except Exception as e:
        print(f"[WARN] Could not list Ollama models: {e}")
    return fallback


# Cached at startup so list() is only called once per language
_TAMIL_MODEL:   Optional[str] = None
_ENGLISH_MODEL: Optional[str] = None


def get_tamil_model() -> str:
    global _TAMIL_MODEL
    if _TAMIL_MODEL is None:
        _TAMIL_MODEL = _pick_model(TAMIL_MODEL_PREFERENCE, fallback="llama3")
        print(f"[INFO] Tamil model  → {_TAMIL_MODEL}")
    return _TAMIL_MODEL


def get_english_model() -> str:
    global _ENGLISH_MODEL
    if _ENGLISH_MODEL is None:
        _ENGLISH_MODEL = _pick_model(ENGLISH_MODEL_PREFERENCE, fallback="phi3")
        print(f"[INFO] English model → {_ENGLISH_MODEL}")
    return _ENGLISH_MODEL


# ---------------------------------------------------------------------------
# Anthropic client (for translation only)
# ---------------------------------------------------------------------------

def get_client():
    """
    Returns Anthropic client if ANTHROPIC_API_KEY is set, else None.
    The pipeline works without it — Tamil translation falls back gracefully.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key or api_key.startswith("sk-ant-..."):
        print("[INFO] No Anthropic API key — translation disabled (query used as-is).")
        return None
    try:
        import anthropic
        return anthropic.Anthropic(api_key=api_key)
    except ImportError:
        print("[WARN] anthropic package not installed — translation disabled.")
        return None


# ---------------------------------------------------------------------------
# Tamil answer generation  (mirrors ret.py logic)
# ---------------------------------------------------------------------------

def _generate_tamil_answer(retrieved_text: str, query: str, model: str) -> str:
    """
    Feed retrieved content + Tamil query to Ollama llama3 using the same
    Tamil-only prompt template from ret.py.

    Args:
        retrieved_text: concatenated relevant chunk texts
        query:          original Tamil query
        model:          Ollama model name (should be llama3 / llama3.1:8b)
    """
    prompt = f"""நீங்கள் ஒரு தமிழ் அறிவியல் ஆசிரியர்.

மாணவர் கேள்வி: {query}

கீழே உள்ள பாட உள்ளடக்கத்தை படித்து:
- முழுவதும் தமிழில்
- எளிமையாக
- விளக்கமாக
- கேள்விக்கு நேரடியாக பதில் சொல்லவும்.

ஆங்கிலம் பயன்படுத்தக்கூடாது.

பாட உள்ளடக்கம்:
{retrieved_text}
"""

    print(f"[TAM] Sending to Ollama ({model}) — Tamil prompt …")
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]


# ---------------------------------------------------------------------------
# English answer generation
# ---------------------------------------------------------------------------

def _generate_english_answer(retrieved_text: str, query: str, model: str) -> str:
    """
    Generate English answer from retrieved chunks using Ollama.
    """
    prompt = f"""You are a helpful science teacher.

Student question: {query}

Using ONLY the content below, answer the question clearly and concisely
in English. Cite specific facts from the content.

Content:
{retrieved_text}
"""
    print(f"[ENG] Sending to Ollama ({model}) — English prompt …")
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]


# ---------------------------------------------------------------------------
# Build context string from chunks
# ---------------------------------------------------------------------------

def _build_context(chunks: List[Dict]) -> str:
    """
    Concatenate relevant_text from each chunk into a single context string.
    Uses relevant_text (keyword-windowed excerpt) to keep prompt concise.
    """
    parts = []
    for i, chunk in enumerate(chunks, 1):
        src  = chunk.get("source", "unknown")
        text = chunk.get("relevant_text") or chunk.get("text", "")
        parts.append(f"[Source {i}: {src}]\n{text.strip()}")
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Save session to outputs/
# ---------------------------------------------------------------------------

def _save_session(session: Dict):
    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)
    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    lang = session.get("query_language", "en")
    path = out_dir / f"session_{lang}_{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        # Make sets JSON-serialisable
        s = {k: list(v) if isinstance(v, set) else v for k, v in session.items()}
        json.dump(s, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Session saved → {path}")


# ---------------------------------------------------------------------------
# Main entry point: ask()
# ---------------------------------------------------------------------------

def ask(
    query:           str,
    index,
    metadata:        List[Dict],
    model,           # SentenceTransformer embed model
    client,          # Anthropic client (or None)
    top_k:           int  = 3,
    save:            bool = True,
    seen_ids:        Set[str] = None,
    is_more_request: bool = False,
    force_lang:      Optional[str] = None,
) -> Dict:
    """
    Full RAG pipeline with Tamil routing.

    TAMIL PATH:
      1. Detect Tamil query
      2. (Optionally) translate to English for cross-lingual retrieval
      3. Retrieve Tamil book chunks + Web chunks  via embedder.retrieve_structured()
      4. Build context from retrieved chunks
      5. Pass context + Tamil query → Ollama llama3 with Tamil-only prompt  ← ret.py logic
      6. Return session dict

    ENGLISH PATH:
      1. Retrieve English book chunks + Web chunks
      2. Pass context + query → Ollama (any model)
      3. Return session dict
    """
    if seen_ids is None:
        seen_ids = set()

    # ── 1. Language detection ────────────────────────────────────────────────
    lang = force_lang if force_lang else detect_language(query)
    print(f"[LANG] Detected: {'Tamil' if lang == 'ta' else 'English'}")

    # ── 2. Query in English (for embedding + keyword extraction) ────────────
    if lang == "ta":
        query_en = translate_to_english(query, client)
        print(f"[TRANS] EN equivalent: {query_en}")
    else:
        query_en = query

    # ── 3. Retrieval ─────────────────────────────────────────────────────────
    web_only = is_more_request  # "explain more" → only new web chunks
    retrieval = retrieve_structured(
        query      = query,
        index      = index,
        metadata   = metadata,
        model      = model,
        top_k      = top_k,
        query_lang = lang,
        query_en   = query_en,
        seen_ids   = seen_ids,
        web_only   = web_only,
    )

    primary_chunks = retrieval["primary_chunks"]
    web_chunks     = retrieval["web_chunks"]
    all_chunks     = retrieval["combined"]
    primary_label  = retrieval["primary_label"]

    print(f"[RET] {len(primary_chunks)} primary chunks, {len(web_chunks)} web chunks")

    # ── 4. Build context from ALL retrieved chunks ───────────────────────────
    context = _build_context(all_chunks) if all_chunks else ""

    # ── 5. Generate answer  (language-specific model) ───────────────────────
    if not context.strip():
        if lang == "ta":
            answer = "மன்னிக்கவும், இந்தக் கேள்விக்கு தகவல் கிடைக்கவில்லை. வேறு வகையில் கேட்டுப் பாருங்கள்."
            ollama_model = get_tamil_model()
        else:
            answer = "Sorry, no relevant content was found for this query. Try rephrasing."
            ollama_model = get_english_model()
    elif lang == "ta":
        # ── TAMIL → Tamil-LLaMA via ret.py prompt ───────────────────────────
        ollama_model = get_tamil_model()
        answer = _generate_tamil_answer(context, query, ollama_model)
    else:
        # ── ENGLISH → phi3 ──────────────────────────────────────────────────
        ollama_model = get_english_model()
        answer = _generate_english_answer(context, query, ollama_model)

    # ── 6. Collect new seen chunk IDs ────────────────────────────────────────
    new_seen_ids = [c.get("chunk_id", "") for c in all_chunks if c.get("chunk_id")]

    # ── 7. Build session dict ────────────────────────────────────────────────
    session = {
        "query":          query,
        "query_english":  query_en,
        "query_language": lang,
        "primary_label":  primary_label,
        "primary_chunks": primary_chunks,
        "web_chunks":     web_chunks,
        "context":        context,
        "answer_final":   answer,
        "ollama_model":   ollama_model,
        "new_seen_ids":   new_seen_ids,
        "timestamp":      datetime.datetime.now().isoformat(),
    }

    if save:
        _save_session(session)

    return session