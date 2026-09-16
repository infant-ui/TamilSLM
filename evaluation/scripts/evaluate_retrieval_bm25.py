# evaluation/scripts/evaluate_retrieval_bm25.py
"""
Runs a FAITHFUL, standalone reproduction of the production BM25 sparse-retrieval
stage (backend/retrieval-service/app/retrieval/hybrid_retriever.py: SimpleBM25
and the medium/term candidate filter) against the REAL cached indices, using
the gold_dataset.json questions.

Why BM25-only, and not the full hybrid (dense + BM25 + RRF) + reranker pipeline:
this script is designed to run with ONLY numpy as a dependency, so it can execute
anywhere (including a sandboxed environment with no access to the project's
Windows venv, no network, and no local Ollama). It does NOT need the GTE
embedding model, the CrossEncoder reranker, sklearn, or torch.

It reuses the corpus artifacts your ingestion pipeline already produced:
  data/processed/cache/bm25_index.pkl        (pickled SimpleBM25 per language)
  data/processed/cache/english_chunks.pkl    (chunk text + metadata)
  data/processed/cache/tamil_chunks.pkl

For the DENSE + reranker + generation stages, see evaluate_retrieval_full.py
and evaluate_generation.py, which must run inside the project's own venv
(they import the real production modules and call the real embedding /
reranker / Ollama models) -- see README.md for exact run instructions.

USAGE (run from the repository root, e.g. via `python evaluation/scripts/evaluate_retrieval_bm25.py`):
    python evaluation/scripts/evaluate_retrieval_bm25.py

Writes: evaluation/results/retrieval_bm25_results.json
"""
import json
import math
import os
import pickle
import re
import sys
import types
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from metrics import (
    calculate_recall_at_k,
    calculate_precision_at_k,
    calculate_mrr,
    calculate_ndcg_at_k,
)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA_CACHE = os.path.join(REPO_ROOT, "data", "processed", "cache")
DATASET_PATH = os.path.join(HERE, "..", "datasets", "gold_dataset.json")
RESULTS_DIR = os.path.join(HERE, "..", "results")


# ---------------------------------------------------------------------------
# Verbatim reproduction of app/retrieval/hybrid_retriever.SimpleBM25
# (needed both to unpickle bm25_index.pkl -- which was pickled under that
# module path -- and to call get_scores exactly as production does).
# ---------------------------------------------------------------------------
class SimpleBM25:
    def __init__(self, corpus=None, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        if corpus is None:
            return  # populated by unpickling instead
        self.corpus_size = len(corpus)
        self.avg_doc_len = 0
        self.doc_lens = []
        self.doc_freqs = {}
        self.idf = {}
        self.doc_term_freqs = []
        if self.corpus_size == 0:
            return
        total_words = 0
        for doc in corpus:
            tokens = self._tokenize(doc)
            self.doc_lens.append(len(tokens))
            total_words += len(tokens)
            term_freq = {}
            for token in tokens:
                term_freq[token] = term_freq.get(token, 0) + 1
            self.doc_term_freqs.append(term_freq)
            for token in term_freq:
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1
        self.avg_doc_len = total_words / self.corpus_size
        for term, freq in self.doc_freqs.items():
            self.idf[term] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1.0)

    def _tokenize(self, text):
        return re.findall(r"\b\w+\b", text.lower())

    def get_scores(self, query):
        scores = [0.0] * self.corpus_size
        query_tokens = self._tokenize(query)
        for token in query_tokens:
            if token not in self.idf:
                continue
            idf_val = self.idf[token]
            for doc_idx in range(self.corpus_size):
                tf = self.doc_term_freqs[doc_idx].get(token, 0)
                doc_len = self.doc_lens[doc_idx]
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_len))
                scores[doc_idx] += idf_val * (numerator / denominator)
        return scores


def _register_stub_module_for_unpickling():
    """bm25_index.pkl was pickled with class path app.retrieval.hybrid_retriever.SimpleBM25.
    Register a module tree with our verbatim class under that exact path so pickle
    can resolve it without needing the real FastAPI/pydantic/sklearn-dependent package."""
    mod_app = types.ModuleType("app")
    mod_retrieval = types.ModuleType("app.retrieval")
    mod_hybrid = types.ModuleType("app.retrieval.hybrid_retriever")
    mod_hybrid.SimpleBM25 = SimpleBM25
    sys.modules["app"] = mod_app
    sys.modules["app.retrieval"] = mod_retrieval
    sys.modules["app.retrieval.hybrid_retriever"] = mod_hybrid


def load_bm25_index():
    path = os.path.join(DATA_CACHE, "bm25_index.pkl")
    _register_stub_module_for_unpickling()
    with open(path, "rb") as f:
        return pickle.load(f)


def load_chunks():
    out = {}
    for lang_key, fname in [("en", "english_chunks.pkl"), ("ta", "tamil_chunks.pkl")]:
        with open(os.path.join(DATA_CACHE, fname), "rb") as f:
            out[lang_key] = pickle.load(f)
    return out


def filter_candidate_indices(chunks, medium, class_level, term, subject):
    """Faithful subset of HybridRetriever.filter_candidates: medium + class_level
    + term + subject filters.

    NOTE (v2.0.0 full-corpus rebuild, 2026-09-16): the original version of this
    function omitted subject filtering entirely, on the documented assumption
    that "100% of the currently indexed corpus is metadata subject=='science'".
    That assumption is now FALSE -- the corpus was rebuilt to include Maths
    alongside Science for every class/term, so omitting the subject filter
    would let e.g. a Class 7 Maths question be scored against a candidate
    pool containing both Class 7 Maths AND Class 7 Science chunks, which is
    not what the production filter_candidates() does and would silently
    distort every new (Maths) item's recall/precision numbers. Fixed here to
    filter by ground-truth subject (passed in from the dataset item), which
    isolates "how good is BM25 ranking within the correct subject" -- a
    separate question from "does the production subject auto-detector pick
    the right subject", which is not something this standalone script tests
    (see hybrid_retriever.HybridRetriever.detect_subjects for that logic).

    Term filtering also now mirrors production exactly: Class 6/7 require an
    exact term match; Class 8 requires term == 0 (the old code only applied
    term filtering for class_level in (6, 7), which happened to be harmless
    for Class 8 since every Class 8 chunk already has term == 0, but is
    fixed here for correctness/clarity rather than relying on that coincidence).
    """
    valid = []
    for idx, chunk in enumerate(chunks):
        meta = chunk.get("metadata", {})
        if meta.get("medium") != medium:
            continue
        if class_level is not None and meta.get("class_level") != class_level:
            continue
        if subject is not None:
            chunk_sub = (meta.get("subject") or "science").lower()
            if chunk_sub != subject.lower():
                continue
        if class_level is not None and term is not None:
            if class_level in (6, 7) and meta.get("term") != term:
                continue
            if class_level == 8 and meta.get("term") != 0:
                continue
        valid.append(idx)
    return valid


def rank_by_bm25(bm25_for_lang, chunks_for_lang, candidate_indices, query):
    scores = bm25_for_lang.get_scores(query)
    scored = [(idx, scores[idx]) for idx in candidate_indices]
    scored.sort(key=lambda x: x[1], reverse=True)
    ranked_pages = []
    for idx, _score in scored:
        page = chunks_for_lang[idx]["metadata"].get("page_number")
        if page is not None:
            ranked_pages.append(page)
    return ranked_pages


def evaluate():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    bm25 = load_bm25_index()
    chunks = load_chunks()

    per_item = []
    for item in dataset["core"]:
        lang = item["lang"]
        # Which corpus(es) to query. For 'tamil'/'english' items this is
        # unambiguous. For 'bilingual'/'tanglish' items there is NO single
        # correct answer -- the UI's language toggle decides the corpus, not
        # the query text (see prompt_builder.detect_language() finding in the
        # final report) -- so we evaluate against BOTH corpora and report
        # both, which is itself the measurement of interest.
        corpora_to_try = {
            "english": ["en"],
            "tamil": ["ta"],
            "bilingual": ["en", "ta"],
            "tanglish": ["en", "ta"],
        }[lang]

        result_row = {"id": item["id"], "lang": lang, "unit": item["unit"],
                      "difficulty": item["difficulty"], "expected_pages": item["pages"]}

        for corpus_lang in corpora_to_try:
            candidate_idx = filter_candidate_indices(
                chunks[corpus_lang], "english" if corpus_lang == "en" else "tamil",
                item["class_"], item["term"], item.get("subject")
            )
            if not candidate_idx:
                ranked_pages = []
            else:
                ranked_pages = rank_by_bm25(bm25[corpus_lang], chunks[corpus_lang], candidate_idx, item["q"])

            expected = item["pages"]
            metrics = {
                "recall_1": calculate_recall_at_k(ranked_pages, expected, 1),
                "recall_3": calculate_recall_at_k(ranked_pages, expected, 3),
                "recall_5": calculate_recall_at_k(ranked_pages, expected, 5),
                "recall_10": calculate_recall_at_k(ranked_pages, expected, 10),
                "precision_5": calculate_precision_at_k(ranked_pages, expected, 5),
                "mrr": calculate_mrr(ranked_pages, expected),
                "ndcg_5": calculate_ndcg_at_k(ranked_pages, expected, 5),
                "top10_pages": ranked_pages[:10],
            }
            result_row[f"against_{corpus_lang}_corpus"] = metrics

        per_item.append(result_row)

    # Aggregate: primary corpus per language (matching toggle = matching lang;
    # for bilingual/tanglish, "primary" is undefined by design -- report both
    # separately plus a combined 'best_of_either_corpus' figure).
    def agg(rows, key_fn, metric):
        vals = [key_fn(r)[metric] for r in rows if key_fn(r) is not None]
        return sum(vals) / len(vals) if vals else None

    summary = {}
    for lang in ["english", "tamil", "bilingual", "tanglish"]:
        rows = [r for r in per_item if r["lang"] == lang]
        if not rows:
            continue
        if lang == "english":
            key_fn = lambda r: r["against_en_corpus"]
        elif lang == "tamil":
            key_fn = lambda r: r["against_ta_corpus"]
        else:
            key_fn = None

        entry = {"n": len(rows)}
        if key_fn:
            for m in ["recall_1", "recall_3", "recall_5", "recall_10", "precision_5", "mrr", "ndcg_5"]:
                entry[m] = agg(rows, key_fn, m)
        else:
            # bilingual / tanglish: report against each corpus separately
            for corpus in ["en", "ta"]:
                sub = {}
                kf = lambda r, c=corpus: r[f"against_{c}_corpus"]
                for m in ["recall_1", "recall_3", "recall_5", "recall_10", "precision_5", "mrr", "ndcg_5"]:
                    sub[m] = agg(rows, kf, m)
                entry[f"against_{corpus}_corpus"] = sub
            # best-of-either: recall@5 if EITHER corpus finds it (upper bound,
            # i.e. "if the system always guessed the right toggle")
            best_recall_5 = []
            for r in rows:
                best_recall_5.append(max(
                    r["against_en_corpus"]["recall_5"], r["against_ta_corpus"]["recall_5"]
                ))
            entry["best_of_either_corpus_recall_5"] = sum(best_recall_5) / len(best_recall_5)
        summary[lang] = entry

    os.makedirs(RESULTS_DIR, exist_ok=True)
    out = {
        "method": "BM25 sparse-retrieval only (no dense/rerank -- see README.md for why)",
        "n_questions": len(per_item),
        "summary_by_language": summary,
        "per_item": per_item,
    }
    out_path = os.path.join(RESULTS_DIR, "retrieval_bm25_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Wrote {out_path}")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    evaluate()
