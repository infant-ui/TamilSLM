# TamilEdu-SLM Evaluation Suite

This folder is a standalone, isolated evaluation harness. **Nothing in `backend/`
or `frontend/` was modified to build it.** It reads your real cached indices
and (optionally) calls your real running services; it does not change them.

## What's here

```
evaluation/
├── datasets/
│   ├── build_dataset.py     # generates gold_dataset.json; regenerate after editing
│   └── gold_dataset.json    # 49 core Q&A + 7 language-instruction + 6 out-of-scope items
├── scripts/
│   ├── metrics.py                    # verbatim copy of app/evaluation/metrics.py
│   ├── evaluate_retrieval_bm25.py    # runs anywhere (numpy only) -- real BM25 index, real chunks
│   ├── evaluate_retrieval_full.py    # needs your venv -- real dense+BM25+RRF+reranker pipeline
│   ├── evaluate_generation.py        # needs your venv + Ollama + live services -- real answers + LLM judge
│   └── evaluate_all.py               # orchestrates the above, writes final_report.json
└── results/                          # created on first run
```

## Why the dataset is small and Class-6-Science-only

Your live serving cache (`data/processed/cache/{english,tamil}_chunks.pkl`)
currently contains **only Class 6 Science** content (396 English chunks, 127
Tamil chunks). Class 7/8 Science and every Maths PDF under `data/books/` exist
on disk but were never embedded into the index that `main.py` actually loads.
Every gold question here was written against passages verified, by directly
unpickling the cache, to exist in that index -- so retrieval scores measure
real retrieval quality, not an artifact of asking about content that was
never indexed. The `out_of_scope` items exist specifically to probe that gap
on purpose (see "Interpreting results" below).

## Running it

### 1. Retrieval, BM25-only (works anywhere, no setup)
```
python evaluation/scripts/evaluate_retrieval_bm25.py
```

### 2. Retrieval, full hybrid pipeline (dense + BM25 + RRF + reranker)
Needs your project's own venv (sentence-transformers/torch installed, GTE
models already cached from prior use):
```
.\.venv\Scripts\python.exe evaluation\scripts\evaluate_retrieval_full.py
```

### 3. Generation + LLM-judge (needs the live stack running)
Start these two (same as `start.bat` does, gateway/Redis/frontend not needed):
```
cd backend\retrieval-service   &&  ..\..\.venv\Scripts\python.exe -m uvicorn main:app --port 8000
cd backend\generation-service  &&  ..\..\.venv\Scripts\python.exe -m uvicorn app:app --port 8001
```
Make sure Ollama Desktop is running with `qwen2.5:7b-instruct-q4_k_m` pulled.
For a less self-graded judge, also `ollama pull llama3.1` (the script prefers
it automatically if present; otherwise it judges qwen with qwen and says so
in the output).
```
.\.venv\Scripts\python.exe evaluation\scripts\evaluate_generation.py
```
Add `--limit 10` for a quick smoke run before committing to the full ~100
live calls (49 core x up to 2 toggles + 6 out-of-scope x up to 2 toggles).

### 4. Everything at once
```
.\.venv\Scripts\python.exe evaluation\scripts\evaluate_all.py --with-full --with-generation
```

## Interpreting results

- **`recall_5`, `mrr`, `ndcg_5`, etc.** follow the exact formulas in
  `app/evaluation/metrics.py` (verified correct for binary, page-level
  relevance -- see final report for the one caveat: they operate on page
  numbers, not chunk identity, so two chunks sharing a page count as one hit).
- **Bilingual / Tanglish items report against BOTH the English and Tamil
  corpus separately**, plus a `best_of_either_corpus` figure. There is no
  single correct answer for which corpus a code-mixed query should hit --
  that choice is made by the UI's language toggle
  (`gateway/app.js` `preferred_medium`), not by the query's own text. The
  gap between the two numbers *is* the measurement: it's how much retrieval
  quality swings purely on which toggle position a bilingual-speaking
  student happens to have selected.
- **`out_of_scope` items must never be scored as retrieval failures.** They
  exist to check *abstention behaviour* (does the system say "not in the
  textbook" / refuse the false premise, or does it fabricate an answer, or
  does it silently serve back same-subject content from a different grade as
  if it answered the question asked). Score them via the `judge.abstained`
  and `judge.hallucination` fields in `generation_results.json`, never via
  recall/precision.
- **`evaluate_retrieval_full.py` also prints a one-line diagnostic** showing
  the CrossEncoder reranker's raw output range on a trivially-matching pair.
  Compare it against the hardcoded `threshold = 0.35` in
  `app/retrieval/reranker.py` -- if the raw scores aren't roughly in [0, 1],
  that threshold is filtering on an uncalibrated scale.

## Regenerating / extending the dataset

Edit `datasets/build_dataset.py`, then re-run it. If you add a new question,
**verify the passage exists in the pickled chunk cache first** (open a Python
shell, `pickle.load` the relevant `*_chunks.pkl`, and search for it) --
this whole suite exists to avoid trusting documentation, folder names, or the
`data/registry/manifest.json` (which is itself stale for several Class 6
Science documents -- see final report) over what's actually indexed.
