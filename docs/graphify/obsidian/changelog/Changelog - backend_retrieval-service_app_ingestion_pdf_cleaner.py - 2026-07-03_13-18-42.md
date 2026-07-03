# Changelog: backend/retrieval-service/app/ingestion/pdf_cleaner.py
**Date:** 2026-07-03_13-18-42
**Type:** Modified

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- `+import logging`

## Diff
```diff
diff --git a/backend/retrieval-service/app/ingestion/pdf_cleaner.py b/backend/retrieval-service/app/ingestion/pdf_cleaner.py
index 08598d8..143cee3 100644
--- a/backend/retrieval-service/app/ingestion/pdf_cleaner.py
+++ b/backend/retrieval-service/app/ingestion/pdf_cleaner.py
@@ -5,6 +5,9 @@ import cv2
 import numpy as np
 import fitz  # PyMuPDF
 from typing import List, Dict, Tuple, Optional
+import logging
+
+logger = logging.getLogger(__name__)
 
 # Constants for layout boundaries
 HEADER_MARGIN_RATIO = 0.08  # top 8%
@@ -65,8 +68,10 @@ class PDFCleaner:
                 if 0.9 <= aspect_ratio <= 1.1 and 40 <= w <= 400 and 40 <= h <= 400:
                     # Return bounding box in pixel coordinates (needs translation to PyMuPDF coords)
                     return (x, y, x + w, y + h)
-        except Exception:
-            pass
+        except cv2.error as e:
+            logger.error(f"OpenCV error detecting QR code: {e}. Skipping QR detection for this image.", exc_info=True)
+        except Exception as e:
+            logger.error(f"Unexpected error detecting QR code: {e}. Skipping QR detection for this image.", exc_info=True)
         return None
 
     def clean_page_text_blocks(self, page: fitz.Page) -> List[Dict]:
@@ -208,8 +213,8 @@ class PDFCleaner:
                         with open(full_path, "wb") as f:
                             f.write(image_bytes)
                         saved_path = full_path
-                except Exception:
-                    pass
+                except Exception as e:
+                    logger.error(f"Failed to extract image {idx} on page {page_no}: {e}. Skipping this figure.", exc_info=True)
 
             elements.append({
                 "type": "figure",  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Backend]]
- [[Home]]
- [[Changelog Index]]
