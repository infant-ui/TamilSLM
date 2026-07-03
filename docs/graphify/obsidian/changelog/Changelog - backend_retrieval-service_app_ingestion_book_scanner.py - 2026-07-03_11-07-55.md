# Changelog: backend/retrieval-service/app/ingestion/book_scanner.py
**Date:** 2026-07-03_11-07-55
**Type:** Modified

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- `+import logging`

## Diff
```diff
diff --git a/backend/retrieval-service/app/ingestion/book_scanner.py b/backend/retrieval-service/app/ingestion/book_scanner.py
index cfa1b29..85734a7 100644
--- a/backend/retrieval-service/app/ingestion/book_scanner.py
+++ b/backend/retrieval-service/app/ingestion/book_scanner.py
@@ -4,8 +4,11 @@ import hashlib
 import json
 from typing import Dict, List, Tuple
 from pydantic import BaseModel
+import logging
 from app.ingestion.metadata_parser import MetadataParser, BookMetadata
 
+logger = logging.getLogger(__name__)
+
 class ScanSummary(BaseModel):
     new_files: List[BookMetadata] = []
     modified_files: List[BookMetadata] = []
@@ -31,8 +34,12 @@ class BookScanner:
             try:
                 with open(self.registry_path, "r", encoding="utf-8") as f:
                     return json.load(f)
-            except Exception:
-                pass
+            except json.JSONDecodeError as e:
+                logger.error(f"Failed to parse manifest {self.registry_path}: {e}. Halting scan to prevent data corruption.", exc_info=True)
+                raise
+            except OSError as e:
+                logger.error(f"Failed to read manifest {self.registry_path}: {e}. Halting scan.", exc_info=True)
+                raise
         return {"last_updated": None, "total_documents": 0, "documents": {}}
 
     def scan(self) -> ScanSummary:  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Backend]]
- [[Home]]
- [[Changelog Index]]
