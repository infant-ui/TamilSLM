# evaluation/scripts/evaluate_agentic.py
"""
Phase 4 comparison eval: agentic RAG (query decomposition + confidence-gated retrieval +
post-generation verification) ON vs OFF, on a SMALL hand-picked subset -- not the full
156-item gold set. Reason: a single generation+judge call on this CPU-only, heavily
shared machine measured ~350s end-to-end during the smoke test (179s generation + 169s
judge); 156 items x 2 conditions at that rate is not a feasible single eval pass. This
subset is a go/no-go latency+quality signal, the same spirit as the 25-item sample used
to tune the Tamil RRF weight before its full confirmatory run -- it is NOT a substitute
for a full run if these numbers look promising enough to justify one later.

Calls the ACTUAL running services (http://127.0.0.1:8000 retrieval, :8001 generation),
same convention as evaluate_generation.py -- does not reimplement retrieval or generation
logic. judge_answer() is imported directly from evaluate_generation.py (same function,
same rubric, same judge model selection) so the OFF condition's quality score is scored
by identical logic to the ON condition's server-side verification.

CAVEAT recorded in the output file: this machine had heavy, unrelated concurrent CPU load
during this run (multiple IDE instances, Steam, Epic Games Launcher, uTorrent all observed
competing for CPU via Get-Process). Absolute latency numbers here are NOT a clean
CPU-only-hardware benchmark; the relative ON-vs-OFF comparison is still meaningful since
both conditions ran under the same contention, interleaved item by item.

Usage: .venv\\Scripts\\python.exe evaluation\\scripts\\evaluate_agentic.py
Writes: evaluation/results/phase4_agentic_results.json
"""
import json
import os
import sys
import time
import importlib.util

RETRIEVAL_URL = "http://127.0.0.1:8000/retrieve"
GENERATION_STREAM_URL = "http://127.0.0.1:8001/generate/stream"
GENERATION_VERIFIED_URL = "http://127.0.0.1:8001/generate/verified"

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "..", "results")

spec = importlib.util.spec_from_file_location("evaluate_generation", os.path.join(HERE, "evaluate_generation.py"))
eg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eg)

import requests

# 3 natural items from the gold set (unmodified, single-hop by the decomposition
# heuristic) + 3 synthesized genuinely-compound questions (to actually exercise step 1,
# since the gold set was not authored with compound/multi-hop questions in mind).
ITEMS = [
    {"id": "EN_003", "lang": "english", "medium": "english", "class_": 6, "term": 1,
     "q": "How would you measure the length of a curved line using a divider?",
     "key_facts": ["use a divider to step along the curve", "mark small equal segments", "measure total with a ruler"]},
    {"id": "TA_001", "lang": "tamil", "medium": "tamil", "class_": 6, "term": 1,
     "q": "நீளத்தின் அலகு என்ன, அதன் குறியீடு என்ன?",
     "key_facts": ["metre", "symbol m"]},
    {"id": "BI_001", "lang": "bilingual", "medium": "english", "class_": 6, "term": 1,
     "q": "SI unit-ல் metre-க்கு பயன்படுத்தப்படும் prefix-கள் இரண்டை கூறி, அவை எதைக் குறிக்கும் என்று விளக்குக.",
     "key_facts": ["centi = 1/100", "kilo = 1000"]},
    {"id": "SYN_EN_COMPOUND_1", "lang": "english", "medium": "english", "class_": 6, "term": 1,
     "q": "What is photosynthesis and what is the SI unit of force?",
     "key_facts": ["plants use sunlight water carbon dioxide to make food", "SI unit of force is the newton (N)"]},
    {"id": "SYN_EN_COMPOUND_2", "lang": "english", "medium": "english", "class_": 7, "term": 1,
     "q": "1. What is friction? 2. What is the boiling point of water in Celsius?",
     "key_facts": ["friction opposes relative motion between surfaces", "water boils at 100 degrees Celsius"]},
    {"id": "SYN_TA_COMPOUND_1", "lang": "tamil", "medium": "tamil", "class_": 6, "term": 1,
     "q": "ஒளிச்சேர்க்கை என்றால் என்ன, மற்றும் நீரின் கொதிநிலை என்ன?",
     "key_facts": ["தாவரங்கள் சூரிய ஒளி நீர் கார்பன் டை ஆக்சைடு பயன்படுத்தி உணவு தயாரிக்கின்றன", "நீர் 100 டிகிரி செல்சியஸில் கொதிக்கிறது"]},
]


def call_retrieve(question, class_id, medium, top_k=3, agentic=False):
    payload = {
        "question": question, "detected_language": medium, "class_id": class_id,
        "subject": "auto", "term": 1, "preferred_medium": medium,
        "allowed_content_types": ["textbook", "guide"], "top_k": top_k, "agentic": agentic,
    }
    t0 = time.time()
    r = requests.post(RETRIEVAL_URL, json=payload, timeout=60)
    r.raise_for_status()
    latency_ms = (time.time() - t0) * 1000
    return r.json(), latency_ms


def call_generate_stream(query, context, language, system_prompt):
    payload = {"query": query, "context": context, "language": language, "history_summary": "", "system_prompt": system_prompt}
    t0 = time.time()
    r = requests.post(GENERATION_STREAM_URL, json=payload, stream=True, timeout=1800)
    r.raise_for_status()
    answer = ""
    for line in r.iter_lines():
        if not line:
            continue
        decoded = line.decode("utf-8")
        if not decoded.startswith("data: "):
            continue
        chunk = decoded[len("data: "):].strip()
        if chunk in ("[DONE]", ""):
            continue
        try:
            data = json.loads(chunk)
        except json.JSONDecodeError:
            continue
        if "token" in data:
            answer += data["token"]
    return answer, (time.time() - t0) * 1000


def call_generate_verified(query, context, language, system_prompt, key_facts, alt_context):
    payload = {"query": query, "context": context, "language": language, "history_summary": "",
               "system_prompt": system_prompt, "verify": True, "key_facts": key_facts, "alt_context": alt_context}
    r = requests.post(GENERATION_VERIFIED_URL, json=payload, timeout=7200)  # server-side budget can reach gen+judge(x2 attempts)+retry, all at 1800s each
    r.raise_for_status()
    return r.json()


def run_off(item):
    """Current production default: single-pass retrieval (agentic=False), streamed
    generation, harness-side judging (mirrors evaluate_generation.py's inline-judge mode)."""
    retrieval, retrieval_ms = call_retrieve(item["q"], item["class_"], item["medium"], top_k=3, agentic=False)
    chunks = retrieval.get("results", [])
    context = "\n".join(c["text"] for c in chunks)
    system_prompt = retrieval.get("diagnostics", {}).get("system_prompt")
    answer, gen_ms = call_generate_stream(item["q"], context, item["medium"], system_prompt)
    t0 = time.time()
    judge_model = eg.pick_judge_model(None)
    judgement = eg.judge_answer(judge_model, item["q"], context, answer, item.get("key_facts", []), max_attempts=2, timeout_s=1800)
    judge_ms = (time.time() - t0) * 1000
    composite = None
    if isinstance(judgement, dict) and all(k in judgement for k in ("correctness", "groundedness", "faithfulness")):
        composite = sum(judgement[k] for k in ("correctness", "groundedness", "faithfulness")) / 3
    return {
        "condition": "agentic_off", "answer": answer, "judge": judgement, "composite_score": composite,
        "retrieval_latency_ms": retrieval_ms, "generation_latency_ms": gen_ms, "verify_latency_ms": judge_ms,
        "total_latency_ms": retrieval_ms + gen_ms + judge_ms,
        "n_chunks": len(chunks), "agentic_diagnostics": None,
        "retried_with_alt_context": False, "low_confidence_flag": False,
    }


def run_on(item):
    """Agentic path: decomposition + confidence-gated retrieval (top_k=6 so ranks 4-6 are
    available as alt_context for the verification retry leg), then /generate/verified."""
    retrieval, retrieval_ms = call_retrieve(item["q"], item["class_"], item["medium"], top_k=6, agentic=True)
    chunks = retrieval.get("results", [])
    primary_chunks, alt_chunks = chunks[:3], chunks[3:6]
    context = "\n".join(c["text"] for c in primary_chunks)
    alt_context = "\n".join(c["text"] for c in alt_chunks) if alt_chunks else None
    system_prompt = retrieval.get("diagnostics", {}).get("system_prompt")
    agentic_diag = retrieval.get("diagnostics", {}).get("agentic")

    verified = call_generate_verified(item["q"], context, item["medium"], system_prompt,
                                       item.get("key_facts", []), alt_context)
    return {
        "condition": "agentic_on", "answer": verified["answer"], "judge": verified["judge"],
        "composite_score": verified["composite_score"],
        "retrieval_latency_ms": retrieval_ms, "generation_latency_ms": verified["gen_latency_ms"],
        "verify_latency_ms": verified["judge_latency_ms"], "retry_latency_ms": verified["retry_latency_ms"],
        "total_latency_ms": retrieval_ms + verified["total_latency_ms"],
        "n_chunks": len(primary_chunks), "agentic_diagnostics": agentic_diag,
        "retried_with_alt_context": verified["retried_with_alt_context"],
        "low_confidence_flag": verified["low_confidence_flag"],
    }


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(RESULTS_DIR, "phase4_agentic_results.json")

    # Resumable (this machine's per-item cost is large enough that a late failure
    # shouldn't throw away everything completed so far -- same checkpoint philosophy as
    # evaluate_generation.py's Checkpoint class, simplified since this eval is much smaller).
    results, failures = [], []
    if os.path.exists(out_path):
        try:
            prior = json.load(open(out_path, "r", encoding="utf-8"))
            if prior.get("status") in ("in_progress", "complete"):
                results = prior.get("items", [])
                failures = prior.get("failures", [])
                print(f"Resuming: {len(results)} item(s) already done.", flush=True)
        except (json.JSONDecodeError, OSError):
            pass
    done_ids = {r["id"] for r in results}

    for i, item in enumerate(ITEMS):
        if item["id"] in done_ids:
            continue
        try:
            print(f"[{i+1}/{len(ITEMS)}] {item['id']} -- agentic OFF ...", flush=True)
            off = run_off(item)
            print(f"  OFF done: total={off['total_latency_ms']:.0f}ms composite={off['composite_score']}", flush=True)
            print(f"[{i+1}/{len(ITEMS)}] {item['id']} -- agentic ON ...", flush=True)
            on = run_on(item)
            print(f"  ON done: total={on['total_latency_ms']:.0f}ms composite={on['composite_score']} "
                  f"decomposed={(on['agentic_diagnostics'] or {}).get('decomposed')}", flush=True)
        except Exception as e:
            print(f"  FAILED on {item['id']}: {type(e).__name__}: {e}", flush=True)
            failures.append({"id": item["id"], "error": f"{type(e).__name__}: {e}"})
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump({"status": "in_progress", "items": results, "failures": failures}, f, ensure_ascii=False, indent=2)
            continue
        results.append({"id": item["id"], "lang": item["lang"], "q": item["q"], "off": off, "on": on})
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({"status": "in_progress", "items": results, "failures": failures}, f, ensure_ascii=False, indent=2)

    final = {
        "status": "complete",
        "failures": failures,
        "git_commit": "TODO -- fill in after committing Phase 4 code; this results file is committed as the "
                       "immediate next commit referencing that hash, per the project's established convention",
        "hardware_caveat": (
            "This machine had heavy, unrelated concurrent CPU load during this run (multiple IDE instances, "
            "Steam, Epic Games Launcher, uTorrent all observed competing for CPU via Get-Process at the time "
            "of the initial /generate/verified smoke test, which measured ~350s for one generation+judge call "
            "on a trivial English question). Absolute latency numbers below are NOT a clean CPU-only-hardware "
            "benchmark. The relative agentic ON-vs-OFF comparison is still meaningful: both conditions for a "
            "given item ran back-to-back under the same contention."
        ),
        "method": (
            "6 hand-picked items (not the full 156-item gold set -- infeasible at ~350s/generation+judge call "
            "on this machine): 3 natural gold-set items (EN_003, TA_001, BI_001, all single-hop by the "
            "decomposition heuristic) + 3 synthesized genuinely-compound questions (the gold set was not "
            "authored with multi-hop questions in mind, so decomposition needed synthetic examples to exercise "
            "it at all). agentic_off = current production default (single-pass retrieval, streamed generation, "
            "harness-side judging via judge_answer(), mirroring evaluate_generation.py's inline-judge mode). "
            "agentic_on = query decomposition + confidence-gated retrieval (top_k=6 so ranks 4-6 are available "
            "as alt_context) + /generate/verified (verify=True, same judge_answer() function, called "
            "server-side this time as the live guardrail)."
        ),
        "items": results,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
