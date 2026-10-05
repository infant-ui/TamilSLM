# TamilSLM

Building Futures: Nurturing Science and Maths for Rural Area School Children Through Tamil Small Language Model

TamilSLM (TamilEdu-SLM) is a bilingual (Tamil/English) retrieval-augmented tutoring assistant for school Science and Maths, Classes 6 to 8. It answers student questions in Tamil from the Tamil Nadu textbooks, keeps scientific terms bilingual (Tamil term with the English term in brackets), and can generate simple educational images.

## Architecture

| Component | Path | Stack | Role |
|---|---|---|---|
| Frontend | `frontend/` | React | Chat UI with Markdown and KaTeX math rendering |
| Gateway | `backend/gateway/` | Node/Express | Single entry point on port 5000; routes to the services below |
| Retrieval service | `backend/retrieval-service/` | FastAPI, Celery, Redis | Textbook ingestion (PDF cleaning, OCR with Tesseract/Paddle), embeddings, `/retrieve` |
| Generation service | `backend/generation-service/` | FastAPI, Ollama | Streaming answers (`/generate/stream`), session summaries, educational image generation |
| Correction service | `backend/correction-service/` | FastAPI | Collects and reviews user-reported corrections |
| Data | `data/` | | Textbooks, processed chunks, registry |
| Glossary | `data/derived/glossary_outputs/` | CSV | Tamil/English term pairs per class and subject |
| Evaluation | `eval/` | Python | LLM-as-judge vs human scoring (Cohen's kappa) |
| Research | `research/`, `tamil-llama/` | |  Experiments on cross-lingual retrieval, embeddings, and the vendored Tamil-LLaMA project |

## Getting started

1. Copy `.env.example` to `.env` and set every secret (there are no safe defaults; see Security below).
2. Install and start Ollama (port 11434) and pull the models you need.
3. Windows: run `start.bat` (starts Redis, services and frontend; `stop.bat` stops them). Docker: `docker compose up` currently starts only Redis and the generation service.
4. Large research binaries use Git LFS: run `git lfs pull` after cloning.

## Evaluation

The judge pipeline compares `llama3.1` scores with independently authored human scores. Current verified results (see `eval/results/`): messy set quadratic-weighted kappa 0.610 (10 items), large set 0.699 (30 items). The mock-judge pipeline in `eval/deprecated/` is invalid and must not be cited.

## Status and known issues

Functional prototype, not production-ready. From the audits in `docs/audits/`:

- Critical: hardcoded fallback admin keys, XSS via `dangerouslySetInnerHTML` in the chat UI, path traversal in `/upload`, duplicated code in `generation-service/app.py`, unauthenticated `/upload` and `/reload-cache`, incomplete `docker-compose.yml`.
- High: silent `except Exception` blocks in ingestion, loose dependency pinning.
- Medium/low: no automated tests, no health checks.

## Roadmap (see [ROADMAP.md](ROADMAP.md))

1. Remove hardcoded secrets, add auth, sanitize uploads and chat rendering.
2. Orchestrate the full stack in `docker-compose.yml` with health checks.
3. Pin dependencies, fix error handling and logging in ingestion.
4. Add pytest/jest coverage for `/generate` and `/retrieve`.
5. Improve judge calibration (rubric tuning) and expand the evaluation set.

Research directions (rotary-encoder repair and re-embedding, score-normalized fusion, calibrated reranking, Sarvam-M comparison) are listed in ROADMAP.md.

## Repository layout

`backend/`, `frontend/`, `data/`, `eval/`, `research/`, `scripts/`, `docs/` (`audits/`, `reports/`), `tamil-llama/` (vendored upstream), `tessdata/` (Tesseract data).

## License

To be decided (the root LICENSE file is currently empty).
