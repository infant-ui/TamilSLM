"""
document_loader.py
------------------
Loads and chunks documents from:

  data/
  ├── pdfs/
  │   ├── english_bookk.pdf          ← main English textbook
  │   └── add/                       ← web-content PDFs
  │       ├── web1.pdf
  │       └── ...
  └── texts/
      └── tamil_book_output.txt      ← Tamil textbook (plain text, UTF-8)

Chunking strategy:
  - English PDFs : 400 words, 60-word overlap  (complete statements fit)
  - Tamil text   : 200 words, 50-word overlap  (Tamil words are longer/denser)
  - Minimum chunk length: 40 chars (skip noise pages)
"""

import re
from pathlib import Path
from typing import List, Dict

import fitz  # PyMuPDF
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 42 #Makes language detection consistent every time


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def detect_language(text: str) -> str:
    try:
        lang = detect(text[:500])
        return "ta" if lang == "ta" else "en"
    except Exception:
        return "en"


def clean_text(text: str) -> str:
    # Collapse whitespace but keep sentence boundaries
    text = re.sub(r"[ \t]+", " ", text)#Replace multiple spaces/tabs → single space
    text = re.sub(r"\n{3,}", "\n\n", text) #Too many new lines → reduce to 2
    return text.strip()


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 60) -> List[str]:
    """Word-based overlapping chunks. Returns complete-sentence chunks where possible."""
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        end   = min(start + chunk_size, len(words)) #Take 400 words max
        chunk = " ".join(words[start:end])
        if len(chunk.strip()) >= 40:
            chunks.append(chunk.strip())
        start += chunk_size - overlap
    return chunks


# ---------------------------------------------------------------------------
# PDF loader
# ---------------------------------------------------------------------------

def load_pdf(pdf_path: str, source_label: str = "") -> List[Dict]:
    """
    Extract text page-by-page, chunk each page, return list of chunk dicts.
    Uses 400-word chunks with 60-word overlap for complete statement coverage.
    """
    records: List[Dict] = []
    label = source_label or Path(pdf_path).stem

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"[WARN] Cannot open PDF '{pdf_path}': {e}")
        return records

    # Collect full text first, then chunk — avoids mid-sentence page breaks
    full_text_pages: List[tuple] = []
    for page_num, page in enumerate(doc, start=1):
        raw     = page.get_text("text") #Get text from page
        cleaned = clean_text(raw)
        if len(cleaned) >= 40:
            full_text_pages.append((page_num, cleaned))

    doc.close()

    # Chunk each page independently (keeps page number in metadata)
    for page_num, page_text in full_text_pages:
        lang   = detect_language(page_text)
        chunks = chunk_text(page_text, chunk_size=400, overlap=60) #Split into chunks
        for i, chunk in enumerate(chunks):
            records.append({
                "text":     chunk,
                "source":   label,
                "language": lang,
                "page":     page_num,
                "chunk_id": f"{label}_p{page_num}_c{i}",
            })

    print(f"[INFO] PDF  '{Path(pdf_path).name}'  ({label}) → {len(records)} chunks")
    return records


# ---------------------------------------------------------------------------
# Plain-text loader  (Tamil book)
# ---------------------------------------------------------------------------

def load_text_file(txt_path: str, source_label: str = "") -> List[Dict]:
    """
    Load a plain-text file, auto-detect language per chunk.
    Uses smaller chunks (200 words) for Tamil — richer morphology needs less context.
    """
    records: List[Dict] = []
    label = source_label or Path(txt_path).stem

    try:
        with open(txt_path, "r", encoding="utf-8") as fh:
            raw = fh.read()
    except UnicodeDecodeError:
        try:
            with open(txt_path, "r", encoding="latin-1") as fh:
                raw = fh.read()
        except Exception as e:
            print(f"[WARN] Cannot read '{txt_path}': {e}")
            return records
    except Exception as e:
        print(f"[WARN] Cannot read '{txt_path}': {e}")
        return records

    cleaned = clean_text(raw)

    # Detect overall language to set chunk size
    overall_lang = detect_language(cleaned[:1000])
    c_size, c_overlap = (200, 50) if overall_lang == "ta" else (400, 60)

    chunks = chunk_text(cleaned, chunk_size=c_size, overlap=c_overlap)

    for i, chunk in enumerate(chunks):
        lang = detect_language(chunk)
        records.append({
            "text":     chunk,
            "source":   label,
            "language": lang,
            "page":     None,
            "chunk_id": f"{label}_c{i}",
        })

    print(f"[INFO] TXT  '{Path(txt_path).name}'  ({label}) → {len(records)} chunks  [lang={overall_lang}]")
    return records


# ---------------------------------------------------------------------------
# Master loader
# ---------------------------------------------------------------------------

def load_all_documents(
    pdf_dir:  str = "data/pdfs",
    text_dir: str = "data/texts",
) -> List[Dict]:
    """
    Recursively loads:
      - All *.pdf  inside pdf_dir  and sub-folders  (e.g. add/)
      - All *.txt  inside text_dir

    Expected layout:
        data/pdfs/english_bookk.pdf
        data/pdfs/add/web1.pdf
        data/pdfs/add/web2.pdf
        data/texts/tamil_book_output.txt
    """
    all_chunks: List[Dict] = []

    # ── PDFs (recursive) ────────────────────────────────────────────────────
    pdf_root = Path(pdf_dir)
    if pdf_root.exists():
        pdf_files = sorted(pdf_root.rglob("*.pdf")) #Find all PDFs (even inside folders)
        if pdf_files:
            for pdf_file in pdf_files:
                rel   = pdf_file.relative_to(pdf_root)
                label = str(rel.with_suffix("")).replace("\\", "/") #add/web1.pdf → add/web1
                all_chunks.extend(load_pdf(str(pdf_file), source_label=label))
        else:
            print(f"[WARN] No PDF files under '{pdf_dir}'")
    else:
        print(f"[WARN] PDF dir not found: '{pdf_dir}'  — create it and add PDFs")

    # ── Text files ──────────────────────────────────────────────────────────
    txt_root = Path(text_dir)
    if txt_root.exists():
        txt_files = sorted(txt_root.glob("*.txt"))
        if txt_files:
            for txt_file in txt_files:
                all_chunks.extend(load_text_file(str(txt_file)))
        else:
            print(f"[WARN] No .txt files in '{text_dir}'")
    else:
        print(f"[WARN] Text dir not found: '{text_dir}'")

    print(f"\n[INFO] Total chunks loaded: {len(all_chunks)}")
    return all_chunks
