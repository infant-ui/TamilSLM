# Changelog: docker-compose.yml
**Date:** 2026-07-03_11-13-10
**Type:** Modified

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/docker-compose.yml b/docker-compose.yml
index 17628b5..873c6a0 100644
--- a/docker-compose.yml
+++ b/docker-compose.yml
@@ -29,6 +29,60 @@ services:
     depends_on:
       - redis
     restart: always
+    healthcheck:
+      test: ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8001/docs')\""]
+      interval: 10s
+      timeout: 5s
+      retries: 5
+
+  # 3. FastAPI Retrieval Service
+  retrieval-service:
+    build:
+      context: ./backend/retrieval-service
+      dockerfile: Dockerfile
+    container_name: tamiledu-retrieval
+    ports:
+      - "8000:8000"
+    volumes:
+      - ./data:/data
+    restart: always
+    healthcheck:
+      test: ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')\""]
+      interval: 10s
+      timeout: 5s
+      retries: 5
+
+  # 4. FastAPI Correction Service
+  correction-service:
+    build:
+      context: ./backend/correction-service
+      dockerfile: Dockerfile
+    container_name: tamiledu-correction
+    ports:
+      - "8002:8002"
+    restart: always
+    healthcheck:
+      test: ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8002/docs')\""]
+      interval: 10s
+      timeout: 5s
+      retries: 5
+
+  # 5. React Frontend
+  frontend:
+    build:
+      context: ./frontend
+      dockerfile: Dockerfile
+    container_name: tamiledu-frontend
+    ports:
+      - "3000:3000"
+    depends_on:
+      retrieval-service:
+        condition: service_healthy
+      generation-service:
+        condition: service_healthy
+      correction-service:
+        condition: service_healthy
+    restart: always
 
 volumes:
   redis_data:  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Root]]
- [[Home]]
- [[Changelog Index]]
