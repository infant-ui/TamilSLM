# System Engineering Audit Report

This document contains a comprehensive, read-only system engineering audit of the repository, highlighting discrepancies between the documented architecture and actual code, assessing tech debt, and providing a prioritized list of findings.

## 1. Architecture Overview
**Findings:** There is a significant mismatch between the documented architecture and the reality of the codebase.
- **Documented:** The Graphify KB (`System Architecture`, `Folder Structure`) claims a unified system.
- **Actual Code:** The repository contains several disjointed sub-projects: `backend/` (which itself is split into microservices: `gateway`, `generation-service`, `retrieval-service`, `correction-service`, `models`), `frontend/` (a React application), and massive experimental ML directories (`tamil-llama`, `Cross Lingual Retrieval`).
- **Deployment Mismatch:** The `docker-compose.yml` file only orchestrates `redis` and `generation-service`. The `frontend`, `gateway`, `correction-service`, and `retrieval-service` are completely missing from the container orchestration, meaning there is no unified way to run the full stack locally or in production.

## 2. Dependency & Version Health
**Findings:** Dependency management is loose and prone to breakage.
- **Python (backend):** `backend/generation-service/requirements.txt` uses loose `>=` pinning (e.g., `fastapi>=0.100.0`, `Pillow>=10.0.0`). This exposes the build to future breaking changes in upstream libraries.
- **Node.js (gateway & frontend):** Uses `^` versioning (e.g., `"express": "^5.2.1"`). While standard, lockfiles must be strictly committed.
- **Missing Test Dependencies:** There are no testing frameworks (`pytest`, `jest`, etc.) declared in any of the requirements files or `package.json` devDependencies.

## 3. Configuration & Secrets
**Findings:** 
- A full-history deep scan of the git repository was attempted but overwhelmed by the massive `graphify-out` cache data (over 470,000 lines of JSON). 
- In the active codebase, environment variables like `OLLAMA_HOST` and `REDIS_HOST` are passed via `docker-compose.yml`, but there is no centralized `.env.example` or documentation on required secrets for the other un-orchestrated services (`retrieval-service`, `gateway`).

## 4. API Surface Review
**Findings:** Critical security gap.
- Across the `backend/` services, numerous routes are exposed without any authentication decorators (e.g., `@requires_auth`).
- **`retrieval-service/main.py`:** Exposes `/retrieve`, `/reload-cache`, `/feedback`, `/upload`, and `/retrieve/debug`. The `/upload` and `/reload-cache` endpoints are highly sensitive and currently unauthenticated.
- **`generation-service/app.py`:** Exposes `/generate/stream`, `/summarize-session`, `/generate/image`.
- **`correction-service/main.py`:** Exposes `/corrections/report`, `/corrections/review/{report_id}`.

## 5. Data & Model Pipeline Integrity
**Findings:** Silent failure paths detected.
- The `retrieval-service` (specifically in `app/ingestion/pdf_cleaner.py`, `book_scanner.py`, and `evaluator.py`) uses bare `except Exception:` blocks. If PDF parsing or OCR fails, these blocks swallow the exception silently, potentially causing pipelines to proceed with corrupted or empty data.

## 6. Error Handling & Logging Consistency
**Findings:** 
- Error handling is inconsistent. The presence of silent `except` blocks in the ingestion pipeline contrasts heavily with standard FastAPI error raising. 
- There is no unified centralized logging configuration (like a standard Python `logging.conf` or a structured JSON logger) across the different microservices.

## 7. Testing Coverage
**Findings:** Zero critical path coverage.
- There are no `tests/` directories or `test_*.py` files in the core `backend/` microservices or `frontend/src`.
- The `graphify-repo` contains its own tests (`test_multilang.py`), but the actual application code (Generation, Retrieval, Correction) has no automated tests.

## 8. Technical Debt & Known Issues
**Findings:** Documentation drift.
- The Graphify KB generated a `TODO.md` page, but a regex search for `TODO` and `FIXME` across the `backend/` and `frontend/` source code returned **0 results**. This means either developers are not tracking tech debt in code, or the documented issues in the Obsidian vault are completely disconnected from the actual implementation.

## 9. Build & Deployment Reliability
**Findings:** Incomplete containerization.
- The `docker-compose.yml` is incomplete (missing 4 out of 5 services).
- Base images in Dockerfiles (where they exist) likely lack explicit SHA pinning.
- There are no health checks (`HEALTHCHECK`) defined in the `docker-compose.yml` for Redis or the generation service.

## 10. Prioritized Findings

1. **[CRITICAL] Unauthenticated Admin Routes**
   - **Fix:** Implement a JWT or API Key auth middleware and apply it to `/upload` and `/reload-cache` in `retrieval-service/main.py`.
   - **Effort:** Medium
2. **[CRITICAL] Incomplete Docker Orchestration**
   - **Fix:** Add `gateway`, `retrieval-service`, `correction-service`, and `frontend` to `docker-compose.yml` so the entire stack can boot together.
   - **Effort:** Large
3. **[HIGH] Silent Exception Swallowing in Ingestion**
   - **Fix:** Replace `except Exception:` with specific exception catches and add `logger.error()` in `backend/retrieval-service/app/ingestion/*.py`.
   - **Effort:** Small
4. **[HIGH] Loose Dependency Pinning**
   - **Fix:** Freeze `requirements.txt` using exact versions (`==`) instead of `>=` to prevent unexpected pipeline breaks.
   - **Effort:** Small
5. **[MEDIUM] Zero Test Coverage for Core Services**
   - **Fix:** Introduce `pytest` and write basic unit tests for the `/generate` and `/retrieve` FastAPI endpoints.
   - **Effort:** Large
6. **[LOW] Missing Health Checks**
   - **Fix:** Add `healthcheck` blocks to `docker-compose.yml` for all services to ensure they restart if frozen.
   - **Effort:** Small
