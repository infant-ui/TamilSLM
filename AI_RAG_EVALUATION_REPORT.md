# Comprehensive Evaluation: Tamil–English Educational RAG System (TamilEdu-SLM)

**Evaluation date:** 2026-09-15 (original), **updated 2026-09-16**
**Evaluated by:** Code-level inspection of the actual repository + real, executed BM25 retrieval runs against the live cached index. No score in this report is estimated or assumed unless explicitly labeled "not currently measurable."
**Scope of what was executed live:** BM25 sparse-retrieval evaluation (real data, real production algorithm, executed and reported below — now against the full 28-book corpus, see Section 0). Dense retrieval, reranking, and generation evaluation are delivered as ready-to-run scripts in `evaluation/` (see "Reproducibility" below) — this evaluation runs in a sandbox with no network egress and no access to your local GPU/Ollama/venv, so those stages could not be executed from here. Run `evaluate_all.py --with-full --with-generation` on your machine to complete the picture (see Section 0 for the exact command).

---

## 0. UPDATE (2026-09-16) — Full 28-Book Corpus Rebuild

**Everything below this section describes the system as of 2026-09-15, when the live index covered only Class 6 Science (523 chunks total).** Since then, at your request, the entire corpus was re-ingested from raw PDFs to cover the full curriculum. This section summarizes what changed; the rest of the report is left as the original, dated record, with pointer notes added at the specific sections whose numbers/scope claims this update supersedes.

**0.1 — Corpus now covers all 28 books.** `data/registry/manifest.json` and the pickled chunk caches now show:

| | Before (2026-09-15) | After (2026-09-16) |
|---|---:|---:|
| Books indexed | 1 (Class 6 Science) | 28 (Class 6/7/8 × Maths/Science × English/Tamil, all applicable terms) |
| English chunks | 396 | 3,583 |
| Tamil chunks | 127 | 3,843 |
| Total chunks | 523 | 7,426 |

This directly resolves the Section 1/2 finding that "the live index covers only Class 6 Science" and that 2 of the 4 `benchmark_dataset.json` questions and several `out_of_scope` gold-dataset items tested a coverage gap rather than retrieval quality (Finding 4.5, Section 12).

**0.2 — Two real bugs were found and fixed during re-ingestion (not previously documented):**
- **Class 8 folder-layout bug.** The Class 8 books lived in a different on-disk folder layout (`class_8/<medium>/textbooks/<subject>/file.pdf`) than Class 6/7's convention (`class_<n>/<subject>/<medium>/textbook/file.pdf`). `MetadataParser.parse_from_filename()`'s path-segment logic (already documented as fragile in the original Finding 4.4) would have silently mis-derived subject/medium/term for all 4 Class 8 books had this not been caught and fixed *before* the reindex, by moving the files to match the established convention. Verified afterward: all Class 8 entries show correct `term: 0`, subject, and medium in the manifest.
- **A native (non-Python-catchable) crash during OCR.** `app/ingestion/ocr_cleaner.py`'s `perform_ocr_on_bbox()` passed a zero-width/zero-height PDF crop region straight into `page.get_pixmap()` → PaddleOCR inference, which segfaults on degenerate input with no Python exception to catch — this reliably killed the ingestion run at the same book/page every time. Fixed with a one-line guard (`if pix.width <= 0 or pix.height <= 0: return "", 0.0`) immediately after the pixmap is created; verified by `py_compile` and by the subsequent full 28-book run completing past the exact previous crash point.

**0.3 — Tamil text-extraction corruption (Finding 4.6) is now precisely characterized, and its fix's real impact is measured.** Reading curated text extractions from all 28 books surfaced three distinct corruption mechanisms in Tamil-medium PDFs, not one:
1. Split vowel-sign glyphs (already partially handled by the existing `normalize_tamil_unicode()`).
2. Raw C0 control codes and U+FFFD replacement characters where a glyph had no Unicode mapping in the source PDF's font.
3. **Systematic consonant/matra duplication** (e.g. `ககோடிட்்ட` for `க�ோடிட்ட`) — this is the dominant, highest-volume corruption pattern, and it has **no known text-level fix**: it would require reverse-engineering the specific broken font's glyph-to-Unicode mapping, not a Unicode-normalization pass.

A fix for mechanisms (1) and (2) was implemented (`app/ingestion/text_utils.py`, wired into `pdf_cleaner.py`'s `clean_page_text_blocks()`) and its impact was **measured before being relied on**, rather than assumed: it recovered only **1.1 percentage points** of previously-unusable Tamil chunks (386 → 428 "good" chunks out of the corpus sampled, 10.0% → 11.1%). Mechanism (3) — the dominant one — remains unfixed. Concretely, per-book "usable prose" coverage found while building the new gold dataset (Section 0.4):

| Book | Tamil prose usable? |
|---|---|
| Class 6/7 Maths (all terms) | Yes — garbled but legible; numeric/formula content survives well |
| Class 8 Maths | Yes — same pattern |
| Class 6 Science T2 | Glossary-only (glossary pages are clean; prose is not) |
| Class 6 Science T1/T3 | No — effectively empty |
| Class 7 Science (all terms) | No — effectively empty (1-2 usable chunks per term) |
| Class 8 Science | Glossary-only |

**Recommendation unchanged from the original Priority 1 item, now sharpened:** the fix that would actually move the needle is forcing OCR for Tamil-medium documents regardless of whether PyMuPDF reports the page as "searchable" (native text extraction is what's hitting the broken font's CMap; OCR reads the rendered glyphs directly and would sidestep the encoding problem for mechanisms 1-3 alike). This has not been implemented — it's a larger pipeline change than the one-line guard fixes above, and was deliberately deferred (see 0.4) rather than run as another costly full reindex on a hypothesis. It should be Priority 1 in Section 20's roadmap, above the metadata fixes now that this quantification exists.

**0.4 — The gold evaluation dataset was rebuilt (v1.0.0 → v2.0.0) to proportionally cover the new corpus**, per your explicit direction to build the dataset now on current data rather than block further on the Tamil fix above:
- `evaluation/datasets/build_dataset.py` / `gold_dataset.json`: **49 → 156 CORE items**, all newly-added items grounded in content read directly from curated per-book text extractions of the live post-reindex corpus (not assumed, not copied from the PDFs blind). Breakdown: 108 English, 25 Tamil, 14 bilingual, 9 Tanglish; 90 Class 6 items, 45 Class 7, 21 Class 8; every item now also tags ground-truth `subject` (science/maths).
- `language_instruction` probes: 7 → 8 (added a Maths-specific example; all 7 original ones were Science-only).
- `out_of_scope` items: the 3 original items testing "Class 7/8 not indexed" and "Maths not indexed" are **removed** (now false) and replaced with genuinely-absent topics confirmed absent while reading all 28 books in full: content above Class 8 level, calculus (not in the TN Class 6-8 syllabus), and Bohr's-model-level atomic physics (the corpus's atomic structure content stops at Dalton/Thomson/valency arithmetic). The false-premise and unrelated-concept-combination items are unchanged.
- Tamil Science coverage in the new items is intentionally thin (vocabulary/glossary questions only, per 0.3's findings) rather than padded with items the corpus can't actually answer — this under-representation is a **measurement of a real corpus limitation**, not an oversight, and is documented as such in the dataset file's own header.

**0.5 — A latent bug in the evaluation tooling itself was found and fixed while re-running BM25 against the expanded dataset.** `evaluate_retrieval_bm25.py`'s `filter_candidate_indices()` carried a comment stating subject filtering was safely omitted "because 100% of the currently indexed corpus is metadata `subject=='science'`" — true on 2026-09-15, **false** as of the reindex, since the corpus now has Maths alongside Science for every class/term. Left unfixed, every new Maths gold-dataset item would have been scored against a candidate pool contaminated with same-class-and-term Science chunks (and vice versa), silently distorting every new item's recall/precision numbers. Fixed to filter by ground-truth subject (verified against the real production `HybridRetriever.filter_candidates`, which does filter by subject via a keyword-based `detect_subjects()` — see `hybrid_retriever.py:110-206`); term-filtering was also corrected to explicitly mirror production's Class-8-requires-`term==0` rule rather than relying on it working by coincidence.

**0.6 — Fresh BM25 baseline results, full corpus + expanded dataset** (`evaluation/results/retrieval_bm25_results.json`, executed 2026-09-16, same standalone numpy-only method as the original Section 9 run — see that section's method note, which still applies verbatim):

| Language | n | Recall@1 | Recall@3 | Recall@5 | Recall@10 | Precision@5 | MRR | nDCG@5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| English | 108 | 0.685 | 0.898 | 0.926 | 0.981 | 0.231 | 0.793 | 0.925 |
| Tamil | 25 | 0.200 | 0.600 | 0.600 | 0.640 | 0.128 | 0.384 | 0.403 |
| Bilingual vs EN corpus | 14 | 0.071 | 0.714 | 0.786 | 1.000 | 0.157 | 0.338 | 0.416 |
| Bilingual vs TA corpus | 14 | 0.071 | 0.071 | 0.143 | 0.214 | 0.029 | 0.125 | 0.090 |
| Tanglish vs EN corpus | 9 | 0.222 | 0.778 | 0.778 | 1.000 | 0.222 | 0.531 | 0.649 |
| Tanglish vs TA corpus | 9 | 0.000 | 0.000 | 0.111 | 0.111 | 0.022 | 0.035 | 0.026 |

**Reading these against the original Section 9 numbers (49-item, Class-6-Science-only dataset):** the core finding is unchanged and now more robustly evidenced at 3x the sample size across 3x the grade levels and both subjects — English retrieval is strong (Recall@5 92.6%, up slightly from 90.0%, now proven across Maths *and* Science, all three grades), Tamil retrieval is markedly weaker (Recall@5 60.0%, down from 58.3% — statistically the same, now on a larger and more representative sample) with the gap directly attributable to the text-corruption finding in 0.3, and the bilingual/Tanglish toggle-routing problem (Section 7) persists essentially unchanged (Recall@5 against the "wrong" corpus is still in the 11-21% range vs. 78-79% against the "right" one). **This is still a BM25-only lower bound** — the dense+reranker+generation stages still require your local venv/GPU/Ollama and could not be run from this sandbox; see the Cowork prompt below.

**0.7 — Still pending, and blocked on your local machine (not on anything in this sandbox):**
- Run the full hybrid+reranker retrieval eval and the live generation+judge eval against the new corpus and new 156-item dataset:
  ```
  cd backend\retrieval-service
  ..\..\.venv\Scripts\python.exe ..\..\evaluation\scripts\evaluate_all.py --with-full --with-generation
  ```
  (run from the repo root is also fine: `.\.venv\Scripts\python.exe evaluation\scripts\evaluate_all.py --with-full --with-generation`). This will overwrite the stale `evaluation/results/{retrieval_full_results.json, generation_results.json, final_report.json}` currently on disk, which were produced on 2026-09-16 *before* the reindex finished and are against the old 49-item/523-chunk state — **do not cite those three files' current contents; they predate this update.**
- Once that's run, Sections 5-14, 17, and 21 of this report should be rewritten against the real numbers rather than the 2026-09-15 baseline — flagged inline below at each affected section.
- Implementing the force-OCR-for-Tamil fix discussed in 0.3, if you decide the ~1.1pt partial fix isn't sufficient (it likely isn't, given mechanism 3's dominance).

---

## 1. Executive Summary

> **⚠ Superseded in part — see Section 0.** Point 1 below ("live index covers only Class 6 Science") was true on 2026-09-15 and is **no longer true**: the corpus was fully rebuilt on 2026-09-16 to cover all 28 books. Points 2 and 3 (bilingual/Tanglish toggle routing, broken chapter/section metadata) remain accurate and unchanged.

The system is a real, working, microservice RAG pipeline (gateway → retrieval-service → generation-service → correction-service), not a prototype in name only — the retrieval and generation code paths execute, and the BM25 stage was run end-to-end against your actual data during this evaluation. But three structural facts limit how far any quality claim about it can currently reach:

1. **The live index covers only Class 6 Science** (396 English chunks, 127 Tamil chunks). Class 7/8 Science and every Mathematics document under `data/books/` sit on disk unembedded. Any evaluation — including 2 of the 4 questions in the project's own `benchmark_dataset.json` — that assumes broader coverage is testing a gap that has nothing to do with model or retrieval quality.
2. **Code-mixed (bilingual/Tanglish) query handling is not implemented as a first-class concern anywhere in the pipeline.** Language routing is a client-side UI toggle; the only text-based language signal in the code is a one-line check for the presence of any Tamil Unicode character, used only to choose a prompt template, not to route retrieval. The real, measured consequence (Section 7) is a 50+ percentage-point swing in Recall@5 depending purely on which toggle position a bilingual-speaking student happens to have selected — not on anything about their question.
3. **Structural metadata (chapter, section) is broken across effectively 100% of the indexed corpus**, traced to a specific, fixable root cause in `chapter_parser.py` (Section 4). This doesn't stop retrieval from finding the right text, but it does mean every citation, every "Chapter: X" label shown to the LLM and (via chunk metadata) potentially to students, is wrong.

None of this is a criticism of the choice of embedding model, reranker, or LLM. **Every clearly severe issue found here is in the data/metadata/orchestration layer, not the model layer** — which is good news, because it means the fixes are tractable and don't require fine-tuning (see Section 19, "Do not recommend fine-tuning automatically").

---

## 2. Actual System Architecture (verified from code, not documentation)

```
Browser (React, frontend/)
   │  POST /query/stream  { query, language, preferred_medium, class_id, term, ... }
   ▼
Gateway  (backend/gateway/app.js — Node/Express)
   │  1. Deterministic keyword intent router (Image if query contains "diagram"/"படம்"/etc.)
   │  2. Session filters (class/term/medium) cached in Redis or in-memory fallback
   │  3. POST /retrieve  →  Retrieval Service
   ▼
Retrieval Service  (backend/retrieval-service/main.py — FastAPI)
   │  0. Correction Service lookup (exact/keyword-overlap override, 0.5s timeout)
   │  1. Encode query: Alibaba-NLP/gte-multilingual-base (single model instance shared
   │     for BOTH "ta_model" and "en_model" — see main.py:163-164)
   │  2. HybridRetriever: dense cosine (brute-force numpy/sklearn over cached .npy
   │     arrays — there is NO FAISS, Qdrant, or any ANN index anywhere in this repo,
   │     despite the term "vector database" appearing in the prompt/doc language)
   │     + BM25 (hand-rolled SimpleBM25, in-memory) + Reciprocal Rank Fusion (k=60)
   │     + source-priority merge (textbook/guide first, PYQ/notes supplement)
   │  3. CrossEncoderReranker: Alibaba-NLP/gte-multilingual-reranker-base,
   │     hardcoded threshold 0.35 (calibration unverified — see Section 11)
   │  4. PromptBuilder: builds a full system+user prompt server-side (grade level,
   │     subject, exam/practice/math mode, grounding-confidence prefix, language
   │     template) and returns it as a diagnostic field — the LLM prompt is built
   │     once here, not in the generation service.
   ▼ (system_prompt, context chunks) returned to Gateway
   │  Gateway concatenates chunk texts as `context`, forwards to Generation Service
   ▼
Generation Service  (backend/generation-service/app.py — FastAPI)
   │  POST /generate/stream → Ollama HTTP API (localhost:11434)
   │  model = "qwen2.5:7b-instruct-q4_k_m" (hardcoded), temperature=0.2,
   │  num_predict=1000, num_ctx=4096, stream=True (SSE)
   ▼
Gateway relays SSE tokens to browser; caches full answer in Redis (24h) + session history (last 6 turns)
```

Supporting pieces:
- **Correction Service** (`backend/correction-service`): FastAPI + SQLite. Humans report issues → admin approves a canonical correction → future matching queries get the correction injected as a system-prompt override *before* retrieval even runs. Matching is keyword-overlap (≥2 shared non-stopword tokens, or substring containment) — no embeddings. Its stopword list is English-only (`{"is","the","of","a",...}`); nothing is stripped for Tamil, and Tamil's more agglutinative tokenization means fewer, longer tokens per query, so this matcher is structurally easier to trigger for English reports than Tamil ones.
- **Ingestion pipeline** (`app/ingestion/*`): PyMuPDF text extraction → layout analysis → OCR fallback (Tesseract / PaddleOCR, GPU-gated) → Tamil Unicode repair pass → chapter/section parsing → word-count-based chunking (500 words, 75-word overlap) → embedding → Celery background task on `/upload`.
- **Image generation** lives in `generation-service` too (NVIDIA NIM API, `alibaba/qwen-image` model) — a separate concern from text QA, gated by intent-keyword routing in the gateway.

**Nothing here is a language model fine-tune.** A separate `tamil-llama/` directory contains a full conda export for what looks like an abandoned QLoRA/PEFT fine-tuning experiment (`peft`, `bitsandbytes`, `trl`, `autotrain-advanced`, `flash-attn`) — it is not imported or referenced by anything in `backend/`, and the live system runs stock `qwen2.5:7b-instruct-q4_k_m` via Ollama.

---

## 3. Model and Pipeline Analysis (stage by stage)

| Stage | Actual library/model | Config found in code | Notes |
|---|---|---|---|
| Embedding | `Alibaba-NLP/gte-multilingual-base` via `sentence-transformers` | `trust_remote_code=True`, device auto-selected by a hardware-tier detector, a manual `position_ids` patch applied at load (main.py:151-161) — patch existing at all implies the base model has a known bug/quirk on some torch versions | One model instance shared for Tamil and English (`main.py:163-164`); this is fine (it *is* the multilingual model) but means Tamil-specific fine-tuning of the embedder is not happening anywhere |
| Sparse retrieval | Hand-written `SimpleBM25` (`hybrid_retriever.py`) | k1=1.5, b=0.75 (standard defaults), tokenizer = `\b\w+\b` lowercase (Unicode-aware, so it does tokenize Tamil, just naively — no stemming/normalization) | O(query_terms × corpus_size) score loop — fine at 523 total chunks, would not scale past a few thousand |
| Fusion | Reciprocal Rank Fusion, k=60 | Standard formula, correctly implemented | — |
| Dense search | Brute-force cosine similarity (`sklearn.metrics.pairwise.cosine_similarity`) over the full filtered embedding matrix | No FAISS/Qdrant/Annoy/HNSW anywhere in the codebase | Fine at this corpus size; would not scale, and "vector database" language elsewhere in project docs is aspirational, not implemented |
| Reranker | `Alibaba-NLP/gte-multilingual-reranker-base` via `CrossEncoder` | hardcoded `threshold = 0.35` | **Unverified**: whether `CrossEncoder.predict()` returns a calibrated [0,1] probability or a raw logit depends on the installed `sentence-transformers` version and the model's own config, and `retrieval-service/requirements.txt` pins neither. `evaluate_retrieval_full.py` (delivered) prints the raw score on a trivially-correct pair the first time you run it — check that number against 0.35 before trusting anything downstream of the threshold. |
| Generation | Ollama, `qwen2.5:7b-instruct-q4_k_m` | temperature 0.2, num_predict 1000, num_ctx 4096, streamed | A `Modelfile` exists in the same folder defining *different* params (temp 0.15, num_ctx 8192, a simpler system prompt) and would create a *differently-named* Ollama model if `ollama create` were ever run against it — `app.py` never references that name, so **the Modelfile is dead configuration**, not what's running |
| Prompt construction | `PromptBuilder.build_prompt()` (`retrieval-service`) | Regex/keyword heuristics decide grade, subject (math vs. science), mode (exam/practice/math/science-theory), difficulty, and a "grounding confidence" prefix from `avg(rerank_score)` | Prompt is fully deterministic Python string-building, not templated through a config file — every wording change requires a code deploy |
| Streaming | SSE via `StreamingResponse`, line-by-line JSON | Gateway re-parses SSE and re-emits SSE to the browser | Two hops of manual SSE parsing (Ollama→generation-service→gateway→browser); functional, but each hop is a place a malformed partial JSON line silently drops a token (`except json.JSONDecodeError: continue` in three places) |
| Caching | Redis (session filters, answer cache 24h, last-6-turn history) with automatic in-memory fallback if Redis is unreachable | — | In-memory fallback means cache/session state resets on every service restart in that mode, and doesn't survive multi-worker deployment — acceptable for local dev, worth flagging for anything beyond that |

---

## 4. Retrieval-Critical Bugs and Data-Integrity Findings (highest priority — read this before the language sections)

These are concrete, code-and-data-verified issues, not stylistic suggestions.

**4.1 — `app/evaluation/evaluator.py` does not run.**
`RAGEvaluator.run_evaluation()` calls:
```python
candidates = self.retriever.retrieve(req, query_vector)   # evaluator.py:102
```
but `HybridRetriever.retrieve` is `async def` (`hybrid_retriever.py:216`). Called without `await` and with no event loop, this line produces an *unexecuted coroutine object*, not a result. That object is then handed to `reranker.rerank(query, candidates, top_k)`, whose first line is `if not candidates or self.model is None: return candidates[:top_k]` — a coroutine is truthy and not subscriptable, so this raises `TypeError` on `candidates[:top_k]`. Separately, even were this fixed, the evaluator calls with `query_vector = np.zeros(768)` (evaluator.py:99) — a zero vector — for *every* question, so `cosine_similarity` returns ~0 for all candidates and the "dense" half of hybrid retrieval contributes nothing in this evaluator; its reported numbers, on the rare occasion they've been captured (`data/processed/evals/eval_history.json`, `report_*.md`), reflect BM25-plus-broken-fusion, not the system a student actually queries.

**4.2 — `priority_retriever.py` / `PriorityRetriever` is dead code.**
`grep -rn "priority_retriever\|PriorityRetriever" main.py app/` returns only the file's own definition. Source prioritization is real and does work — it's just re-implemented inline inside `hybrid_retriever.py`'s `_execute_retrieve_for_medium` (the "Textbooks & Guides first, PYQ/notes supplement" block). Anyone reading the codebase to understand *how* prioritization works would reasonably start at `priority_retriever.py` and be misled.

**4.3 — Chapter and section metadata are non-functional across ~100% of the corpus.**
Every one of the 396 English chunks and 127 Tamil chunks carries `chapter_title = "Front Matter / Introduction"` (or `"Unknown Chapter"` for one small document) and `section_no = None`, regardless of actual content — I confirmed real chunks from pages spanning Unit 1 through Unit 7 (Measurement, Force and Motion, Matter, Plants, Animals, Nutrients, Computers) all carry the same placeholder chapter label. Root cause, found in `app/ingestion/chapter_parser.py`:
```python
CHAPTER_REGEX = re.compile(
    r"^(அலகு|அத்தியாயம்|அதிகாரம்|unit|chapter)\s*([ivxlcdm]+|\d+)\s*:?\s*(.*)$", re.IGNORECASE)
```
This requires a heading block whose text *starts* with one of those literal words followed immediately by a number and (optionally) a colon — e.g. `"Unit 1: Measurement"`. The actual textbook headings, as extracted, look like `"Unit\n1\nMeasurements"` (line-broken, unit number and title on separate physical lines/layout blocks) or just `"1 Measurements"` — they never produce a single block matching this exact pattern, so `split_by_chapters` never advances past its initialized default (`chapter_parser.py:30-34`), and every chunk gets tagged with the front-matter placeholder. This is a layout-detection problem, not a language problem — it affects English and Tamil equally, and it means every "Chapter: {chapter_title}" line shown to the LLM in its context header (`prompt_builder.py:build_context_text`) is currently useless, and any citation feature relying on `chapter_title` will show every citation as "Front Matter / Introduction."

**4.4 — The registry manifest (`data/registry/manifest.json`) disagrees with the actual serving cache.** The manifest records `"term": 1` for the Class 6 Science English *and* Tamil documents that are physically Term 2 and Term 3 (`Class_6_Science_English_Science_-_Term_2.pdf`, `-Term_3.pdf`, and the Tamil equivalents), even though those PDFs sit in correctly-named `term_2/`/`term_3/` folders on disk. I verified this does **not** propagate into the actual chunks fed to retrieval — `english_chunks.pkl`/`tamil_chunks.pkl` correctly carry `term: 1/2/3` per document — so end users are not affected by this specific instance. But it does mean the registry (the system's own record of "what's indexed and how") cannot be trusted for an audit; whatever generates/updates it is out of sync with the real ingestion output. Root cause is consistent with `metadata_parser.py`'s term-detection loop (`for part in parts: ... break` at the first path segment matching `term[_\s-]?[1-3]`) picking up a stale/incorrect segment in whatever path was originally fed to the registry writer, separately from the current chunk cache's (correct) provenance.
**Practical implication:** don't trust `data/registry/manifest.json`, `SYSTEM_AUDIT_REPORT.md`, or `SECURITY_QUALITY_AUDIT_REPORT.md` as ground truth for what's indexed — always check the pickled cache directly, exactly as this evaluation did.

**4.5 — The project's own gold benchmark (`app/evaluation/benchmark_dataset.json`) has a stale-looking citation.** Question `VAL_SCI_6_T1_001` ("தாவரங்கள் ஒளிச்சேர்க்கையின் போது வெளியிடும் வாயு எது?" — what gas do plants release during photosynthesis) cites `expected_pages: [48, 49]`. I searched the live Tamil chunk cache directly for `ஒளிச்` / `சேர்க்கை` / `கார்பன்` / `டை ஆக்` and found no match at pages 48–49 — those pages fall within Unit 3 (Matter/Mixtures) in the currently indexed Term 1 Tamil textbook, not Unit 4 (Plants, pp. 59–71, where photosynthesis content would be expected). Either the ground truth was authored against a different edition/pagination of the PDF than what's currently indexed, or the citation was written without page-level verification. Either way: **running the existing (also-buggy, see 4.1) evaluator against this benchmark would report retrieval failure for a reason that has nothing to do with retrieval quality.** Two of the benchmark's four questions (`VAL_SCI_7_T1_001`, `VAL_SCI_8_FY_001`) additionally ask about Class 7/8 content that (Finding in Section 2) wasn't indexed at all as of 2026-09-15 — **as of the Section 0 reindex, that specific gap is closed** (Class 7/8 Science is now indexed), though the citation/pagination issue in this same question likely still needs separate verification against the new corpus. So 3 of the project's 4 existing gold questions could not, at the time, produce a meaningful pass/fail signal, for three different reasons — 2 of those 3 reasons no longer apply post-reindex. This is exactly the failure mode Section 36's rules warn against, occurring inside the project's own QA tooling.

**4.6 — Text-extraction quality is inconsistent, and Tamil specifically shows systematic corruption.** *(See Section 0.3 for the follow-up: the exact 3 corruption mechanisms identified, the fix implemented for 2 of them, and its measured — small — real-world impact.)* Most sampled pages extract cleanly (e.g. the "Electric Eel"/conductors passage, p.30 Term 2 English; the ராணி/ரவி vegetable-market passage, p.60 Term 1 Tamil). But diagram/table-dense pages can extract as scrambled, single-character-per-line noise — e.g. a Term 2 heat-transfer page (p.20) extracts as `"g\ne\nn\na\nof\nh\nn\nio\nSt..."`, unusable if retrieved. Separately, **Tamil text throughout the corpus shows systematic character-level corruption**: duplicated consonants and stray replacement characters, e.g. `பொ�ொருள்` (contains a literal U+FFFD replacement character), `ககற்்றல்`, `கக ணக்கிடு` — visible in essentially every Tamil chunk I inspected. `app/ingestion/ocr_cleaner.py` does contain a `normalize_tamil_unicode()` pass explicitly designed to repair "OCR artifacts where vowel modifier tokens are detached" — the fact that this corruption still ships in the served cache means that repair pass is incomplete against your actual source PDFs' Tamil font encoding, not that no attempt was made. **This is likely the single largest concrete contributor to any measured gap between Tamil and English answer/retrieval quality** — it's a source-text-quality problem upstream of the embedding model, the reranker, and the LLM, not a deficiency in any of those three.

**4.7 — Print-production artifacts leak into chunk text.** Extracted text includes leftover InDesign export watermarks and timestamps, e.g. `"VII Std Science Term-1 EM Unit 1.indd 3 06/01/2022 01:49:55"`, embedded mid-paragraph inside a *Class 6* chunk. (Table-of-contents evidence confirms Class 6 Term 1 legitimately has its own "Measurements" unit, so this is not proof of wrong-book contamination — it reads as a residual print-file artifact that `pdf_cleaner.py` doesn't strip — but it does mean this specific string, if surfaced, could easily be mistaken by anyone auditing the data for exactly the "wrong grade" bug it merely resembles, and it's real noise the LLM's context window pays for.)

**4.8 — No dependency version pins in `retrieval-service/requirements.txt`.** `sentence-transformers`, `torch`, `scikit-learn`, `paddleocr`, and everything else is unpinned. Combined with Finding 4.0 above (reranker score calibration depends on the installed version), this is a direct reproducibility gap against your own brief's Section 33 requirements.

---

## 5. Tamil Evaluation

> **⚠ Numbers superseded — see Section 0.3 and 0.6.** This section's Recall@5 figures (58.3%) are from the 12-item, Class-6-Science-only pass. The 0.6 rerun (25 Tamil items, all 3 grades, both subjects) found Recall@5 60.0% — the same conclusion, now on a larger sample — and 0.3 adds the precise 3-mechanism breakdown of *why*, plus the measured (small) impact of the partial fix applied. The qualitative analysis below (prompt templates, chunking hypothesis) is unchanged and still accurate.

**What's genuinely strong:** the Tamil prompt templates (`prompt_builder.py`) are detailed and pedagogically considered — explicit rules for LCM/multiply/divide terminology, KaTeX formatting instructions, an emoji-structured response template per mode (exam/practice/math/science). The correction-service and `Modelfile`'s system prompt both explicitly instruct the model to say "விடை பாடப்புத்தகத்தில் இல்லை" ("the answer is not in the textbook") rather than fabricate, when context is insufficient — good practice, present in intent even if (per 4.0) the Modelfile itself isn't live.

**What's measurably weaker, with cause identified:**
- Real BM25 retrieval (Section 7) is meaningfully worse for Tamil than English at every k (Recall@5: 58.3% Tamil vs. 90.0% English; MRR: 0.43 vs. 0.66) on the *same* underlying textbook content, translated 1:1 in the Term 1 units.
- The Tamil corpus is ~3.1x smaller than the English one (127 vs. 396 chunks) for what should be the same curriculum coverage — likely fewer/coarser source pages OCR'd successfully, or fewer supplementary documents provided in Tamil medium.
- Systemic character-level OCR corruption (Finding 4.6) directly degrades both the token overlap BM25 needs and the semantic signal the embedding model receives.
- Chunking is word-count-based (500 words), not token-based. Tamil's agglutinative morphology and the way LLM tokenizers (including Qwen's) typically fragment Indic scripts into more subword tokens per surface word than English means a "500-word" Tamil chunk very likely consumes meaningfully more of the 4096-token generation context window than a 500-word English chunk — untested here (would need the actual tokenizer), but a well-founded hypothesis given the general behavior of BPE tokenizers on Tamil, and worth verifying directly with the real Qwen tokenizer before the 30-day plan's context-budget work.
- Language quality of *generated* Tamil answers is **not currently measurable** from this sandbox (needs a live Ollama call — see `evaluate_generation.py`). Judge it on the `language_quality` field once you run that script; do not assume it's bad because retrieval is weaker — those are different pipeline stages with different, now-separated diagnoses.

---

## 6. English Evaluation

> **⚠ Numbers superseded — see Section 0.6.** The rerun (108 English items, all 3 grades, both subjects) found Recall@5 92.6%, Recall@10 98.1%, MRR 0.793, nDCG@5 0.925 — the same "English retrieval is strong" conclusion, now confirmed well beyond Class 6 Science alone.

Real BM25 numbers (Section 7, original 2026-09-15 run) are strong: Recall@5 90%, Recall@10 100%, MRR 0.66, nDCG@5 0.69, on 20 core English questions spanning 7 curriculum units. This is expected — English textbook text extracted cleanly in every sample I inspected, and BM25 lexical matching against clean, well-segmented English text is close to a best case for this retrieval method. The main risks for English are the same architecture-level ones as everywhere else (chapter/section metadata broken, no citation instruction in the prompt, print-artifact leakage) rather than anything language-specific.

---

## 7. Bilingual (code-mixed) Evaluation — the most important measured result in this report

> **⚠ Numbers superseded — see Section 0.6.** The rerun (14 bilingual + 9 Tanglish items, full corpus) found the identical mechanism and a comparably large gap (bilingual: 78.6% vs 14.3% Recall@5, a 64.3-point gap; Tanglish: 77.8% vs 11.1%, a 66.7-point gap) — the toggle-routing problem below is unchanged by the corpus rebuild, as expected, since it's a routing-logic bug, not a coverage gap.

Nine bilingual (Tamil-script sentence + embedded English technical terms) and eight Tanglish (fully Latin-script, phonetically transliterated Tamil) questions were run through the **real, unmodified production BM25 algorithm** against both the real English and real Tamil indices (`evaluation/results/retrieval_bm25_results.json`, executed 2026-09-15):

| Query type | vs. English corpus Recall@5 | vs. Tamil corpus Recall@5 | Best-of-either | Gap |
|---|---:|---:|---:|---:|
| Bilingual (Tamil script + English terms) | 66.7% | 11.1% | 66.7% | **55.6 pts** |
| Tanglish (Latin-script transliteration) | 87.5% | 12.5% | 100.0% | **75.0 pts** |

**Why this happens, mechanically:** `PromptBuilder.detect_language()` (the only text-based language signal anywhere in the pipeline) is a single check — "does the query contain ≥1 Tamil Unicode codepoint" — and it is used *only* to select which prompt-template wording to build, never to route retrieval. Which corpus gets *searched* is decided entirely by `preferred_medium`, a value the **client UI** sends (a toggle the student sets, defaulting from a separate `language` field also supplied by the client — `gateway/app.js:135,169,411`). BM25 is a literal-token matcher: a Tanglish query like *"Ver thodappugal evlo types irukku"* shares zero tokens with the Tamil-script corpus (`வேர்த் தொகுப்பு...`) no matter how good the retrieval math is, but does share tokens with English chunks that happen to use the word "types." A bilingual query with embedded English technical terms (*"Root system-ல எத்தனை types இருக்கு..."*) gets a genuine, if partial, boost against the English corpus purely because "root," "system," and "types" are literal English words appearing in both.

**The practical consequence:** a bilingual-speaking student's retrieval quality is currently determined more by which UI toggle position they happen to have selected than by anything about their actual question. There is no code anywhere that reconciles or arbitrates between the two — no query-time bilingual detection, no dual-corpus search-and-merge, no fallback triggered by the *presence* of code-mixing (the existing `fallback_language_allowed` flag only fires when the *primary* search returns zero results, which a code-mixed query against its "wrong" corpus frequently will not — it just returns bad results, not none).

Dense retrieval and the reranker (both semantic, not literal-token, methods) will likely narrow this specific gap — a multilingual embedding model can plausibly place `"root system"` and `"வேர்த் தொகுப்பு"` close in vector space even without shared tokens — but that is a hypothesis this report cannot yet confirm from the sandbox it ran in. **Run `evaluate_retrieval_full.py` next**; the same per-item, per-corpus structure is already computed there specifically so you can directly compare the BM25-only gap above against the dense+reranked gap, and see how much of this the semantic stages actually close.

---

## 8. Tanglish Evaluation

Covered jointly with Bilingual above (Section 7) since both are measured the same way in this pass — the results table there separates them. One Tanglish-specific note: the **English-corpus recall for Tanglish (87.5%) is higher than for genuinely bilingual queries (66.7%)**, which makes sense mechanically — a fully Latin-script Tanglish sentence, if it retains any English technical vocabulary (as most of the sampled items do — "types," "explain," subject nouns), matches the English corpus purely lexically almost as well as a native English question would, while a Tamil-script-heavy bilingual query has fewer literal English tokens for BM25 to latch onto. This is a coincidence of this test set's vocabulary choices, not a general claim that Tanglish is "easier" than bilingual — it would be worth re-testing with Tanglish items that use zero English loanwords once you have generation-stage results, to see whether that pattern holds for pure code-mixed phonetic transliteration with no lexical crutch.

---

## 9. Retrieval Evaluation (metrics, executed)

> **⚠ Numbers superseded — see Section 0.6 for the current 156-item/7,426-chunk rerun.** The table below is preserved as the original 2026-09-15 baseline (49 items, Class 6 Science only, 523 chunks). Note also that this original run predates the Section 0.5 subject-filter bug fix — harmless for this specific run since 100% of the corpus really was `subject=='science'` at the time, but not safe to reuse as a template for any future rerun against mixed-subject data without that fix.

**Executed 2026-09-15 (real data, real algorithm, 49 core questions, Class 6 Science only):**

| Language | Recall@1 | Recall@3 | Recall@5 | Recall@10 | Precision@5 | MRR | nDCG@5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| English (n=20) | 0.50 | 0.85 | 0.90 | 1.00 | 0.20 | 0.656 | 0.688 |
| Tamil (n=12) | 0.25 | 0.50 | 0.583 | 0.75 | 0.117 | 0.433 | 0.423 |
| Bilingual vs EN corpus (n=9) | 0.00 | 0.667 | 0.667 | 0.889 | 0.133 | 0.260 | 0.312 |
| Bilingual vs TA corpus (n=9) | 0.111 | 0.111 | 0.111 | 0.222 | 0.022 | 0.151 | 0.111 |
| Tanglish vs EN corpus (n=8) | 0.125 | 0.75 | 0.875 | 1.00 | 0.20 | 0.476 | 0.575 |
| Tanglish vs TA corpus (n=8) | 0.00 | 0.00 | 0.125 | 0.125 | 0.025 | 0.044 | 0.030 |

Full per-question breakdown (including which pages were actually returned for every miss): `evaluation/results/retrieval_bm25_results.json`.

**Method note (read before citing these numbers elsewhere):** this is the BM25/sparse-retrieval stage only, run stand-alone with the same `SimpleBM25` class and identical `filter_candidates` medium/term logic as production, against the real cached corpus. It intentionally excludes dense retrieval, RRF fusion with a real dense signal, and the cross-encoder reranker — those need your local venv (torch/sentence-transformers) and are not reachable from the sandbox this report was produced in. **This is very likely a lower bound, not the system's real quality** — production always runs BM25 fused with dense retrieval and then reranks; a semantic (embedding-based) stage should recover at least some of the misses a purely lexical method makes, particularly for the bilingual/Tanglish gap in Section 7. Run `evaluate_retrieval_full.py` (delivered, ready to run) to get the honest, complete number — it reports before/after-reranker metrics in the identical schema, so the two result files are directly comparable.

**Not currently measurable from here:** Precision@1/3/10, Hit Rate beyond what Recall@k already reports (they're the same measurement under this dataset's single-relevant-item-per-question structure — noted in `metrics.py`), dense-only and reranked-only breakdowns, and any comparison against Class 7/8/Maths content (doesn't exist in the index — see Section 2).

**On the existing `app/evaluation/evaluator.py` and `metrics.py`:** the metric *formulas* in `metrics.py` (Recall@k, Precision@k, MRR, nDCG@k with binary relevance) are mathematically correct — I re-derived and independently re-implemented them (verbatim copy in `evaluation/scripts/metrics.py`) and got sane, expected values on a synthetic smoke test before trusting them against real data. The *evaluator that calls them* is broken (Section 4.1) and its one saved benchmark is partly stale (Section 4.5) — the formulas are fine, the harness around them is not.

---

## 10. Generation Evaluation

**Not executed live from this sandbox** (needs Ollama + the running retrieval/generation services on your machine — no network path from here to `localhost:11434` on a different machine). `evaluation/scripts/evaluate_generation.py` is ready to run and will:
- Call your real `/retrieve` then `/generate/stream` endpoints for all 49 core + 6 out-of-scope questions, across whichever language toggle(s) apply per item.
- Score every answer on correctness, relevance, completeness, groundedness, faithfulness, language quality, educational suitability, hallucination (0/1), abstention (0/1), and detected response script/language, via an LLM-judge rubric (Section 12 below covers the design and its limits).
- Prefer a *different* Ollama model as judge than the answer-generation model (auto-detects `llama3.1` if you have it pulled) specifically to reduce self-grading bias; falls back to self-judging qwen with an explicit warning printed and recorded in the output if no second model is available.

Run it (even with `--limit 10` for a 10-question smoke test first) and re-open this report's companion `evaluation/results/generation_results.json` — the scores, per-language breakdowns, and worked examples of correct/incorrect answers all belong here and cannot be responsibly filled in without that data.

---

## 11. Groundedness Evaluation

Structurally, the pipeline is designed for groundedness: the system prompt tells the LLM to rely only on the provided textbook context and never fabricate ("Do not hallucinate content outside the context" / "பாடப்புத்தக விவரங்களைக் கடந்து கற்பனையாகப் பதிலளிக்கக் கூடாது"), and a numeric "grounding confidence" prefix (`avg_score >= 0.7` → "According to your Samacheer Kalvi textbook," vs. a hedged "Based on the available textbook information,") is computed from the reranker's own scores. Two caveats on trusting that number:
1. **The Tamil-language version of this instruction has a real bug** (`prompt_builder.py:237-239`): both the "if grounding is strong" and "if grounding is weak" example lines print the *same* already-resolved `grounding_prefix_ta` value — the two conditional-looking lines convey no actual conditional information to the model (Python already chose the value beforehand). Functionally harmless (the correct single value still reaches the model) but confusing boilerplate that should be cleaned up.
2. **The 0.7 threshold is being compared against the same reranker score whose calibration is unverified** (Section 3/4.0) — if `CrossEncoder.predict()` isn't returning something in [0,1], this confidence signal is arbitrary, not meaningful. This is the single fastest thing to verify once you have your venv available: the diagnostic print already built into `evaluate_retrieval_full.py` answers it in one line.

Actual groundedness of generated answers (whether text in the output is *actually* traceable to retrieved chunks) is scored per-item by `evaluate_generation.py`'s judge rubric — not currently measurable without running it.

---

## 12. Hallucination Evaluation

Six adversarial `out_of_scope` items are included in `gold_dataset.json` specifically for this: two ask about Class 7/8 content that isn't indexed, one asks a false-premise question ("why does water boil at 50°C at sea level"), one combines two unrelated concepts (photosynthesis and Newton's third law) neither of which is a Class 6 Science topic, and two ask about Mathematics (not indexed in any medium). Per this evaluation's own methodology (and Section 36's rule 10): **these must be scored for abstention/hallucination behavior, never for retrieval recall** — a "failure" to retrieve is the *expected, correct* outcome for them. `evaluate_generation.py` records `judge.abstained` and `judge.hallucination` for exactly this reason. Not executable from this sandbox; run it locally.

One structural risk worth flagging even before that data exists: because `class_id` filtering is optional and the subject detector (`detect_subjects`) is a broad keyword regex, an out-of-syllabus Class 7 question that happens to share vocabulary with an indexed Class 6 topic (e.g., "force," "pressure") could retrieve real Class 6 content and let the model construct a plausible-sounding, textbook-grounded-*looking* answer to a question about material it never actually saw — a subtler and more dangerous failure mode than outright fabrication, because it would pass a naive "is this grounded in retrieved context" check while still answering the wrong grade's question. `evaluate_generation.py` deliberately leaves `class_id` unset for out-of-scope items specifically to surface this.

---

## 13. Citation Evaluation

The context header shown to the LLM (`prompt_builder.build_context_text`) does include rich structured metadata per chunk — source filename, class, subject, term, chapter, section, page, publisher, edition — but:
- **Chapter and section are wrong for ~100% of chunks** (Finding 4.3), so any citation surfaced from them is wrong.
- **The system prompt never instructs the model to actually reproduce a citation in its answer** — no "cite the chapter and page you used" instruction exists in either the Tamil or English prompt template. Citation-worthy metadata is available to the model but never requested back from it, in either language.
- Page numbers themselves are correctly extracted and attached (verified directly from the pickled chunk metadata), so a page-level citation feature, if the prompt asked for one, would at least have *correct* page data to draw from — it's the chapter/section layer specifically that's broken, not the whole metadata stack.

Citation Precision/Recall/Coverage as numeric scores are **not currently measurable** — they require a live-generated answer that claims a citation to check against retrieved-chunk ground truth, which needs `evaluate_generation.py`'s output.

---

## 14. Performance Evaluation

Measured directly from the code (not from a live run, since the services aren't running from this sandbox):
- Generation: `temperature=0.2`, `num_predict=1000`, `num_ctx=4096`, streamed. Whether 4096 tokens of context is adequate depends on chunk count × chunk size × tokenizer inflation (see the Tamil tokenizer-efficiency hypothesis in Section 5) — with `top_k=3` chunks of ~500 words each plus a verbose emoji-templated system prompt (the Tamil template alone runs to several hundred words before any context is even inserted), a 4096-token window leaves comparatively little headroom for the 1000-token response, especially for Tamil.
- Retrieval: BM25 is O(query_terms × corpus_size); at 523 total chunks this is fast (sub-second, confirmed by this evaluation's own BM25 run). Dense search is brute-force cosine similarity over the full filtered embedding matrix — also fine at this scale, would need an ANN index (FAISS/Qdrant, currently absent) if the corpus grows past low thousands of chunks.
- `evaluate_retrieval_full.py` records real latency (`pre_rerank_latency_ms`, `rerank_latency_ms`) per question when you run it — not fabricated here.
- GPU/CPU/RAM usage: the retrieval-service's `/evaluation/dashboard` endpoint (`main.py:get_system_resources`) does compute live CPU/RAM/GPU figures via `psutil`/`torch.cuda`, but only while the service is actually running on your machine — not observable from this static/offline pass.

---

## 15. Failure Analysis

| Failure type | Evidence found | Tamil | English | Bilingual | Notes |
|---|---|---|---|---|---|
| Coverage gap (not a real failure) | Class 7/8/Maths never indexed | — | — | — | **Resolved 2026-09-16, Section 0.1** — was true at original evaluation time; affected `out_of_scope` items and 2/4 of the project's own benchmark questions by design at the time |
| Retrieval failure (lexical) | Measured directly, Section 9 | 41.7% miss @5 | 10% miss @5 | 33–89% miss @5 depending on corpus | Real numbers from this evaluation's BM25 run |
| Metadata/citation failure | Chapter/section broken corpus-wide | Yes | Yes | Yes | Section 4.3, root-caused |
| Language-routing failure | Toggle vs. query-text mismatch, never reconciled | — | — | Directly demonstrated | Section 7 — the report's headline finding |
| Evaluation-harness failure | `evaluator.py` async bug + zero-vector dense scoring | — | — | — | Section 4.1 — the project could not have been correctly measuring itself even before this report |
| Ground-truth staleness | Benchmark's own citation doesn't match live index | — | — | — | Section 4.5 |
| Generation/hallucination/language-quality failure | **Pending** — needs `evaluate_generation.py` | pending | pending | pending | Cannot be responsibly filled in without a live run |

---

## 16. Ablation Study

Designed, partially executed:

| Experiment | Status | Where |
|---|---|---|
| A. LLM only (no RAG) | Not run — would need a direct Ollama call bypassing retrieval; easy to add to `evaluate_generation.py` as a `--no-retrieval` flag if wanted | script exists, flag doesn't yet |
| B. LLM + RAG (BM25 only) | **Executed** | `retrieval_bm25_results.json` |
| C. LLM + RAG (dense + BM25 + RRF, no reranker) | Ready to run | `evaluate_retrieval_full.py` reports `before_rerank` metrics |
| D. LLM + RAG + reranker (current production retrieval config) | Ready to run | `evaluate_retrieval_full.py` reports `after_rerank` metrics — directly comparable to C |
| E. Full system incl. generation + judge scoring | Ready to run | `evaluate_generation.py` |

Once C and D are run, the single most informative number in this whole report will be **how much of the bilingual/Tanglish Recall@5 gap found in Section 7 survives past the reranker** — that answer doesn't exist yet, but the exact comparison is already wired up and waiting for one local run.

---

## 17. Overall Scores — and why most of them can't responsibly be numbers yet

Per this evaluation's own rule (explicitly requested, and one this report intends to actually honor rather than pay lip service to): **a score is only reported where there is a defined, executed measurement behind it.** Retrieval has real numbers. Generation, groundedness-in-practice, hallucination rate, citation accuracy, and overall language quality do not yet, because they need a live model call this sandbox cannot make. Weighting placeholder numbers into a single "Overall Score: XX/100" would manufacture false precision. See the Final Scorecard (Section 21) for what's scoreable today versus what requires your one local run to complete.

---

## 18. Strengths (Top 10, each with evidence)

1. **The microservice separation is real and clean** — retrieval, generation, correction, and gateway are genuinely decoupled FastAPI/Express services with their own Dockerfiles and health checks, not a monolith pretending otherwise.
2. **Prompt engineering is unusually detailed for Tamil**, with explicit, hardcoded terminology rules (LCM, multiply/divide/add/subtract) rather than leaving translation entirely to the model.
3. **A correction/override mechanism exists and runs *before* retrieval**, giving a real, working path for a teacher to hand-fix a wrong answer without retraining or re-indexing anything.
4. **The reranker threshold and grounding-confidence prefix show real intent to communicate uncertainty** to the student rather than always answering with false confidence.
5. **Ingestion has a genuine OCR fallback chain** (PyMuPDF → Tesseract/PaddleOCR, GPU-tiered) and an explicit Tamil Unicode repair pass — the *attempt* at robust text extraction is there even where the *result* (Section 4.6) isn't yet fully working.
6. **Source-priority logic (textbooks/guides over PYQs/notes) is implemented and correct**, even though the module named for it (`priority_retriever.py`) isn't actually where it lives.
7. **The gateway has working resilience patterns**: Redis-with-in-memory-fallback, rate limiting on chat/upload routes, and a cache-key design that correctly incorporates every filter dimension (class/term/medium/subject) rather than caching on query text alone.
8. **The project already has *some* evaluation infrastructure** — a benchmark dataset, a metrics module with correct formulas, and a dashboard endpoint — which is more scaffolding than many projects at this stage have, even though the harness wrapping it needs the fixes in Section 4.
9. **Admin-key gating and per-process random-secret generation (rather than hardcoded dev defaults) is implemented consistently across all three Python services** — a real, deliberate security decision visible in the code, not an oversight.
10. **The data itself is real, curriculum-aligned Tamil Nadu Samacheer Kalvi content**, not synthetic or placeholder text — every chunk I inspected across 7 units was genuine textbook material, correctly page-numbered.

## 19. Weaknesses (Top 10, each with a specific fix)

1. **No code-mixed/bilingual query handling** (Section 7) — Fix: replace the binary Tamil-Unicode-presence check with a real code-mixing detector (even a simple ratio of Tamil-to-Latin tokens, or a small classifier), and — more importantly — search *both* corpora for any query with mixed-script signal, merging results, rather than trusting a single client-supplied toggle. Affected: `prompt_builder.py::detect_language`, `hybrid_retriever.py`, `gateway/app.js`.
2. **Chapter/section metadata broken corpus-wide** (Section 4.3) — Fix: `chapter_parser.py`'s regex needs to work from layout signals (font size, boldness, position from `layout_analyzer.py`) rather than a strict text-prefix match, since the source PDFs don't format headings the way the regex assumes.
3. **`app/evaluation/evaluator.py` cannot run** (Section 4.1) — Fix: call `retriever._retrieve_sync()` directly (synchronous), or properly `await`/`asyncio.run()` the async wrapper; also replace the zero-vector dense query with a real embedding call.
4. ~~**Only Class 6 Science is indexed**~~ **RESOLVED 2026-09-16** (Section 0.1) — full 28-book reindex completed; corpus now covers Class 6/7/8 × Maths/Science × English/Tamil (7,426 chunks, up from 523).
5. **Systemic Tamil OCR/text-extraction corruption** (Section 4.6, precisely characterized in Section 0.3) — a partial Unicode-normalization fix was implemented and shipped, but measured to recover only ~1.1 percentage points, because the dominant corruption mechanism (consonant/matra duplication) is a font-encoding problem, not a normalization problem. Fix (not yet implemented): force OCR for Tamil-medium documents regardless of whether PyMuPDF reports the page as natively searchable, so extraction reads rendered glyphs instead of the broken font's ToUnicode CMap.
6. **Reranker threshold calibration is unverified** (Section 3) — Fix: pin `sentence-transformers` and check `CrossEncoder.predict()`'s actual output range once (the diagnostic already exists in `evaluate_retrieval_full.py`); recalibrate 0.35 if the range isn't [0,1].
7. **No dependency version pins in `retrieval-service/requirements.txt`** (Section 4.8) — Fix: `pip freeze` your working venv into pinned versions.
8. **Orphaned `Modelfile` documents a system that isn't running** (Section 3) — Fix: either wire `generation-service/app.py` to actually build/use the custom Ollama model the Modelfile defines, or delete the Modelfile to stop it misleading future readers (including future evaluations like this one).
9. **No citation instruction in either language's system prompt** (Section 13) — Fix: add one line asking the model to name the chapter/page it drew from — but only after Finding 4.3 (chapter/section metadata) is fixed, or the model will confidently cite "Front Matter / Introduction" every time.
10. **The project's own benchmark and registry manifest are stale relative to the live index** (Sections 4.4, 4.5) — Fix: regenerate both from the current `*_chunks.pkl` cache as the source of truth, and add a CI check (or even just a pre-commit script) that fails if `manifest.json`'s document list diverges from what's actually in the cache.

---

## 20. Recommended Improvement Roadmap

### Priority 1 — Critical (correctness/reliability)
| # | Problem | Evidence | Fix | Files | Benefit | Difficulty |
|---|---|---|---|---|---|---|
|1| Evaluator can't run | 4.1 | Fix async call + real query embedding | `app/evaluation/evaluator.py` | Restores your ability to self-measure at all | Low |
|2| Chapter/section metadata dead | 4.3 | Layout-based heading detection | `chapter_parser.py`, `layout_analyzer.py` | Fixes citations + context quality system-wide | Medium |
|3| Bilingual/Tanglish retrieval routing | Section 7 (measured, 55–75pt gap) | Dual-corpus search + real code-mix detection | `prompt_builder.py`, `hybrid_retriever.py`, `gateway/app.js` | Directly fixes the largest measured quality gap in this report | Medium |

### Priority 2 — High (Tamil/bilingual performance)
| # | Problem | Evidence | Fix | Files | Benefit | Difficulty |
|---|---|---|---|---|---|---|
|4| Tamil OCR corruption | 4.6 | Extend Unicode repair patterns / re-extract | `ocr_cleaner.py` | Improves Tamil retrieval + generation quality at the source | Medium-High |
|5| ~~Class 7/8/Maths not indexed~~ **DONE 2026-09-16** | Section 0.1 | Full 28-book reindex completed | — | Coverage gap closed | — |
|6| Tamil corpus was 3x smaller than English | Section 5 (original) | ~~Audit why then backfill~~ **Partially addressed**: post-reindex, Tamil chunk count (3,843) now exceeds English (3,583) — the raw-count gap is gone, but Section 0.3's *usability* gap (corrupted prose in most Tamil Science books) is the more consequential remaining version of this problem | `data/books/`, Section 0.3 | Parity in retrievable material | Medium (the corruption fix, not the count) |

### Priority 3 — Medium (performance/maintainability)
| # | Problem | Evidence | Fix | Files | Benefit | Difficulty |
|---|---|---|---|---|---|---|
|7| Unpinned dependencies | 4.8 | Freeze and pin | `requirements.txt` | Reproducibility | Low |
|8| Orphaned Modelfile | Section 3 | Wire up or delete | `generation-service/Modelfile` | Removes a misleading artifact | Low |
|9| Stale registry manifest | 4.4 | Regenerate from live cache | `data/registry/manifest.json` | Trustworthy self-documentation | Low |
|10| Reranker calibration unverified | Section 3/11 | One diagnostic run + threshold recheck | `reranker.py` | Confidence signal becomes meaningful | Low |

### Priority 4 — Research Enhancements
| # | Idea | Why | Difficulty |
|---|---|---|---|
|11| Token-based (not word-based) chunk sizing, tokenizer-aware per language | Tamil/English tokenizer inflation asymmetry (Section 5 hypothesis) | Medium |
|12| Replace brute-force cosine with FAISS/Qdrant | Only matters once corpus grows past low thousands of chunks — not urgent today, worth planning before ingesting Class 7/8/Maths at scale | Medium |
|13| LLM-as-judge with a genuinely independent judge model, human-validated on a subsample | `evaluate_generation.py` already prefers a second model when available — validate its agreement with human raters before trusting it at scale | Medium |
|14| Publishable ablation (Section 16, experiments A–E) once C/D/E are run | Turns this report's groundwork into a citable result | Low (mechanically — scripts exist), depends on your own analysis |

**Not recommended: fine-tuning.** Every Priority 1 and 2 item above is a retrieval/metadata/routing/data-quality fix. None of the measured problems in this report are "the LLM doesn't understand Tamil well enough" — they are "the LLM was never given a fair, correctly-labeled, correctly-routed context to work from." Fine-tuning qwen2.5 on Tamil educational content might still be worth exploring eventually, but only after Priorities 1–2 are done and you can re-measure with a clean baseline — right now it would be solving the wrong layer.

---

## 21. Final Scorecard

> **⚠ Retrieval rows superseded — see Section 0.6.** Current (2026-09-16, 156-item/7,426-chunk) retrieval Recall@5: Tamil 60/100, English 93/100, Bilingual 14–79/100 depending on toggle, Tanglish 11–78/100 depending on toggle. Same conclusions, larger and more representative sample. All non-retrieval rows below remain accurate (still not measurable without the local generation run).

| Category | Score | Confidence | Basis |
|---|---:|---|---|
| Tamil Understanding (retrieval) | 58/100 (Recall@5) | **High** — executed, real data | Section 9 |
| English Understanding (retrieval) | 90/100 (Recall@5) | **High** — executed, real data | Section 9 |
| Bilingual Understanding (retrieval) | 12–67/100 depending on toggle | **High** — executed, real data | Section 7, 9 |
| Tanglish Understanding (retrieval) | 13–88/100 depending on toggle | **High** — executed, real data | Section 7, 9 |
| Retrieval (dense + reranked) | Not currently measurable | **Low** | Needs `evaluate_retrieval_full.py` run |
| Answer Correctness | Not currently measurable | **Low** | Needs `evaluate_generation.py` run |
| Groundedness (generation-stage) | Not currently measurable | **Low** | Needs `evaluate_generation.py` run |
| Faithfulness | Not currently measurable | **Low** | Needs `evaluate_generation.py` run |
| Citation Quality | Not currently measurable (metadata is broken regardless) | **High confidence that it's broken today**, low confidence in any future numeric score until 4.3 is fixed | Section 4.3, 13 |
| Hallucination Control | Not currently measurable | **Low** | Needs `evaluate_generation.py` on the 6 out-of-scope items |
| Educational Suitability | Not currently measurable | **Low** | Needs `evaluate_generation.py` run |
| Response Quality (overall) | Not currently measurable | **Low** | Needs `evaluate_generation.py` run |
| **Overall System** | **Not scored as a single number** | — | See Section 17: any weighted composite right now would be half real data, half placeholder. Re-run this section once `evaluate_all.py --with-full --with-generation` completes. |

---

## 22. The Direct Answer

**How good is the Tamil–English bilingual educational AI system you've actually built, based on measurable evidence?**

The infrastructure is real and mostly sound: a genuine hybrid-retrieval RAG pipeline with source prioritization, caching, rate limiting, and a correction-override mechanism, running against real curriculum content. What's demonstrably weak is not the language model or the choice of embedding/reranker models — it's three specific, fixable layers: (1) the system only actually knows Class 6 Science, (2) code-mixed queries are routed by a client-side toggle with zero reconciliation against the query's actual language content, measured here at a 55–75 point Recall@5 swing depending purely on that toggle, and (3) the structural metadata (chapter/section) that citations and context quality depend on doesn't work for any document in the corpus, traced to one specific regex.

**Is it ready for real student usage?** Not yet, in its current scope — students studying Class 7/8 Science or any Maths would get either silence or (more concerning, per Section 12) a confidently-wrong answer built from misretrieved Class 6 content. Within Class 6 Science, English-medium usage looks solid at the retrieval layer; Tamil-medium usage would benefit substantially from fixing the OCR corruption before wider rollout.

**Is it ready for academic evaluation, or strong enough for a research paper?** Not in its current state, but it is *close* to being able to produce one, and this report — plus the evaluation harness it leaves behind — is most of the missing scaffolding. What's missing is exactly the live-generation data this sandbox couldn't produce: run `evaluate_all.py --with-full --with-generation` once, and you will have real Recall/MRR/nDCG for the full hybrid+reranked pipeline, real LLM-judge scores across correctness/groundedness/hallucination/language-quality, and a genuine A/B/C/D/E ablation — publishable material, assuming the numbers hold up to the same scrutiny this report applied to what could be checked today.

**What should you fix first?** In order: (1) run the two scripts you haven't run yet so you have real generation-quality data, (2) fix the chapter-parser regex (small, isolated, high-leverage), (3) decide the bilingual-routing fix (dual-corpus search is the highest-value single change measured in this entire report).

**What would give the biggest improvement in Tamil and bilingual performance specifically?** Two things, in this order: fixing Tamil OCR corruption at the source (Section 4.6 — everything downstream inherits this), and implementing real dual-corpus retrieval for code-mixed queries (Section 7 — the single largest, most precisely quantified gap this evaluation found).

---

## 23. Concrete 30-Day Plan, Prioritized by Expected Impact

**Week 1 — See clearly (no model changes yet)**
- Day 1–2: Run `evaluate_all.py --with-full --with-generation` (start with `--gen-limit 15` for a fast first pass). This closes the single biggest gap in this report — everything currently marked "not currently measurable."
- Day 2: Fix `app/evaluation/evaluator.py`'s async bug (1-line-scope fix) and re-point it at a corrected `benchmark_dataset.json` (verify all 4 questions' pages against the live cache the way this report did for question 1).
- Day 3: Run the reranker-calibration diagnostic (already printed by `evaluate_retrieval_full.py`); recalibrate the 0.35 threshold if needed.
- Day 4–5: Pin `retrieval-service/requirements.txt`. Regenerate `data/registry/manifest.json` from the live `*_chunks.pkl` cache so it stops disagreeing with reality.

**Week 2 — Fix the highest-leverage bug (bilingual routing)**
- Implement dual-corpus retrieval for any query with mixed-script or Tamil+English-loanword signal: search both English and Tamil indices, merge/rerank the combined candidate set, rather than trusting a single client toggle.
- Re-run `evaluate_retrieval_bm25.py` and `evaluate_retrieval_full.py` against the same 62-item gold set to directly measure the before/after — this report's Section 7 numbers are your baseline.

**Week 3 — Fix metadata + start on Tamil text quality**
- Rework `chapter_parser.py` to use layout signals (font size/position from `layout_analyzer.py`) instead of the current text-prefix regex.
- Add a citation instruction to both prompt templates once chapter/section data is trustworthy.
- Begin auditing the Tamil OCR corruption pattern-by-pattern against a larger sample (start with the specific strings this report already found: `பொ�ொருள்`, `கக ணக்கிடு`) and extend `normalize_tamil_unicode()`'s repair rules.

**Week 4 — Coverage + re-measure**
- ~~Run the existing `/upload` ingestion pipeline against the already-present Class 7/8 Science and Maths PDFs~~ **DONE 2026-09-16, ahead of schedule** (Section 0.1) — full 28-book batch reindex, not `/upload`, was used (`python -m app.ingestion.index_books --all`), and two real bugs were found and fixed in the process (Section 0.2).
- Re-run the full evaluation suite end-to-end and compare against this report's numbers as your baseline — the BM25 stage of this has already been done (Section 0.6); the dense+reranker+generation stages still need one local run (`evaluate_all.py --with-full --with-generation`, Section 0.7) to complete the before/after.

**Week 5 (added 2026-09-16) — Tamil text-extraction root fix**
- Implement force-OCR-for-Tamil (Section 0.3): route Tamil-medium documents through the OCR path unconditionally, regardless of PyMuPDF's "is this page searchable" check, since the corruption originates in the source PDFs' broken font ToUnicode CMaps, not in OCR quality.
- Re-run the BM25 baseline (`evaluate_retrieval_bm25.py`, fast, numpy-only) after that change to directly measure its impact against the 60.0% Tamil Recall@5 baseline in Section 0.6, the same way this evaluation measured the smaller Unicode-normalization fix's 1.1-point impact before relying on it.

---

## Reproducibility

**Original pass (2026-09-15):**
- Model/algorithm: `SimpleBM25` exactly as implemented in `backend/retrieval-service/app/retrieval/hybrid_retriever.py` (k1=1.5, b=0.75), verbatim-copied into `evaluation/scripts/evaluate_retrieval_bm25.py` and run against the unmodified `data/processed/cache/bm25_index.pkl`, `english_chunks.pkl`, `tamil_chunks.pkl`.
- Dataset: `evaluation/datasets/gold_dataset.json` v1.0.0, 49 core + 7 language-instruction + 6 out-of-scope items, built 2026-09-15, grounded in Class 6 Science Term 1 (all 7 units) + two Term 2 spot-checks.
- Hardware/runtime: sandboxed Linux VM (no GPU, no network egress), Python 3.10.12, numpy only.
- Corpus: 523 total chunks (396 English, 127 Tamil), Class 6 Science only.

**Update pass (2026-09-16, see Section 0):**
- Corpus: full 28-book reindex, 7,426 total chunks (3,583 English, 3,843 Tamil), Class 6/7/8 × Maths/Science × English/Tamil. Two ingestion bugs fixed in the process (Section 0.2); Tamil text-corruption mechanisms characterized and partially fixed (Section 0.3).
- Dataset: `evaluation/datasets/gold_dataset.json` v2.0.0, 156 core + 8 language-instruction + 6 out-of-scope items, built 2026-09-16 from curated text extractions of the live post-reindex corpus (see the dataset file's own module docstring for full per-book sourcing and the Tamil-coverage limitations).
- Evaluation-tooling bug fixed: `evaluate_retrieval_bm25.py`'s subject filter (Section 0.5) — the fixed script is what produced the 0.6 numbers; if you have a copy from before 2026-09-16, re-pull it before re-running.
- Full per-question results for both passes, including every retrieved page for every hit and miss: `evaluation/results/retrieval_bm25_results.json` (currently holds the 2026-09-16 run; the file is overwritten on each run, so the 2026-09-15 numbers above are only preserved in this report's tables).
- **Not yet run** (needs your local venv/GPU/Ollama): `evaluate_retrieval_full.py`, `evaluate_generation.py`. The three result files currently on disk for those (`retrieval_full_results.json`, `generation_results.json`, `final_report.json`) predate the 2026-09-16 reindex and dataset rebuild — do not cite their current contents.

To reproduce or extend: `evaluation/README.md` has exact commands. To regenerate the dataset: `python evaluation/datasets/build_dataset.py` (run from `evaluation/datasets/`). To complete the picture with dense retrieval, reranking, and live generation+judge scoring against the current corpus and dataset:
```
cd backend\retrieval-service
..\..\.venv\Scripts\python.exe ..\..\evaluation\scripts\evaluate_all.py --with-full --with-generation
```
