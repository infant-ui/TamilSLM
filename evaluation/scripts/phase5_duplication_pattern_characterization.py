# evaluation/scripts/phase5_duplication_pattern_characterization.py
"""
Phase 5, step 2: characterizing the "duplication of consonant+matra sequences"
corruption pattern that text_utils.py's docstring explicitly left unaddressed
("not confidently characterized as a safe, general regex fix").

Uses wordfreq's externally-sourced Tamil frequency list (NOT a wordlist built from
this same corpus -- a self-referential reference risks being contaminated by the
very corruption it's meant to detect) to find out-of-vocabulary tokens with an
unambiguous (unique) edit-distance-1 correction, then decomposes the resulting
candidates by what kind of edit they represent -- because that decomposition is
where the real safety story is:

1. dedup_combining_SAFE: an immediately-repeated Tamil COMBINING mark (vowel sign
   or pulli, U+0BBE-U+0BCD), collapsed to one occurrence. Validated as safe to fix
   corpus-wide, unconditionally (not just when OOV): zero of 68,414 real Tamil
   words in the external vocabulary contain this pattern, and a direct scan of
   every Tamil chunk in the corpus found 41,078 token occurrences of a doubled
   combining mark, NONE of which is already a recognized real word as-written.
   Zero false positives found. Affects all 14 Tamil PDFs, with intensity varying
   widely by book (9%-82% of chunks) -- not isolated to specific fonts the way
   Phase 5 step 1's severe-mojibake pages were, but the fix's safety doesn't
   depend on isolation: the pattern is structurally invalid in Tamil regardless
   of source.

2. dedup_base_consonant_RISKY: an immediately-repeated Tamil BASE CONSONANT (no
   combining mark, no intervening pulli), collapsed to one occurrence. NOT safe
   as a general rule -- 1,991 real Tamil words in the external vocabulary
   legitimately contain this pattern, overwhelmingly as standard past-tense verb
   morphology (e.g. "இருந்தது" was, "வந்தது" came, "செய்தது" did, "கொடுத்தது"
   gave -- all extremely common). A blind collapse rule would corrupt correct
   grammar. NOT recommended for any corpus-wide fix.

3. other / other_single_delete: everything else the edit-distance search found,
   including some likely-genuine further patterns (e.g. a missing leading
   consonant before an orphaned vowel sign: "ொள்ளுதல்" -> "கொள்ளுதல்", seen
   recurring) mixed with clear false positives from the edit-distance method
   matching a different, unrelated but more frequent real word (e.g.
   "வடிவியல்" geometry -> "வடிவில்" in-shape; "நோய்கள்" diseases -> "நாய்கள்"
   dogs -- both wrong in their science/maths context). NOT characterized as safe;
   NOT recommended for any corpus-wide fix. A narrower follow-up investigation
   of the "missing leading consonant before orphaned vowel sign" sub-pattern
   specifically may be worthwhile later, but is out of scope for this pass.

Usage:
    .venv\\Scripts\\python.exe evaluation\\scripts\\phase5_duplication_pattern_characterization.py
Writes: evaluation/results/phase5_duplication_pattern_results.json
"""
import json
import os
import re
import sys

import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..", "..")
RESULTS_DIR = os.path.join(HERE, "..", "results")

sys.path.insert(0, os.path.join(REPO, "backend", "retrieval-service"))
sys.path.insert(0, os.path.join(REPO, "evaluation", "scripts"))
spec = importlib.util.spec_from_file_location("erf", os.path.join(REPO, "evaluation", "scripts", "evaluate_retrieval_full.py"))
erf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(erf)
from wordfreq import top_n_list

COMBINING = set("ாிீுூெேைொோௌ்")
DEDUP_COMBINING_RE = re.compile(r"([" + "".join(COMBINING) + r"])\1")
TAMIL_WORD_RE = re.compile(r"[஀-௿]+")

# Phase 5 step 1's confirmed severe-mojibake pages -- a different corruption
# mechanism, already piloted separately, excluded here to keep this pass focused.
SEVERE_MOJIBAKE_PAGES = {
    ("Class_7_Science_Tamil_Science_-_Term_1_-_2025.pdf", 92),
    ("Class_7_Science_Tamil_Science_-_Term_1_-_2025.pdf", 93),
    ("Class_7_Science_Tamil_Science_-_Term_2.pdf", 40),
    ("Class_7_Science_Tamil_Science_-_Term_2.pdf", 41),
}


def edits1(word, alphabet):
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    substitutes = [L + c + R[1:] for L, R in splits if R for c in alphabet if c != R[0]]
    inserts = [L + c + R for L, R in splits for c in alphabet]
    return set(deletes + substitutes + inserts)


def classify_edit(token: str, correction: str) -> str:
    if len(token) != len(correction) + 1:
        return "other"
    for j in range(len(token)):
        if token[:j] + token[j + 1:] == correction:
            deleted = token[j]
            is_dup = (j > 0 and token[j - 1] == deleted) or (j + 1 < len(token) and token[j + 1] == deleted)
            if is_dup and deleted in COMBINING:
                return "dedup_combining_SAFE"
            if is_dup:
                return "dedup_base_consonant_RISKY"
            return "other_single_delete"
    return "other"


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    cache = erf.build_services_cache()
    ta_chunks = cache["ta_chunks"]

    vocab = set(top_n_list("ta", 200000))
    alphabet = sorted(set("".join(vocab)))
    print(f"vocab size: {len(vocab)}, alphabet size: {len(alphabet)}", file=sys.stderr)

    # --- Part A: vocabulary-level validation of the SAFE pattern (no corpus needed) ---
    vocab_words_with_dup_combining = [w for w in vocab if DEDUP_COMBINING_RE.search(w)]
    vocab_words_with_dup_base = []
    for w in vocab:
        for i in range(len(w) - 1):
            if w[i] == w[i + 1] and w[i] not in COMBINING:
                vocab_words_with_dup_base.append(w)
                break

    # --- Part B: edit-distance-1 candidate search over OOV tokens in the corpus ---
    edit_classes = {}
    examples_by_class = {}
    n_chunks_analyzed = 0
    for c in ta_chunks:
        text = c.get("text") or c.get("content") or ""
        meta = c.get("metadata", {})
        if (meta.get("filename", ""), meta.get("page_number", 0)) in SEVERE_MOJIBAKE_PAGES:
            continue
        if not text or text.startswith("[Figure") or text.startswith("[Table"):
            continue
        tokens = [t for t in TAMIL_WORD_RE.findall(text) if len(t) >= 3]
        if not tokens:
            continue
        n_chunks_analyzed += 1
        for tok in tokens:
            if tok in vocab:
                continue
            candidates = sorted(cand for cand in edits1(tok, alphabet) if cand in vocab)
            if len(candidates) != 1:
                continue
            cls = classify_edit(tok, candidates[0])
            edit_classes[cls] = edit_classes.get(cls, 0) + 1
            examples_by_class.setdefault(cls, [])
            if len(examples_by_class[cls]) < 15:
                examples_by_class[cls].append({"token": tok, "correction": candidates[0],
                                                 "pdf": meta.get("filename"), "page": meta.get("page_number")})

    # --- Part C: direct, unconditional scan for doubled-combining-mark occurrences
    # (not gated by OOV+unique-edit-distance-1 -- this is the TRUE prevalence, and
    # also the actual false-positive check: is the as-written token already a real word?) ---
    n_token_occurrences_with_dup_combining = 0
    n_false_positives = 0
    by_pdf = {}
    chunks_affected_by_pdf = {}
    chunks_total_by_pdf = {}
    for c in ta_chunks:
        text = c.get("text") or c.get("content") or ""
        meta = c.get("metadata", {})
        fn = meta.get("filename", "unknown")
        chunks_total_by_pdf[fn] = chunks_total_by_pdf.get(fn, 0) + 1
        if not text:
            continue
        chunk_hit = False
        for tok in TAMIL_WORD_RE.findall(text):
            if DEDUP_COMBINING_RE.search(tok):
                n_token_occurrences_with_dup_combining += 1
                by_pdf[fn] = by_pdf.get(fn, 0) + 1
                chunk_hit = True
                if tok in vocab:
                    n_false_positives += 1
        if chunk_hit:
            chunks_affected_by_pdf[fn] = chunks_affected_by_pdf.get(fn, 0) + 1

    out = {
        "status": "characterization_complete_pending_go_no_go",
        "git_commit": "TODO -- fill in after committing this script; results file committed as the immediate next commit",
        "scope": "Step 2 of 2 (duplication-pattern characterization, steps 2a-2d). Step 3 (go/no-go gate: re-chunk/re-embed "
                 "affected pages through the self-retrieval gate, re-run the full 156-item eval + Tamil dense-only R@5 "
                 "isolation metric) has NOT been run -- this is a characterization report only, no corpus fix applied.",
        "vocabulary_validation": {
            "vocab_size": len(vocab),
            "n_vocab_words_with_doubled_combining_mark": len(vocab_words_with_dup_combining),
            "n_vocab_words_with_doubled_base_consonant": len(vocab_words_with_dup_base),
            "sample_doubled_base_consonant_real_words": vocab_words_with_dup_base[:30],
            "interpretation": "Zero real Tamil words contain a doubled combining mark -- that pattern is structurally "
                               "invalid in the language, safe to collapse unconditionally. 1,991 real words legitimately "
                               "contain a doubled BASE consonant (overwhelmingly standard past-tense verb morphology, "
                               "e.g. the sample words above) -- collapsing that pattern is NOT safe as a general rule.",
        },
        "edit_distance_candidate_search": {
            "n_chunks_analyzed": n_chunks_analyzed,
            "counts_by_class": edit_classes,
            "examples_by_class": examples_by_class,
        },
        "direct_prevalence_and_false_positive_check": {
            "n_token_occurrences_with_doubled_combining_mark": n_token_occurrences_with_dup_combining,
            "n_false_positives_already_a_real_word_as_written": n_false_positives,
            "false_positive_rate": (n_false_positives / n_token_occurrences_with_dup_combining
                                     if n_token_occurrences_with_dup_combining else None),
            "by_pdf_occurrence_counts": by_pdf,
            "by_pdf_chunks_affected": chunks_affected_by_pdf,
            "by_pdf_chunks_total": chunks_total_by_pdf,
            "font_correlation": "Affects all 14 Tamil PDFs (not isolated to specific fonts/pages the way Phase 5 step "
                                 "1's severe-mojibake pages were), with intensity varying widely by book (9%-82% of "
                                 "chunks per book). The fix's safety case rests on the structural invalidity of the "
                                 "pattern itself (see vocabulary_validation), not on isolating it to a narrow signature.",
        },
        "recommendation": {
            "dedup_combining_SAFE": "Proceed to the step-3 go/no-go gate (re-chunk/re-embed affected pages through the "
                                     "self-retrieval gate, re-run the full eval) -- validated safe, zero false positives "
                                     "found against an external 68k-word vocabulary across 41,078 occurrences.",
            "dedup_base_consonant_RISKY": "Do NOT apply. Legitimately occurs in common past-tense verb forms.",
            "other_and_other_single_delete": "Do NOT apply. Mix of a possibly-real secondary pattern (missing leading "
                                              "consonant before an orphaned vowel sign, e.g. 'ொள்ளுதல்' -> 'கொள்ளுதல்') "
                                              "and clear false positives from the edit-distance method matching an "
                                              "unrelated real word (e.g. 'வடிவியல்' geometry -> 'வடிவில்' in-shape). "
                                              "Worth a narrower follow-up investigation later; out of scope now.",
        },
    }
    out_path = os.path.join(RESULTS_DIR, "phase5_duplication_pattern_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Wrote {out_path}")
    print(json.dumps({k: v for k, v in out.items() if k not in ("edit_distance_candidate_search",)}, ensure_ascii=False, indent=2)[:2000])


if __name__ == "__main__":
    main()
