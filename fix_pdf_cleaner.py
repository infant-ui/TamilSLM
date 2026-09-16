import io

path = "backend/retrieval-service/app/ingestion/pdf_cleaner.py"

with io.open(path, "r", encoding="utf-8", newline="") as f:
    content = f.read()

# 1. Add the import, right after the existing "import logging" line.
old_import = (
    "import fitz  # PyMuPDF\r\n"
    "from typing import List, Dict, Tuple, Optional\r\n"
    "import logging\r\n"
)
new_import = (
    "import fitz  # PyMuPDF\r\n"
    "from typing import List, Dict, Tuple, Optional\r\n"
    "import logging\r\n"
    "from app.ingestion.text_utils import normalize_tamil_unicode, strip_unrecoverable_artifacts\r\n"
)
n1 = content.count(old_import)
if n1 != 1:
    raise SystemExit(f"import block: expected 1 match, found {n1}")
content = content.replace(old_import, new_import)

# 2. Apply the repair functions to natively-extracted text, right where it's
#    first stripped, before any of the header/footer/watermark filtering.
old_strip = (
    "        for block in raw_blocks:\r\n"
    "            x0, y0, x1, y1, text, block_no, block_type = block\r\n"
    "            text_strip = text.strip()\r\n"
    "            \r\n"
    "            if not text_strip:\r\n"
)
new_strip = (
    "        for block in raw_blocks:\r\n"
    "            x0, y0, x1, y1, text, block_no, block_type = block\r\n"
    "            # Repair Tamil text corruption from this PDF's embedded font encoding\r\n"
    "            # (split vowel signs, stray replacement/control-code glyphs) -- see\r\n"
    "            # text_utils.py docstring. NFC normalization and the replacement-char\r\n"
    "            # strip are no-ops for already-clean English text, so this is safe to\r\n"
    "            # apply unconditionally rather than threading medium/language through.\r\n"
    "            text_strip = normalize_tamil_unicode(strip_unrecoverable_artifacts(text.strip()))\r\n"
    "            \r\n"
    "            if not text_strip:\r\n"
)
n2 = content.count(old_strip)
if n2 != 1:
    raise SystemExit(f"strip block: expected 1 match, found {n2}")
content = content.replace(old_strip, new_strip)

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(content)

print("Patched pdf_cleaner.py successfully.")
