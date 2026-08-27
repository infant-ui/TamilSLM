# Security & Code Quality Audit Report

**Scope:** Full codebase — `backend/gateway` (Node/Express), `backend/generation-service`, `backend/retrieval-service`, `backend/correction-service` (FastAPI/Python), `frontend` (React), plus `docker-compose.yml` and Dockerfiles.
**Method:** Direct source review (auth, input handling, injection, error handling, containerization) across all five services. Prior findings in `SYSTEM_AUDIT_REPORT.md` (architecture/tech-debt focused) were cross-checked rather than repeated; this report supersedes it on security specifics and notes where things have changed.
**Out of scope:** the experimental `tamil-llama`, `Cross Lingual Retrieval`, `Mindmap`, `Embedding`, `graphify-*`, and `research` directories, and any file under `node_modules`/`.venv`.

## Executive Summary

The application is functional but was clearly built fast: authentication exists in spots but relies on hardcoded fallback secrets that double as the *actual* credentials the code ships with, CORS is wide open everywhere, and one file (`generation-service/app.py`) contains a full duplicate of itself where the dead half is the fixed version and the live half is the buggy one. The most urgent issues are exploitable today with no special access — a crafted chat response can run script in the browser, and the same hardcoded key unlocks admin routes on two different services. Several of these are the kind of thing that's easy to miss when moving quickly and straightforward to fix.

## Critical Issues (Must Fix)

**1. Unsanitized `dangerouslySetInnerHTML` renders LLM output as raw HTML — stored/reflected XSS**
`frontend/src/App.js:62-66`. `parseBoldAndMath()` takes chat message text, runs it through a KaTeX pass and a `**bold**` → `<strong>` regex, then injects the result via `dangerouslySetInnerHTML` with no sanitization step. The text originates from the tutor LLM's streamed answer (and, upstream, from OCR'd textbook content and the retrieval context), none of which is trusted input. A prompt-injected or malformed model response containing `<img src=x onerror=...>` or a stray `<script>` executes in every user's browser. `react-markdown` is already a project dependency and would render this safely by default — it just isn't used here.
*Fix:* route this content through `react-markdown` (or sanitize the HTML string with DOMPurify) before rendering; stop hand-building HTML strings with regex.

**2. Hardcoded default admin secrets double as real, working credentials**
- `backend/generation-service/app.py:159-160` (and again in the duplicated block at 354-355): `GENERATION_ADMIN_KEYS = { os.environ.get("GENERATION_ADMIN_KEY", "dev-generation-secret-key-123"): "Admin" }`
- `backend/retrieval-service/main.py:189-190`: same pattern with `dev-retrieval-secret-key-123`
- `backend/correction-service/main.py:17-20`: `"test-key-123"` is *always* a valid admin key, unconditionally, regardless of any env var
- `backend/gateway/app.js:161`: hardcodes the literal string `"dev-generation-secret-key-123"` as the header sent to generation-service — i.e. the gateway doesn't read a secret from config at all, it ships the same fallback dev key as source code.

Any deployment that doesn't override every one of these env vars is running with admin access (approve corrections, trigger retrieval cache reloads, generate images) gated by strings that are sitting in the repository. `correction-service`'s `test-key-123` grants access unconditionally even when `CORRECTION_ADMIN_KEY` *is* set.
*Fix:* remove all hardcoded fallbacks — fail to start if the admin-key env var is missing — and have the gateway read its outbound key from its own env var instead of a literal.

**3. Path traversal on the PDF upload endpoint**
`backend/retrieval-service/main.py:407`: `temp_path = os.path.join(temp_dir, file.filename)` uses the client-supplied filename (from the multipart `Content-Disposition` header) directly to build a filesystem path. A filename like `../../../etc/whatever.pdf` writes outside `temp_uploads/`. The endpoint requires the admin key from #2 above, which is the only thing standing between this and being unauthenticated — and that key is a shared default.
*Fix:* sanitize with `os.path.basename(file.filename)` (or a UUID-based name) before joining the path.

**4. `generation-service/app.py` is duplicated top-to-bottom, and the live half is the buggy one**
The entire file — imports, `CORSMiddleware` setup, `/generate/stream`, `/summarize-session`, `GENERATION_ADMIN_KEYS`, `/generate/image`, `/images/{...}` — appears twice (lines 1–209, then again 210–415, plus a second `if __name__ == "__main__"` block at line 343). FastAPI matches routes in registration order, so the routes that actually run are the *first* copy, which has already-fixed bugs still present:
- Live `/generate/image` (line 172-203) calls `enhanced, labels, _, _ = enhance_prompt(...)` and `generate_image(enhanced, labels)`, silently discarding `subject`/`language` — the corrected call signature (`generate_image(enhanced, labels, subject, language)`) only exists in the dead second copy at line 388.
- Live `/images/{year}/{month}/{day}/{filename}` (line 205-209) has no `else` branch, so a missing file falls through and returns `None` instead of a 404 — the dead copy at line 400-405 has the correct `raise HTTPException(404, ...)`.

Anyone reading from the bottom of the file (where most people start when skimming) will believe bugs are fixed that aren't.
*Fix:* delete the entire duplicated block (everything from the second `try: sys.stdout.reconfigure` onward), keeping only the corrected versions.

**5. `frontend` container calls a `gateway` that `docker-compose.yml` never starts**
Every fetch in `App.js` targets `http://localhost:5000` (lines 183, 220, 504, 530, 692, 839, 865, 904, 920) — the gateway's port. `docker-compose.yml` defines `redis`, `generation-service`, `retrieval-service`, `retrieval-worker`, `correction-service`, and `frontend`, but never a `gateway` service. Inside the `frontend` container, `localhost` refers to that container itself, not the host or a sibling container — so under `docker-compose up`, chat, mindmap, uploads, and feedback all fail outright, not just "missing orchestration" as noted in the prior audit, but a full break of every user-facing feature when the stack is run as documented.
*Fix:* add `gateway` to `docker-compose.yml`, and change the frontend's API base to the service DNS name (or an env-injected URL) instead of a hardcoded `localhost`.

## Warnings (Should Fix)

**6. Wide-open CORS on every backend service.** `generation-service`, `retrieval-service` (`allow_origins=["*"], allow_credentials=True`) and the gateway (`app.use(cors())` with no options) accept requests from any origin. `*` + `allow_credentials=True` is actually invalid per the CORS spec and most browsers will reject the combination, but it signals none of these services were ever scoped to a real allowlist — worth locking down before this leaves localhost.

**7. Image generation API payload doesn't match the configured provider.** `backend/generation-service/image/image_service.py` sends a Stability-AI-style payload (`text_prompts`, `cfg_scale`, `steps`) and parses `artifacts[0].base64` from the response, while `.env.example` points `NVIDIA_API_URL` at `https://integrate.api.nvidia.com/v1/images/generations` with `NVIDIA_IMAGE_MODEL=alibaba/qwen-image` — a different API shape entirely. The code's own comment in `app.py` ("Placeholder for actual generation which is pending NVIDIA schema") confirms this is known, unfinished work rather than a new regression — flagging here since it means image generation is likely non-functional against the documented target endpoint.

**8. Developer-machine paths hardcoded into service code.**
- `backend/generation-service/image/prompt_enhancer.py:7`: `GLOSSARY_PATH = r"d:\Project Assistan\glossary_all_classes.csv"` — an absolute Windows path that doesn't exist inside the Linux Docker image built by `generation-service/Dockerfile`. `load_glossary()` just returns early when the path is missing, so this fails silently: labels fall back to English with no error, no log line indicating why.
- `backend/generation-service/image/text_detector.py:14`: hardcodes `C:\Users\YAZHINI\AppData\Local\Programs\Tesseract-OCR\tesseract.exe` — a specific developer's username baked into source, and another path that won't exist in the container or on any other machine.

**9. Blocking synchronous call inside an `async def` endpoint.** `generate_image()` (`image_service.py`) makes a synchronous `requests.post` (up to 3 retries × 60s timeout) and is called directly, un-awaited-in-a-threadpool, from `async def generate_image_endpoint`. This blocks the FastAPI event loop for the full duration — every other concurrent request to `generation-service` stalls. `retrieval-service` gets this right elsewhere (`anyio.to_thread.run_sync` for the reranker), so the fix pattern already exists in the codebase.

**10. No authentication or rate limiting on the expensive/sensitive read paths.** `retrieval-service`'s `/retrieve`, `/retrieve/debug`, `/evaluation/dashboard`, `/feedback`, and every route in the gateway (`/query/stream`, `/query`, `/mindmap/generate`, `/api/upload`, `/api/feedback`) have no auth and no throttling. `/retrieve` runs the full embedding + rerank pipeline (GPU/CPU-heavy) per call — an easy resource-exhaustion vector. `/retrieve/debug` and `/evaluation/dashboard` also return internal system prompts and CPU/RAM/GPU usage to anyone who asks. Only `correction-service`'s `/corrections/report` has a rate limiter, and it's explicitly documented as in-memory/per-process (won't hold under multiple workers or behind a proxy that doesn't forward `X-Forwarded-For`).

**11. User input concatenated into a URL query string.** `retrieval-service/main.py:217`: `requests.get(f"http://127.0.0.1:8002/corrections/lookup?query={req.question}")` interpolates the raw question into the URL instead of using `requests`' `params={"query": req.question}`. Any `&`, `#`, or `%` in a student's question can corrupt or redirect the request.

**12. `correction-service` has zero dependency pinning.** Its Dockerfile runs `pip install --no-cache-dir fastapi uvicorn pydantic` with no `requirements.txt` and no version constraints at all — a step further than the loose `>=` pinning already flagged for the other two services in the prior audit.

**13. Frontend Docker image runs the dev server in "production."** `frontend/Dockerfile`'s `CMD ["npm", "start"]` launches `react-scripts start` (the webpack dev server) rather than building static assets and serving them with something production-appropriate — slower, unoptimized, and not hardened for real traffic.

**14. Redis has no password and is double-exposed to the host.** `docker-compose.yml` maps both `6379:6379` and `6380:6379` to the same Redis container, with no `requirepass`/ACL configured. Anyone who can reach the host on either port can read/write session filters, cached answers, and chat history unauthenticated.

## Nitpicks / Suggestions (Nice to Have)

- **`frontend/src/App.js` is a 1,483-line, 65KB single component.** Worth decomposing — it currently owns chat state, streaming, mindmap jobs, uploads, feedback, and evaluation dashboard rendering all in one file. An identical-sized `App.backup.js` is also tracked in the repo; rely on git history instead of a live backup copy.
- **`frontend/src/features/image-generation/api/imageApi.js` looks orphaned.** It POSTs directly to `generation-service:8001/generate/image` without the `x-generation-service-admin-key` header the endpoint requires, so it would always 401 if actually called from the UI — the working path is the gateway's SSE image branch in `App.js` instead.
- Nested nested ternary in `retrieval-service/main.py:261` (`lang_key = "ta" if (... if ... else ...) else "en"`) is hard to parse at a glance; a couple of `if/elif` lines would read more clearly.
- `Math.random().toString(36)` is used for gateway job IDs (`/mindmap/generate`) — fine since they aren't security tokens, but worth a comment noting that if job IDs are ever treated as an access control (e.g. "only the requester can fetch this job"), this isn't a safe generator for that.
- Stray SQLite test artifacts committed under `backend/correction-service/` (`test_corrections_0.db`, `test_corrections_100.db`, `test_corrections_10000.db`) — repo hygiene, consider a `.gitignore` entry.
- `get_system_resources()` in `retrieval-service/main.py` shells out to `wmic` via `subprocess.check_output(..., shell=True)` as a Windows fallback; the command is a fixed string so it isn't exploitable, but `wmic` is deprecated/removed on newer Windows builds, so this fallback may itself go silently unused.

## Positive Callouts

- **`correction-service` does SQL correctly.** Every query in `corrections_db.py` is fully parameterized — no injection surface — and the module is upfront in its own comments about the tradeoffs of using SQLite for this workload.
- **`retrieval-service`'s admin routes are actually gated.** The prior audit flagged `/upload` and `/reload-cache` as unauthenticated; both now correctly require `verify_retrieval_admin_key` — a real improvement since that audit, even though the key itself still needs hardening (see #2).
- **The mindmap job spawner avoids shell injection deliberately and correctly.** `backend/gateway/app.js` uses `execFile` (not `exec`), sanitizes the language parameter, and validates that the Python executable and script exist before running — exactly the right pattern for shelling out to a script, with a comment explaining why.
- **The image generation safety pipeline is genuinely well thought out for a platform serving minors:** a keyword blocklist, a secondary LLM-based moderation pass that fails closed on error, and a post-generation OCR gate (`contains_hallucinated_text`) that automatically discards and rerolls images containing unwanted embedded text before they reach a student.
- **`.gitignore` is well maintained** — `.env`, `node_modules/`, `.venv/`, model weight files (`*.gguf`, `*.safetensors`, etc.), and generated image output are all correctly excluded, and the `.env.example` files use clearly-labeled placeholders rather than real values.
