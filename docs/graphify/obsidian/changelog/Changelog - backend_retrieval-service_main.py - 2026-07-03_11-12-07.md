# Changelog: backend/retrieval-service/main.py
**Date:** 2026-07-03_11-12-07
**Type:** Modified

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- `-from fastapi import FastAPI, HTTPException, UploadFile, File, Form`
- `+from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Header, Depends`

## Diff
```diff
diff --git a/backend/retrieval-service/main.py b/backend/retrieval-service/main.py
index a1a219c..0f3dd97 100644
--- a/backend/retrieval-service/main.py
+++ b/backend/retrieval-service/main.py
@@ -10,7 +10,7 @@ import shutil
 import anyio
 from datetime import datetime
 from typing import Optional, List
-from fastapi import FastAPI, HTTPException, UploadFile, File, Form
+from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Header, Depends
 from fastapi.middleware.cors import CORSMiddleware
 from sentence_transformers import SentenceTransformer
 from contextlib import asynccontextmanager
@@ -186,6 +186,16 @@ app.add_middleware(
     allow_headers=["*"],
 )
 
+RETRIEVAL_ADMIN_KEYS = {
+    os.environ.get("RETRIEVAL_ADMIN_KEY", "dev-retrieval-secret-key-123"): "Admin"
+}
+
+def verify_retrieval_admin_key(x_retrieval_service_admin_key: Optional[str] = Header(None)) -> str:
+    if not x_retrieval_service_admin_key or x_retrieval_service_admin_key not in RETRIEVAL_ADMIN_KEYS:
+        raise HTTPException(status_code=401, detail="Unauthorized - Invalid or missing admin key")
+    return RETRIEVAL_ADMIN_KEYS[x_retrieval_service_admin_key]
+
+
 @app.post("/retrieve", response_model=RetrieveResponse)
 async def retrieve(req: RetrieveRequest):
     t_start = time.time()
@@ -265,7 +275,7 @@ async def retrieve(req: RetrieveRequest):
     )
 
 @app.post("/reload-cache")
-async def reload_cache():
+async def reload_cache(admin: str = Depends(verify_retrieval_admin_key)):
     """
     Triggers re-loading of chunks and embeddings caches in-memory without downtime.
     """
@@ -376,7 +386,8 @@ async def upload_book(
     subject: Optional[str] = Form(None),
     medium: Optional[str] = Form(None),
     content_type: Optional[str] = Form(None),
-    term: Optional[int] = Form(None)
+    term: Optional[int] = Form(None),
+    admin: str = Depends(verify_retrieval_admin_key)
 ):
     """
     Unified PDF upload system:  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Backend]]
- [[Home]]
- [[Changelog Index]]
