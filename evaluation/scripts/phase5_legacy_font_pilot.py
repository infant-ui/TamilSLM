# evaluation/scripts/phase5_legacy_font_pilot.py
"""
Phase 5, step 1: legacy-font severe-mojibake detection + forced-OCR pilot.

Context: Phase 3/4's corrupted Tamil samples all turned out to come from
"searchable" pages (PyMuPDF's native text-layer extraction), not OCR -- OCR only
ever runs on 24/4016 pages corpus-wide (app/ingestion/layout_analyzer.py's
is_page_searchable gate). Within the searchable-page corruption, there are two
DIFFERENT failure modes, and this script targets only the narrower, more severe
one: complete mojibake from a legacy pre-Unicode Tamil DTP font (TAMElango*
variants observed) with no usable ToUnicode CMap, versus the separate, much more
common "duplicated consonant/matra" pattern (text_utils.py's already-disclosed,
not-yet-fixed Problem 3 -- a different script, Phase 5 step 2).

Detection: a font-name match (e.g. "tamelango" in the page's font list) is NOT a
reliable trigger on its own -- see find_severe_mojibake_pages()'s docstring. This
uses a CONTENT-based signal instead: the fraction of non-whitespace characters in
the native-extracted text that fall in the Latin-1-Supplement/Latin-Extended-A
range (U+00A0-U+02FF, excluding common legitimate symbols like degree/currency
marks). Real Tamil text has ~0% of such characters; a legacy font rendered through
the wrong encoding produces a high fraction of them (observed 0.48-0.57 on the 4
confirmed severe pages, vs 0.0-0.098 on 14 OTHER pages that merely use a
TAMElango-family font without being broken).

Usage:
    .venv\\Scripts\\python.exe evaluation\\scripts\\phase5_legacy_font_pilot.py
Writes: evaluation/results/phase5_legacy_font_pilot_results.json
"""
import glob
import json
import os

import fitz
import pytesseract
from PIL import Image

TESSERACT_CMD = os.environ.get(
    "TESSERACT_CMD", r"C:\Users\Infant Jelen Christ\AppData\Local\Programs\Tesseract-OCR\tesseract.EXE"
)
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..", "..")
RESULTS_DIR = os.path.join(HERE, "..", "results")

MOJIBAKE_RATIO_THRESHOLD = 0.25  # see docstring: validated zero false positives at this threshold
LEGITIMATE_SYMBOLS = "°±×÷€£¥©®™"


def mojibake_ratio(text: str) -> float:
    chars = [c for c in text if not c.isspace()]
    if not chars:
        return 0.0
    hits = sum(1 for c in chars if "\u00A0" <= c <= "\u02FF" and c not in LEGITIMATE_SYMBOLS)
    return hits / len(chars)


def distinct_pdfs(pattern: str):
    """Case-insensitive-filesystem-safe dedup: Windows glob can return the same file
    twice if two path segments differ only in case (e.g. 'Tamil' vs 'tamil' folders)."""
    seen, out = set(), []
    for p in glob.glob(pattern, recursive=True):
        norm = os.path.normcase(os.path.abspath(p))
        if norm in seen:
            continue
        seen.add(norm)
        out.append(p)
    return sorted(out)


def find_severe_mojibake_pages():
    """Scans every book PDF for pages whose native-extracted text exceeds
    MOJIBAKE_RATIO_THRESHOLD. Font-name matching alone was tried first and rejected:
    of 18 pages using some TAMElango-family font, only 4 are actually severely
    corrupted (22% precision) -- the same nominal font name can have a working
    ToUnicode CMap in one PDF's embedded subset and a broken one in another's, or
    be broken only for specific glyphs (e.g. a bold heading run) that don't dominate
    the page. The content-based ratio is the validated, precise signal."""
    flagged = []
    for p in distinct_pdfs(os.path.join(REPO, "data", "books", "**", "*.pdf")):
        doc = fitz.open(p)
        for i, page in enumerate(doc):
            text = page.get_text("text")
            if len(text.strip()) <= 100:
                continue  # non-searchable: OCR already runs here, different code path
            r = mojibake_ratio(text)
            if r > MOJIBAKE_RATIO_THRESHOLD:
                fonts = [f[3] for f in page.get_fonts(full=True)]
                flagged.append({"pdf": os.path.relpath(p, REPO), "page_number": i + 1,
                                 "mojibake_ratio": round(r, 4), "fonts": fonts,
                                 "native_text_sample": text[:200]})
    return flagged


def forced_ocr_page(pdf_path: str, page_number: int, lang: str = "tam+eng") -> str:
    """Rasterizes the page at ~300 DPI and runs Tesseract directly, bypassing the
    PDF's (broken) native text layer entirely -- OCR reads glyph SHAPES from the
    rendered image, so it is immune to a bad embedded-font-to-Unicode mapping in a
    way native text extraction isn't."""
    doc = fitz.open(pdf_path)
    page = doc[page_number - 1]
    zoom = 300 / 72
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return pytesseract.image_to_string(img, lang=lang, config="--oem 3 --psm 6")


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    flagged = find_severe_mojibake_pages()
    print(f"Found {len(flagged)} severe-mojibake page(s) corpus-wide (ratio>{MOJIBAKE_RATIO_THRESHOLD}).")

    pilot_results = []
    for f in flagged:
        pdf_abs = os.path.join(REPO, f["pdf"])
        print(f"Forced OCR: {f['pdf']} page {f['page_number']} ...", flush=True)
        ocr_text = forced_ocr_page(pdf_abs, f["page_number"])
        pilot_results.append({**f, "forced_ocr_text": ocr_text})

    out = {
        "method": (
            f"Corpus-wide scan of every page in every book PDF under data/books/ (dedup'd for "
            f"case-insensitive-filesystem glob duplicates). A page is flagged if its native-extracted "
            f"text (page.get_text('text'), only on pages PyMuPDF already considers 'searchable' -- "
            f"len>100 chars) has a mojibake_ratio > {MOJIBAKE_RATIO_THRESHOLD}: the fraction of "
            f"non-whitespace characters in U+00A0-U+02FF (Latin-1 Supplement/Latin Extended-A, "
            f"excluding common legitimate symbols), which is the diagnostic signature of a legacy "
            f"pre-Unicode Tamil font being decoded as Latin-1. Forced OCR renders each flagged page "
            f"at 300 DPI and runs Tesseract (lang=tam+eng, --oem 3 --psm 6) directly on the image, "
            f"bypassing the native text layer entirely."
        ),
        "font_name_detector_rejected": (
            "Tried first: flag any page using a font whose name contains 'tamelango'. Found 18 such "
            "pages corpus-wide, but only 4 are actually severely corrupted (22% precision) -- the same "
            "nominal font family can have a working ToUnicode CMap in one PDF's embedded subset and a "
            "broken one in another's (PDF font subsetting embeds a per-document glyph table even for "
            "the 'same' font), or be broken only for specific glyphs that don't dominate the page. "
            "Rejected in favor of the content-based mojibake_ratio signal above."
        ),
        "n_flagged": len(flagged),
        "n_total_pages_scanned_approx": 4016,
        "pilot_results": pilot_results,
    }
    out_path = os.path.join(RESULTS_DIR, "phase5_legacy_font_pilot_results.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
