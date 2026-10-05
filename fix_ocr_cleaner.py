import io

path = "backend/retrieval-service/app/ingestion/ocr_cleaner.py"

with io.open(path, "r", encoding="utf-8", newline="") as f:
    content = f.read()

old = (
    "        # Crop the bounding box area from the page\r\n"
    "        rect = fitz.Rect(bbox)\r\n"
    "        # Zoom in for better OCR accuracy (2x resolution)\r\n"
    "        pix = page.get_pixmap(clip=rect, matrix=fitz.Matrix(2, 2))\r\n"
    "        \r\n"
    "        # Convert to PIL Image\r\n"
    "        img_data = Image.frombytes(\"RGB\", [pix.width, pix.height], pix.samples)\r\n"
)

new = (
    "        # Crop the bounding box area from the page\r\n"
    "        rect = fitz.Rect(bbox)\r\n"
    "        # Zoom in for better OCR accuracy (2x resolution)\r\n"
    "        pix = page.get_pixmap(clip=rect, matrix=fitz.Matrix(2, 2))\r\n"
    "        \r\n"
    "        # Guard against a degenerate (zero-width/zero-height) crop: a malformed\r\n"
    "        # or mis-detected bbox (e.g. from figure/table extraction on page 1 of\r\n"
    "        # Class_6_Mathematics_English_Mathematics_-_Term_2.pdf, confirmed via two\r\n"
    "        # reproductions) yields a pixmap with a zero dimension, which crashes\r\n"
    "        # PaddleOCR's native inference below at the C++ level with no catchable\r\n"
    "        # Python exception. Skip OCR entirely for a degenerate box instead.\r\n"
    "        if pix.width <= 0 or pix.height <= 0:\r\n"
    "            return \"\", 0.0\r\n"
    "        \r\n"
    "        # Convert to PIL Image\r\n"
    "        img_data = Image.frombytes(\"RGB\", [pix.width, pix.height], pix.samples)\r\n"
)

count = content.count(old)
if count != 1:
    raise SystemExit(f"Expected exactly 1 match, found {count}. Aborting without writing.")

content = content.replace(old, new)

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(content)

print("Patched ocr_cleaner.py successfully.")
