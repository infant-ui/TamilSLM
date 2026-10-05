"""
app.py — Science RAG (v5)
Tamil query  → Tamil Book chunks  + Web chunks  → answer in Tamil
English query → English Book chunks + Web chunks → answer in English

Model: auto-selected from installed Ollama models
  Best: llama3.1:8b  |  Fallback: mistral  |  Last resort: phi3

Tamil translation: Anthropic Claude API (set ANTHROPIC_API_KEY in .env)
  Fallback: Google Translate → argostranslate (offline)
"""

import re
import os

# Load .env so ANTHROPIC_API_KEY is available for translation
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed; env vars must be set manually

import gradio as gr
from embedder import load_index, get_model
from rag_pipeline import ask, get_client

print("[APP] Loading …")
try:
    index, metadata = load_index()
    embed_model     = get_model() #Loads metadata (source, page, etc.)
    client          = get_client() #Loads LLM client
    READY = True
    print("[APP] Ready ✅")
except FileNotFoundError:
    READY = False; index = metadata = embed_model = client = None
    print("[APP] Run  python build_index.py  first.")
except EnvironmentError as e:
    READY = False; index = metadata = embed_model = client = None
    print(f"[APP] {e}")


# FIX 3: detect "explain more" / "tell me more" intent in English or Tamil
_MORE_PATTERNS = re.compile(
    r"\b(explain\s+more|tell\s+me\s+more|more\s+detail|elaborate|"
    r"give\s+more|show\s+more|continue|go\s+on|next|இன்னும்|மேலும்|"
    r"விரிவாக|தொடர்|மேல்)\b",
    re.IGNORECASE,
)

def _is_more_request(query: str) -> bool: #the user is asking for additional explanation or not.
    return bool(_MORE_PATTERNS.search(query))


def answer_query(query: str, top_k: int, history: list, seen_ids: set, last_query_en: str, last_lang: str):
    """
    seen_ids     — set of chunk_ids already displayed in this topic thread
    last_query_en — English version of the last substantive question (for "explain more")
    """
    if not query.strip(): #empty message → ignore
        return history, "", seen_ids, last_query_en, last_lang

    if not READY:
        msg = (
            "⚠️ **System not ready.**\n\n"
            "Place files:\n```\ndata/pdfs/english_bookk.pdf\n"
            "data/pdfs/add/web1.pdf\n"
            "data/texts/tamil_book_output.txt\n```\n\n"
            "Then:\n```\npython build_index.py\nollama serve\n```"
        )
        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": msg})
        return history, "", seen_ids, last_query_en, last_lang

    # FIX 3: if user asks "explain more / மேலும்", reuse the last topic query
    # and pass seen_ids so we fetch only NEW chunks
    is_more = _is_more_request(query)
    effective_query = last_query_en if (is_more and last_query_en) else query
    effective_seen  = seen_ids if is_more else set()
    # For "explain more", force the original question's language
    forced_lang = last_lang if (is_more and last_lang) else None

    try:
        session = ask(
            query            = effective_query,
            index            = index,
            metadata         = metadata,
            model            = embed_model,
            client           = client,
            top_k            = int(top_k),
            save             = True,
            seen_ids         = effective_seen,
            is_more_request  = is_more,
            force_lang       = forced_lang,
        )
    except Exception as e:
        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": f"❌ {e}"})
        return history, "", seen_ids, last_query_en, last_lang

    lang          = session["query_language"]
    lang_label    = "🇮🇳 Tamil" if lang == "ta" else "🇬🇧 English"
    primary_label = session["primary_label"]
    primary_icon  = "🇮🇳" if lang == "ta" else "📖"
    answer        = session["answer_final"]
    p_chunks      = session["primary_chunks"]
    w_chunks      = session["web_chunks"]

    # Accumulate seen_ids
    new_ids = set(session.get("new_seen_ids", [])) #Prevents repetition
    updated_seen_ids = (seen_ids | new_ids) if is_more else new_ids

    # Update last_query_en and last_lang only for real questions (not "explain more")
    updated_last_query = session["query_english"] if not is_more else last_query_en
    updated_last_lang  = lang if not is_more else last_lang

    def fmt_section(chunks, icon, label):
        if not chunks:
            return (
                f"**{icon} {label}**\n\n"
                f"> ⚠️ No chunks found above relevance threshold.\n"
                f"> This topic may not be covered — try rephrasing.\n"
            )
        extra = " (Additional Content)" if is_more else ""
        # Show only TOP-1 chunk
        top_chunk = chunks[0]
        pg    = f", p.{top_chunk['page']}" if top_chunk.get("page") else ""
        score = top_chunk.get("score", 0)
        rel   = top_chunk.get("relevant_text", "").strip()
        full  = top_chunk.get("full_text", "").strip()

        lines = [f"**{icon} {label}{extra} — top chunk:**\n"]
        lines.append(f"**#1** `[{top_chunk['source']}{pg}]`  score=`{score:.3f}`\n")
        lines.append(f"🟡 **Relevant excerpt (sent to LLM):**")
        lines.append(f"> {rel}\n")
        if full and full != rel:
            lines.append(
                f"<details><summary>📄 Full chunk text</summary>\n\n{full}\n\n</details>\n"
            )
        return "\n".join(lines)

    web_section = fmt_section(w_chunks, "🌐", "Web Content")

    # FIX: heading in user's language
    if is_more:
        answer_heading = "✨ கூடுதல் விளக்கம்" if lang == "ta" else "✨ Additional Explanation"
    else:
        answer_heading = "✨ இறுதி விடை" if lang == "ta" else "✨ Final Answer"

    # FIX: for "explain more" → show ONLY web section (no book section)
    if is_more:
        full_response = (
            f"**Language detected:** {lang_label}\n\n"
            f"---\n{web_section}\n"
            f"---\n### {answer_heading}\n\n{answer}"
        )
    else:
        primary_section = fmt_section(p_chunks, primary_icon, primary_label)
        full_response = (
            f"**Language detected:** {lang_label}\n\n"
            f"---\n{primary_section}\n"
            f"---\n{web_section}\n"
            f"---\n### {answer_heading}\n\n{answer}"
        )

    history.append({"role": "user", "content": query})
    history.append({"role": "assistant", "content": full_response})
    return history, "", updated_seen_ids, updated_last_query, updated_last_lang


CSS = """
#title    { text-align: center; padding: 18px 0 6px 0; }
#subtitle { text-align: center; color: #888; margin-bottom: 18px; font-size:0.95em; }
details summary { cursor:pointer; color:#aaa; font-size:0.82em; }
blockquote { border-left:3px solid #f0a500; padding-left:10px; color:#ddd; margin:4px 0; }
"""

ENGLISH_SAMPLES = [
    "What is photosynthesis?",
    "What are derived quantities? Give examples.",
    "Explain Newton's first law of motion.",
    "What is the difference between acids and bases?",
    "What is speed and how is it calculated?",
    "What is a distance-time graph?",
    "What is a cell and its main parts?",
    "What are physical quantities and their classification?",
]

TAMIL_SAMPLES = [
    "ஒளிச்சேர்க்கை என்றால் என்ன?",
    "நியூட்டனின் முதல் இயக்க விதி என்ன?",
    "அமிலங்கள் மற்றும் காரங்கள் என்றால் என்ன?",
    "செல் என்றால் என்ன?",
    "மரபணு என்றால் என்ன?",
    "வேகம் என்றால் என்ன?",
    "இயற்பியல் அளவுகள் என்றால் என்ன?",
]

with gr.Blocks(css=CSS, title="Science RAG — Offline") as demo:
    gr.Markdown("# 🔬 Science RAG — Offline (Phi3)", elem_id="title")
    gr.Markdown(
        "**Tamil query** → Tamil Book + Web &nbsp;|&nbsp; "
        "**English query** → English Book + Web &nbsp;|&nbsp; "
        "🟡 = top-1 chunk sent to LLM &nbsp;|&nbsp; "
        "💡 Type **'explain more'** / **'மேலும்'** for new web content",
        elem_id="subtitle",
    )

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                label="Conversation", height=620
                
            )
            with gr.Row():
                query_box = gr.Textbox(
                    placeholder="English or Tamil question… / தமிழ் அல்லது ஆங்கிலத்தில் கேளுங்கள்… (or type 'explain more')",
                    label="Your Question", lines=2, scale=5,
                )
                submit_btn = gr.Button("Ask →", variant="primary", scale=1)

        with gr.Column(scale=1):
            top_k_slider = gr.Slider(
                minimum=1, maximum=5, value=3, step=1,
                label="Top-K per source",
            )
            gr.Markdown("### 🇬🇧 English Questions")
            for q in ENGLISH_SAMPLES:
                gr.Button(q, size="sm").click(
                    fn=lambda x=q: x, outputs=query_box
                )
            gr.Markdown("### 🇮🇳 Tamil Questions")
            for q in TAMIL_SAMPLES:
                gr.Button(q, size="sm").click(
                    fn=lambda x=q: x, outputs=query_box
                )
            gr.Markdown("---")
            clear_btn = gr.Button("🗑 Clear", variant="secondary")

    # State: seen chunk_ids + last English query + last language for "explain more"
    state_history    = gr.State([])
    state_seen_ids   = gr.State(set())
    state_last_query = gr.State("")
    state_last_lang  = gr.State("")

    submit_btn.click(
        answer_query,
        [query_box, top_k_slider, state_history, state_seen_ids, state_last_query, state_last_lang],
        [chatbot, query_box, state_seen_ids, state_last_query, state_last_lang],
    )
    query_box.submit(
        answer_query,
        [query_box, top_k_slider, state_history, state_seen_ids, state_last_query, state_last_lang],
        [chatbot, query_box, state_seen_ids, state_last_query, state_last_lang],
    )
    clear_btn.click(
        lambda: ([], "", set(), "", ""),
        outputs=[chatbot, query_box, state_seen_ids, state_last_query, state_last_lang],
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False, inbrowser=True)

