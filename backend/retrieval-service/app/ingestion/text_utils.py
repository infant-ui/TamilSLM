"""
app/ingestion/text_utils.py

Small, dependency-free text-repair helpers shared between the OCR path
(ocr_cleaner.py) and the native PDF text-extraction path (pdf_cleaner.py).

Context: an audit of the live chunk cache after the 2026-09-16 full reindex
found that Tamil text extracted natively from these textbook PDFs (i.e. on
pages PyMuPDF considers "searchable", which is the majority of pages -- OCR
is the exception, not the rule) is frequently corrupted by the source PDFs'
embedded Tamil fonts:
  1. Split vowel signs (e.g. "ெ" + consonant + "ா" instead of the combined
     "ொ") -- the same pattern ocr_cleaner.py's normalize_tamil_unicode()
     already repairs for OCR output, but that function was never wired into
     the native-extraction path, so it never ran on the majority of Tamil
     content.
  2. Stray Unicode replacement characters (U+FFFD) and C0 control codes
     (U+0000-U+001F, excluding whitespace) standing in for glyphs the font's
     encoding could not be mapped to Unicode for. These carry no recoverable
     information -- the original character was already lost by the time
     PyMuPDF emits one of these -- so removing them only prevents visible
     junk from reaching chunks; it does not recover the lost glyph.
There is a third, deeper corruption pattern (systematic duplication of
consonant+matra sequences, e.g. "பொ" + stray char + "ொது" where "பொது" was
intended) that looked common in sampling but was NOT confidently
characterized as a safe, general regex fix -- guessing wrong here risks
silently corrupting otherwise-correct text further, so it is intentionally
NOT addressed by this module. See the evaluation report for that finding.
"""
import re
import unicodedata


def normalize_tamil_unicode(text: str) -> str:
    """
    Normalizes Tamil Unicode characters to NFC (Canonical Composition).
    Fixes common OCR/extraction ligature splitting where vowel signs (e.g.
    ொ, ோ, ௌ) are separated from their base consonants.

    Verbatim logic from ocr_cleaner.OCRCleaner.normalize_tamil_unicode --
    duplicated here (rather than imported from OCRCleaner) so that callers
    which only need text repair, such as pdf_cleaner.py, don't have to
    construct an OCRCleaner instance, which initializes PaddleOCR/GPU.
    """
    if not text:
        return ""

    normalized = unicodedata.normalize("NFC", text)

    split_patterns = {
        r"ெ([அ-ிீ-்])ா": r"\1ொ",
        r"ே([அ-ிீ-்])ா": r"\1ோ",
        r"ெ([அ-ிீ-்])ள": r"\1ௌ",
    }
    for pat, repl in split_patterns.items():
        normalized = re.sub(pat, repl, normalized)

    return normalized


def strip_unrecoverable_artifacts(text: str) -> str:
    """
    Strips characters that carry no recoverable text information:
    - U+FFFD (Unicode replacement character), left behind when a PDF's
      embedded font glyph could not be mapped to a real Unicode codepoint.
    - C0 control characters (U+0000-U+001F) other than tab/newline/CR, which
      several of these textbook PDFs' Tamil font encodings emit in place of
      a real glyph when no ToUnicode mapping exists for it.
    This does not "fix" the underlying per-font encoding problem -- the
    glyph was already unrecoverable by the time extraction produced one of
    these placeholders -- it only prevents visible junk from reaching
    chunks and downstream noise-ratio filters.
    """
    if not text:
        return ""
    text = text.replace("�", "")
    text = re.sub(r"[\x00-\x08\x0e-\x1f]", "", text)
    return text
