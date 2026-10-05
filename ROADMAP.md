# Roadmap

## Engineering hygiene (from `docs/audits/`)

| # | Item | Severity | Effort |
|---|---|---|---|
| 1 | Remove hardcoded fallback admin keys (generation, retrieval, correction, gateway); fail on missing env vars. Add auth to `/upload` and `/reload-cache`. Sanitize upload filenames. Sanitize chat rendering (`dangerouslySetInnerHTML`). | Critical | Medium |
| 2 | Remove the duplicated block in `backend/generation-service/app.py`, keeping the corrected versions. | Critical | Small |
| 3 | Add `gateway`, `retrieval-service`, `correction-service` and `frontend` to `docker-compose.yml`, with health checks and a service-DNS API base for the frontend. | Critical | Large |
| 4 | Replace bare `except Exception:` in `retrieval-service/app/ingestion/*.py` with specific catches and logging. | High | Small |
| 5 | Pin dependencies exactly in `requirements.txt`. | High | Small |
| 6 | Add pytest/jest coverage for `/generate` and `/retrieve`. | Medium | Large |
| 7 | Improve judge calibration (rubric tuning) and grow the evaluation set. | Medium | Medium |

## Research (Future Work from the IConSCEPT paper)

Taken from the paper's conclusion as summarized by the project owner; confirm wording against the paper.

- Repair the rotary encoder and re-embed the corpus.
- Replace the fixed cross-corpus interleave with genuine score-normalized fusion.
- Fix the chunk-identifier bug at the source.
- Learned, confidence-calibrated reranking policy.
- Extend the generation comparison to Sarvam-M.
- Per-model token-count auditing methodology.
- Validate the judge against human raters.
