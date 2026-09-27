# evaluation/scripts/evaluate_generation.py
"""
End-to-end generation evaluation: calls your ACTUAL running services (not a
reimplementation) for every gold question, then scores each answer with an
LLM-as-judge using a structured rubric.

PREREQUISITES (matches start.bat):
  - Ollama Desktop running (port 11434) with qwen2.5:7b-instruct-q4_k_m pulled.
  - Retrieval service running on http://127.0.0.1:8000  (uvicorn main:app --port 8000)
  - Generation service running on http://127.0.0.1:8001 (uvicorn app:app --port 8001)
  You do not need the gateway, Redis, or frontend for this script -- it talks
  to retrieval-service and generation-service directly, the same two calls
  gateway/app.js makes in /query/stream.

USAGE:
    .\\.venv\\Scripts\\python.exe evaluation\\scripts\\evaluate_generation.py [--limit N] [--judge-model MODEL] [--answer-model NAME]

    --answer-model is a LABEL for the report/output filename -- it must match
    whatever Ollama model generation-service/app.py was actually started
    with (via the OLLAMA_MODEL env var), since this script always calls the
    live generation-service over HTTP rather than Ollama directly for the
    answer itself. To run a second/third comparison arm (e.g. Tamil-LLaMA,
    Sarvam-M), restart generation-service with OLLAMA_MODEL=<ollama model
    name> set, then rerun this script with --answer-model <same name>.

    --gen-timeout SECONDS  read timeout for one streamed answer (default 180,
                           unchanged for existing arms). It bounds the wait for
                           the FIRST token (model load + prompt evaluation) and
                           each gap between tokens, so slow CPU-bound models
                           need a much larger value.
    --two-phase            generate every answer first, then judge them all in a
                           second pass. Same judge and prompts as inline mode;
                           it only avoids reloading the answer and judge models
                           in Ollama for every item when both cannot stay
                           resident in RAM.

    --tokenizer HF_REPO        HF tokenizer of the ANSWER model (e.g. Qwen/Qwen2.5-7B-Instruct). Lets the
                               truncation guard size the true prompt and compare it with the count Ollama
                               actually evaluated. Every entry records prompt_eval_count either way.
    --fail-on-truncation       treat a suspected truncation as a failure (entry not stored, retried on resume)
                               instead of only flagging it.
    --only-keys PATH           JSON list of "id|toggle" keys: generate ONLY these (skips language-instruction).
    --output PATH              write the results file here instead of the default per-model name.
    --judge-num-ctx N          num_ctx for the judge model (default: Ollama's default window, 4096).

    Silent prompt truncation: Ollama's own engine keeps only the LAST ~half window of an over-long prompt
    (dropping the instruction block at the start of the system prompt) and returns no error. Run
    generation-service with OLLAMA_NUM_CTX large enough (Qwen2.5 Tamil-context prompts reach ~10.7K tokens).

    --snapshot-contexts PATH   fetch the retrieval result (context, medium, system
                               prompt) for every item/toggle from the live
                               retrieval-service once, save it to PATH and exit.
    --contexts-from PATH       use that snapshot instead of calling retrieval-service
                               during generation, so the retrieval-service (and its
                               GPU/RAM) can be stopped while a big model runs. Retrieval
                               is deterministic, so this feeds the model exactly what a
                               live call would have returned.

    Failures (retrieval or generation errors) are never dropped silently: they
    are printed and stored under "failures" in the results file.

Writes: evaluation/results/generation_results.json for the default model
(qwen2.5:7b-instruct-q4_k_m, unchanged filename for backward compatibility),
or evaluation/results/generation_results_<answer-model-slug>.json otherwise.
"""
import argparse
import json
import os
import re
import time

import requests

RETRIEVAL_URL = "http://127.0.0.1:8000/retrieve"
GENERATION_URL = "http://127.0.0.1:8001/generate/stream"
OLLAMA_TAGS_URL = "http://127.0.0.1:11434/api/tags"
OLLAMA_GENERATE_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_ANSWER_MODEL = "qwen2.5:7b-instruct-q4_k_m"
ANSWER_MODEL = DEFAULT_ANSWER_MODEL  # overwritten in main() from --answer-model; see USAGE above
GEN_TIMEOUT_S = 180  # overwritten in main() from --gen-timeout
LAST_GEN_META = {}          # filled by call_generate from the service's final SSE chunk
JUDGE_NUM_CTX = None        # None = Ollama's default window for the judge; set from --judge-num-ctx
TOKENIZER = None            # optional HF tokenizer of the ANSWER model (--tokenizer), for the truncation guard
FAIL_ON_TRUNCATION = False  # --fail-on-truncation
ASSUMED_NUM_PREDICT = 1000  # generation-service's num_predict


def _model_slug(name: str) -> str:
    """Filesystem-safe slug for use in an output filename, e.g.
    'tamil-llama-7b-instruct-v0.2' or 'sarvam-m'."""
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", name.strip()).strip("-").lower()

HERE = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(HERE, "..", "datasets", "gold_dataset.json")
RESULTS_DIR = os.path.join(HERE, "..", "results")

JUDGE_RUBRIC_PROMPT = """You are a strict, technical evaluator of an educational RAG system's answer.
You will be given a QUESTION, the RETRIEVED CONTEXT the system had available, the system's ANSWER,
and (if available) a REFERENCE set of key facts the answer should cover.

Score the ANSWER on each of these dimensions from 0 to 5 (integers), plus two 0/1 flags:
- correctness: is the answer factually correct given the context and general subject-matter knowledge?
- relevance: does it directly answer what was asked?
- completeness: does it cover the key reference facts listed below?
- groundedness: is the answer's content actually supported by the retrieved context (not outside knowledge)?
- faithfulness: does the answer avoid contradicting the retrieved context?
- language_quality: is the answer grammatically natural in the language it responds in (fluent, not
  literal/machine-translated-sounding, correct terminology)?
- educational_suitability: is the explanation pitched appropriately for a Grade 6 student?
- hallucination (0 or 1): 1 if the answer states specific facts/figures NOT present in the retrieved
  context and not common knowledge trivially implied by it, else 0.
- abstained (0 or 1): 1 if the answer explicitly says the information is not available / it doesn't know,
  rather than attempting a full answer.
- response_language: one of "tamil", "english", "mixed" -- the actual language/script the answer is
  written in (judge this from the literal text, not from what was asked).

QUESTION: {question}

RETRIEVED CONTEXT (may be empty if nothing was retrieved):
{context}

REFERENCE KEY FACTS (for completeness scoring only; the answer need not match wording):
{key_facts}

ANSWER:
{answer}

Return ONLY a single valid JSON object with exactly these keys:
correctness, relevance, completeness, groundedness, faithfulness, language_quality,
educational_suitability, hallucination, abstained, response_language
"""


def pick_judge_model(cli_override):
    if cli_override:
        return cli_override
    try:
        tags = requests.get(OLLAMA_TAGS_URL, timeout=5).json().get("models", [])
        names = [m.get("name", "") for m in tags]
        # Prefer a model different from the answer-generation model, to reduce
        # the self-grading bias of using the same model as both generator and judge.
        for candidate in ["llama3.1:latest", "llama3.1:8b", "llama3:latest", "mistral:latest"]:
            if candidate in names:
                return candidate
        print(f"[warn] No distinct judge model found among installed Ollama models {names}. "
              f"Falling back to {ANSWER_MODEL} as its own judge -- treat groundedness/hallucination "
              f"scores with extra caution (self-grading bias). Install a second model "
              f"(e.g. `ollama pull llama3.1`) for a more independent judge.")
    except Exception as e:
        print(f"[warn] Could not query Ollama /api/tags ({e}); defaulting judge to {ANSWER_MODEL}.")
    return ANSWER_MODEL


def call_retrieve(question, class_id, term, preferred_medium, detected_language="english"):
    payload = {
        "question": question, "detected_language": detected_language, "class_id": class_id,
        "subject": "auto", "term": term, "preferred_medium": preferred_medium,
        "allowed_content_types": ["textbook", "guide"], "include_previous_years": False,
        "fallback_language_allowed": False, "top_k": 3,
    }
    r = requests.post(RETRIEVAL_URL, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()


def call_generate(query, context, language, system_prompt):
    payload = {"query": query, "context": context, "language": language,
               "history_summary": "", "system_prompt": system_prompt}
    LAST_GEN_META.clear()
    r = requests.post(GENERATION_URL, json=payload, stream=True, timeout=GEN_TIMEOUT_S)
    r.raise_for_status()
    answer = ""
    for line in r.iter_lines():
        if not line:
            continue
        decoded = line.decode("utf-8")
        if not decoded.startswith("data: "):
            continue
        chunk = decoded[len("data: "):].strip()
        if chunk == "[DONE]" or not chunk:
            continue
        try:
            data = json.loads(chunk)
        except json.JSONDecodeError:
            continue
        if "token" in data:
            answer += data["token"]
        if "error" in data:
            answer += f"\n[GENERATION ERROR: {data['error']}]"
        if data.get("done") or "prompt_eval_count" in data:
            LAST_GEN_META.update({k: data.get(k) for k in ("prompt_eval_count", "eval_count", "done_reason", "num_ctx")})
    return answer


NUMERIC_DIMS = ["correctness", "relevance", "completeness", "groundedness",
                "faithfulness", "language_quality", "educational_suitability"]
FLAG_DIMS = ["hallucination", "abstained"]
GEN_ERROR_MARKER = "[GENERATION ERROR"


def validate_judgement(j):
    """Return (clean_judgement, None) if `j` obeys the rubric's stated scales, else (None, reason).

    The 7 dimensions must be integers 0-5, the two flags 0/1, and response_language
    a string. llama3.1 occasionally answers on a 0-1 scale (e.g. correctness 0.8),
    which silently deflates means, so such replies are treated as invalid.
    """
    if not isinstance(j, dict):
        return None, "reply is not a JSON object"
    clean = dict(j)
    for k in NUMERIC_DIMS:
        v = j.get(k)
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return None, f"{k} is missing or not numeric ({v!r})"
        if float(v) != int(v) or not 0 <= v <= 5:
            return None, f"{k}={v} is not an integer in 0-5"
        clean[k] = int(v)
    for k in FLAG_DIMS:
        v = j.get(k)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v not in (0, 1):
            return None, f"{k}={v!r} is not 0 or 1"
        clean[k] = int(v)
    if not isinstance(j.get("response_language"), str):
        return None, "response_language missing"
    return clean, None


def judge_answer(judge_model, question, context, answer, key_facts, max_attempts=2, timeout_s=240):
    """
    Calls the Ollama judge model. Tolerates a slow/cold model load or a
    transient failure instead of crashing the whole run (2026-09-17: one
    uncaught ReadTimeout lost 37 finished items). A reply that parses but
    violates the rubric's scales (fractional or out-of-range scores, flags other
    than 0/1) is invalid: it is retried once with an explicit correction, and if
    it is still invalid the result is {"_judge_invalid": reason, ...} -- never
    passed through as if it were a real score.
    """
    base_prompt = JUDGE_RUBRIC_PROMPT.format(
        question=question, context=(context or "(no context retrieved)"),
        key_facts="; ".join(key_facts) if key_facts else "(none listed)", answer=answer,
    )
    prompt, temperature = base_prompt, 0.0
    last_error, last_invalid, last_parse_raw, pec = None, None, None, None
    for attempt in range(1, max_attempts + 1):
        options = {"temperature": temperature}
        if JUDGE_NUM_CTX:
            options["num_ctx"] = JUDGE_NUM_CTX
        payload = {"model": judge_model, "prompt": prompt, "stream": False, "format": "json", "options": options}
        try:
            r = requests.post(OLLAMA_GENERATE_URL, json=payload, timeout=timeout_s)
            r.raise_for_status()
            jr = r.json()
            raw, pec = jr.get("response", "{}"), jr.get("prompt_eval_count")
            window = JUDGE_NUM_CTX or 4096
            if pec is not None and pec >= 0.95 * window:
                print(f"  WARNING: judge prompt evaluated {pec} tokens, at its {window}-token window: it may be truncated", flush=True)
        except Exception as e:
            last_error = str(e)
            print(f"  judge call failed (attempt {attempt}/{max_attempts}): {last_error}", flush=True)
            continue
        parsed = None
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            if m:
                try:
                    parsed = json.loads(m.group(0))
                except json.JSONDecodeError:
                    parsed = None
        if parsed is None:
            return {"_judge_parse_error": True, "_raw": raw, "_judge_prompt_eval_count": pec}
        clean, reason = validate_judgement(parsed)
        if clean is not None:
            if attempt > 1:
                clean["_judge_retried_for"] = last_invalid
            clean["_judge_prompt_eval_count"] = pec
            return clean
        last_invalid, last_parse_raw = reason, parsed
        print(f"  judge reply invalid ({reason}); attempt {attempt}/{max_attempts}", flush=True)
        prompt = (base_prompt + f"\n\nIMPORTANT: your previous reply was invalid ({reason}). Reply again with ONLY the "
                  "JSON object. Every score must be an INTEGER from 0 to 5 (not a fraction and not a 0-1 scale); "
                  "hallucination and abstained must each be exactly 0 or 1.")
        temperature = 0.1  # a temperature-0 retry would just repeat the same invalid reply
    if last_invalid:
        return {"_judge_invalid": last_invalid, "_raw_reply": last_parse_raw, "_judge_prompt_eval_count": pec}
    return {"_judge_call_failed": True, "_error": last_error}


TOGGLES = {"english": ["english"], "tamil": ["tamil"],
           "bilingual": ["english", "tamil"], "tanglish": ["english", "tamil"]}


def hard_failure_judgement(reason):
    """Score used when the model produced no answer at all: 0 on every numeric dimension,
    no judge call. Flags are None so the failure counts in neither the hallucination nor
    the abstention rate."""
    j = {k: 0 for k in NUMERIC_DIMS}
    j.update({"hallucination": None, "abstained": None, "response_language": "none", "_hard_failure": reason})
    return j


def generate_with_retry(query, context, language, system_prompt):
    """Generate an answer; retry once if it comes back empty/whitespace or as an infrastructure
    error string (Ollama assigns a fresh random seed per request). Returns
    (answer, attempts, first_attempt_empty, meta) where meta is the service's final-chunk counters
    (prompt_eval_count, eval_count, done_reason, num_ctx) of the LAST attempt. Raises if the call itself raises."""
    first_empty = None
    answer, attempts = "", 0
    for attempts in (1, 2):
        answer = call_generate(query, context, language, system_prompt)
        empty = not answer.strip()
        if first_empty is None:
            first_empty = empty
        if not empty and GEN_ERROR_MARKER not in answer:
            break
        print(f"  {'empty answer' if empty else 'generation error text'} on attempt {attempts}", flush=True)
    return answer, attempts, bool(first_empty), dict(LAST_GEN_META)


def build_items(dataset, limit=None):
    items = dataset["core"] + [
        # Deliberately leave class_/term unset (None): a real student asking an
        # out-of-syllabus question wouldn't know to scope it either, and this
        # is also the more revealing test -- it lets us see whether the system
        # silently serves back same-subject Class 6 content as if it answered
        # the (different-class) question, rather than recognising the gap.
        {**o, "id": o["id"], "class_": None, "term": None, "unit": "OUT_OF_SCOPE", "pages": [],
         "difficulty": "n/a", "qtype": "adversarial", "key_facts": []}
        for o in dataset["out_of_scope"]
    ]
    return items[:limit] if limit else items


def expected_item_toggles(items):
    return sum(len(TOGGLES[it["lang"]]) for it in items)


class Checkpoint:
    """
    Single source of truth for one run. The output file IS the checkpoint: it is
    rewritten (status "in_progress") after every completed unit of work, and a
    rerun resumes from it instead of starting over (fix for 2026-09-17, when one
    uncaught judge timeout lost 37 finished items). Failures are recorded, never
    dropped silently; they are not carried across a resume, so anything that
    failed is simply attempted again.
    """

    def __init__(self, path, judge_model, run_info=None):
        self.path, self.judge_model, self.run_info = path, judge_model, run_info or {}
        self.results, self.li_results, self.failures = [], [], []
        if path and os.path.exists(path):
            prior = {}
            try:
                with open(path, "r", encoding="utf-8") as f:
                    prior = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Could not read checkpoint ({e}); starting fresh.")
            if prior.get("status") == "in_progress":
                if prior.get("answer_model") not in (None, ANSWER_MODEL):
                    print(f"Checkpoint belongs to answer model {prior.get('answer_model')!r}, not "
                          f"{ANSWER_MODEL!r}; starting fresh.")
                else:
                    self.results = prior.get("core_and_out_of_scope", [])
                    self.li_results = prior.get("language_instruction", [])
                    print(f"Resuming from checkpoint: {len(self.results)} item/toggle results and "
                          f"{len(self.li_results)} language-instruction results already done.")

    def save(self, status="in_progress"):
        if not self.path:
            return
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({
                "status": status, "answer_model": ANSWER_MODEL, "judge_model": self.judge_model,
                **self.run_info,
                "core_and_out_of_scope": self.results, "language_instruction": self.li_results,
                "failures": self.failures,
            }, f, ensure_ascii=False, indent=2)

    def fail(self, **info):
        self.failures.append(info)
        self.save()


def _snap_key(item_id, medium):
    return f"{item_id}|{medium}"


def fetch_retrieval(item, medium):
    """One live retrieval call, reduced to exactly what generation needs."""
    retrieval = call_retrieve(item["q"], item.get("class_"), item.get("term"), medium)
    chunks = retrieval.get("results", [])
    return {
        "context": "\n".join(c["text"] for c in chunks),
        "medium": retrieval.get("medium", medium),
        "fallback_applied": retrieval.get("fallback_applied"),
        "n_chunks": len(chunks),
        "system_prompt": retrieval.get("diagnostics", {}).get("system_prompt"),
    }


def build_context_snapshot(dataset, path, limit=None):
    """Paced (retrieval-service allows 30 requests/min) live fetch of every item/toggle."""
    items = build_items(dataset, limit)
    entries = {}
    for i, item in enumerate(items):
        for medium in TOGGLES[item["lang"]]:
            while True:
                try:
                    entries[_snap_key(item["id"], medium)] = fetch_retrieval(item, medium)
                    break
                except requests.HTTPError as e:
                    if e.response is not None and e.response.status_code == 429:
                        time.sleep(10)
                        continue
                    raise
            print(f"[snapshot {i+1}/{len(items)}] {item['id']} ({medium})", flush=True)
            time.sleep(2.1)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"created": time.strftime("%Y-%m-%d %H:%M:%S"), "top_k": 3, "entries": entries}, f, ensure_ascii=False, indent=1)
    print(f"Wrote {len(entries)} retrieval snapshots to {path}")


def assemble_system_prompt(system_prompt, context, language):
    """Mirror of generation-service's system-prompt assembly, needed to size the real prompt."""
    if not system_prompt:
        return None
    if "Textbook Context" not in system_prompt and "\u0baa\u0bbe\u0b9f\u0baa\u0bcd \u0baa\u0bc1\u0ba4\u0bcd\u0ba4\u0b95\u0baa\u0bcd \u0baa\u0b95\u0bc1\u0ba4\u0bbf" not in system_prompt:
        if (language or "").lower() == "tamil":
            return f"{system_prompt}\n\n\u0baa\u0bbe\u0b9f\u0baa\u0bcd \u0baa\u0bc1\u0ba4\u0bcd\u0ba4\u0b95\u0baa\u0bcd \u0baa\u0b95\u0bc1\u0ba4\u0bbf (Textbook Context):\n{context}"
        return f"{system_prompt}\n\nTextbook Context:\n{context}"
    return system_prompt


def expected_prompt_tokens(system_text, question):
    """True length of system+user text in the ANSWER model's own tokenizer (None if no --tokenizer)."""
    if TOKENIZER is None or system_text is None:
        return None
    return len(TOKENIZER(system_text + "\n" + question, add_special_tokens=False)["input_ids"])


def truncation_check(meta, expected_tokens):
    """Compare what Ollama actually evaluated with the true prompt length. Never raises."""
    evaluated, num_ctx = meta.get("prompt_eval_count"), meta.get("num_ctx")
    out = {"prompt_eval_count": evaluated, "eval_count": meta.get("eval_count"), "done_reason": meta.get("done_reason"),
           "num_ctx": num_ctx, "expected_prompt_tokens": expected_tokens, "truncation_suspected": False,
           "truncation_signature": False, "window_tight": bool(expected_tokens and num_ctx and expected_tokens + ASSUMED_NUM_PREDICT > num_ctx),
           "truncation_reason": None}
    if evaluated is None:
        out["truncation_reason"] = "no prompt_eval_count reported (generation-service too old?) -- truncation cannot be ruled out"
        return out
    if expected_tokens is not None and evaluated < 0.95 * expected_tokens:
        out.update(truncation_suspected=True, truncation_reason=f"Ollama evaluated {evaluated} tokens but the prompt is ~{expected_tokens}")
    elif num_ctx and evaluated >= num_ctx - 1:
        out.update(truncation_suspected=True, truncation_reason=f"evaluated count {evaluated} is at the {num_ctx}-token window limit")
    if num_ctx and expected_tokens is None and abs(evaluated - (num_ctx // 2 + 2)) <= 16:
        out["truncation_signature"] = True   # heuristic only: Ollama keeps ~half the window when it truncates
    return out


def generate_core(dataset, ckpt, judge_model, limit=None, judge_inline=True, contexts=None, only_keys=None):
    """Retrieve + generate (+ judge, unless judge_inline is False) for every item/toggle.
    With `contexts` (a snapshot's 'entries'), retrieval is read from it instead of the live service.
    With `only_keys` (a set of "id|toggle"), only those item/toggles are generated."""
    items = build_items(dataset, limit)
    done_keys = {(r["id"], r["toggle_medium"]) for r in ckpt.results}
    for i, item in enumerate(items):
        lang = item["lang"]
        for medium in TOGGLES[lang]:
            if (item["id"], medium) in done_keys:
                continue
            if only_keys is not None and _snap_key(item["id"], medium) not in only_keys:
                continue
            print(f"[{i+1}/{len(items)}] {item['id']} (toggle={medium}) ...", flush=True)
            try:
                if contexts is not None:
                    snap = contexts.get(_snap_key(item["id"], medium))
                    if snap is None:
                        raise KeyError("no entry in the contexts snapshot")
                else:
                    snap = fetch_retrieval(item, medium)
            except Exception as e:
                print(f"  retrieval failed: {e}", flush=True)
                ckpt.fail(id=item["id"], toggle_medium=medium, stage="retrieval", error=str(e))
                continue
            context_text, resolved_medium = snap["context"], snap["medium"]
            system_prompt, n_chunks, fallback_applied = snap["system_prompt"], snap["n_chunks"], snap["fallback_applied"]

            t0 = time.time()
            try:
                answer, attempts, first_empty, meta = generate_with_retry(item["q"], context_text, resolved_medium, system_prompt)
            except Exception as e:
                print(f"  generation failed: {e}", flush=True)
                ckpt.fail(id=item["id"], toggle_medium=medium, stage="generation", error=str(e))
                continue
            gen_latency_ms = (time.time() - t0) * 1000
            if GEN_ERROR_MARKER in answer:  # infrastructure error, not a model output: record and retry on resume
                ckpt.fail(id=item["id"], toggle_medium=medium, stage="generation", error=answer.strip()[:300])
                continue
            chk = truncation_check(meta, expected_prompt_tokens(assemble_system_prompt(system_prompt, context_text, resolved_medium), item["q"]))
            if chk["truncation_suspected"]:
                print(f"  TRUNCATION SUSPECTED: {chk['truncation_reason']}", flush=True)
                if FAIL_ON_TRUNCATION:
                    ckpt.fail(id=item["id"], toggle_medium=medium, stage="truncation", error=chk["truncation_reason"])
                    continue

            entry = {
                "id": item["id"], "lang": lang, "toggle_medium": medium,
                "resolved_medium": resolved_medium, "fallback_applied": fallback_applied,
                "n_chunks_retrieved": n_chunks, "gen_latency_ms": gen_latency_ms,
                "attempts": attempts, "first_attempt_empty": first_empty,
                "answer": answer, "judge": None,
                "retrieved_context": context_text,  # kept so any arm can be re-judged later
                **chk,
            }
            if not answer.strip():
                entry["judge"] = hard_failure_judgement("empty_answer_after_retry")
                print("  HARD FAILURE: empty after retry -> scored 0 on every dimension, judge skipped", flush=True)
            elif judge_inline:
                entry["judge"] = judge_answer(judge_model, item["q"], context_text, answer, item.get("key_facts", []))
            ckpt.results.append(entry)
            ckpt.save()


def judge_pending(dataset, ckpt, judge_model):
    """Judge every stored answer that has no judgement yet (second pass of --two-phase)."""
    lookup = {it["id"]: it for it in build_items(dataset)}
    pending = [r for r in ckpt.results if r.get("judge") is None]
    for n, r in enumerate(pending, 1):
        print(f"[judge {n}/{len(pending)}] {r['id']} (toggle={r['toggle_medium']}) ...", flush=True)
        ctx = r.get("retrieved_context", r.get("_context"))
        if ctx is None:
            ckpt.fail(id=r["id"], toggle_medium=r["toggle_medium"], stage="judge",
                      error="stored answer has no saved retrieval context to judge against")
            continue
        item = lookup[r["id"]]
        r["judge"] = judge_answer(judge_model, item["q"], ctx, r["answer"], item.get("key_facts", []))
        r.pop("_context", None)
        ckpt.save()


def run_language_instruction(dataset, ckpt):
    done_ids = {r["id"] for r in ckpt.li_results}
    for item in dataset["language_instruction"]:
        if item["id"] in done_ids:
            continue
        # This suite bypasses retrieval and sends the instruction directly as
        # part of the query, using a neutral system prompt, to isolate pure
        # instruction-following behaviour from retrieval/grounding effects.
        combined_query = f"{item['instruction']}\n\n{item['underlying_q']}"
        neutral_system_prompt = (
            "You are a helpful bilingual (Tamil/English) science tutor. Follow the student's "
            "language instruction exactly."
        )
        print(f"[language-instruction] {item['id']} ...", flush=True)
        try:
            answer, attempts, first_empty, meta = generate_with_retry(combined_query, "", "english", neutral_system_prompt)
        except Exception as e:
            print(f"  generation failed for {item['id']}: {e}", flush=True)
            ckpt.fail(id=item["id"], stage="language_instruction_generation", error=str(e))
            continue
        if not answer.strip():
            detected_script = "none"
        else:
            has_tamil = bool(re.search(r"[஀-௿]", answer))
            has_latin = bool(re.search(r"[A-Za-z]{3,}", answer))
            detected_script = "mixed" if (has_tamil and has_latin) else ("tamil" if has_tamil else "latin")
        ckpt.li_results.append({
            "id": item["id"], "instruction": item["instruction"], "expected_script": item["expect_script"],
            "detected_script": detected_script, "answer": answer, "attempts": attempts,
            "first_attempt_empty": first_empty, "prompt_eval_count": meta.get("prompt_eval_count"), "num_ctx": meta.get("num_ctx"),
        })
        ckpt.save()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Limit number of core items (for a quick smoke run)")
    parser.add_argument("--judge-model", type=str, default=None)
    parser.add_argument(
        "--answer-model", type=str, default=None,
        help="Label matching the Ollama model generation-service was started with "
             "(OLLAMA_MODEL env var). Defaults to qwen2.5:7b-instruct-q4_k_m. "
             "Only affects labeling/output filename -- does not itself switch models.",
    )
    parser.add_argument("--gen-timeout", type=int, default=180,
                        help="Read timeout (s) for one streamed answer; raise for slow CPU-bound models.")
    parser.add_argument("--two-phase", action="store_true",
                        help="Generate all answers first, then judge them all (same judge/prompts).")
    parser.add_argument("--snapshot-contexts", type=str, default=None, metavar="PATH",
                        help="Fetch every item/toggle's retrieval result once from the live service, save to PATH, exit.")
    parser.add_argument("--contexts-from", type=str, default=None, metavar="PATH",
                        help="Read retrieval results from a snapshot instead of calling retrieval-service.")
    parser.add_argument("--tokenizer", type=str, default=None, metavar="HF_REPO",
                        help="HF tokenizer of the answer model; enables the exact truncation check.")
    parser.add_argument("--fail-on-truncation", action="store_true",
                        help="Record a suspected prompt truncation as a failure instead of only flagging it.")
    parser.add_argument("--only-keys", type=str, default=None, metavar="PATH",
                        help='JSON list of "id|toggle" keys to generate (skips language-instruction).')
    parser.add_argument("--output", type=str, default=None, metavar="PATH", help="Results file path override.")
    parser.add_argument("--judge-num-ctx", type=int, default=None, help="num_ctx for the judge model.")
    args = parser.parse_args()

    global ANSWER_MODEL, GEN_TIMEOUT_S, TOKENIZER, JUDGE_NUM_CTX, FAIL_ON_TRUNCATION
    ANSWER_MODEL = args.answer_model or DEFAULT_ANSWER_MODEL
    GEN_TIMEOUT_S = args.gen_timeout
    JUDGE_NUM_CTX = args.judge_num_ctx
    FAIL_ON_TRUNCATION = args.fail_on_truncation
    if args.tokenizer:
        from transformers import AutoTokenizer
        kw = {"fix_mistral_regex": True} if any(t in args.tokenizer.lower() for t in ("sarvam", "mistral")) else {}
        TOKENIZER = AutoTokenizer.from_pretrained(args.tokenizer, **kw)
        print(f"Truncation guard: exact prompt sizing with the {args.tokenizer} tokenizer", flush=True)
    only_keys = None
    if args.only_keys:
        with open(args.only_keys, "r", encoding="utf-8") as f:
            only_keys = set(json.load(f))
        print(f"--only-keys: generating just {len(only_keys)} item/toggle(s); language-instruction is skipped", flush=True)

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    if args.snapshot_contexts:
        build_context_snapshot(dataset, args.snapshot_contexts, limit=args.limit)
        return
    contexts = None
    if args.contexts_from:
        with open(args.contexts_from, "r", encoding="utf-8") as f:
            contexts = json.load(f)["entries"]
        print(f"Using cached retrieval contexts from {args.contexts_from} ({len(contexts)} entries); "
              f"retrieval-service is not called.")

    judge_model = pick_judge_model(args.judge_model)
    print(f"Using judge model: {judge_model}")
    print(f"Answer model (label only -- must match generation-service's actual "
          f"OLLAMA_MODEL): {ANSWER_MODEL}")
    print(f"gen timeout: {GEN_TIMEOUT_S}s | mode: {'two-phase' if args.two_phase else 'inline judging'}", flush=True)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    if args.output:
        out_path = args.output
    elif ANSWER_MODEL == DEFAULT_ANSWER_MODEL:
        out_path = os.path.join(RESULTS_DIR, "generation_results.json")
    else:
        out_path = os.path.join(RESULTS_DIR, f"generation_results_{_model_slug(ANSWER_MODEL)}.json")

    all_keys = {_snap_key(it["id"], m) for it in build_items(dataset, args.limit) for m in TOGGLES[it["lang"]]}
    if only_keys is not None:
        unknown = only_keys - all_keys
        if unknown:
            raise SystemExit(f"--only-keys contains keys that are not in the evaluation set: {sorted(unknown)[:5]}")
    expected = len(only_keys) if only_keys is not None else expected_item_toggles(build_items(dataset, args.limit))
    ckpt = Checkpoint(out_path, judge_model, run_info={
        "gen_timeout_s": GEN_TIMEOUT_S, "two_phase": bool(args.two_phase), "expected_item_toggles": expected,
        "contexts_from": args.contexts_from, "tokenizer": args.tokenizer, "judge_num_ctx": JUDGE_NUM_CTX,
        "fail_on_truncation": FAIL_ON_TRUNCATION, "only_keys": sorted(only_keys) if only_keys is not None else None,
    })

    generate_core(dataset, ckpt, judge_model, limit=args.limit, judge_inline=not args.two_phase, contexts=contexts,
                  only_keys=only_keys)
    if only_keys is None:
        run_language_instruction(dataset, ckpt)
    judge_pending(dataset, ckpt, judge_model)

    ckpt.save("complete")
    judged = [r for r in ckpt.results if isinstance(r.get("judge"), dict)]
    judge_bad = sum(1 for r in judged if r["judge"].get("_judge_call_failed") or r["judge"].get("_judge_parse_error")
                    or r["judge"].get("_judge_invalid"))
    hard = sum(1 for r in ckpt.results if isinstance(r.get("judge"), dict) and r["judge"].get("_hard_failure"))
    first_empty = sum(1 for r in ckpt.results if r.get("first_attempt_empty"))
    n_pec = sum(1 for r in ckpt.results if r.get("prompt_eval_count") is not None)
    n_trunc = sum(1 for r in ckpt.results if r.get("truncation_suspected"))
    n_sig = sum(1 for r in ckpt.results if r.get("truncation_signature"))
    n_tight = sum(1 for r in ckpt.results if r.get("window_tight"))
    print(f"\nTruncation guard: prompt_eval_count recorded on {n_pec}/{len(ckpt.results)} entries | suspected truncation: {n_trunc} "
          f"| half-window signature (no tokenizer): {n_sig} | prompt+{ASSUMED_NUM_PREDICT} > window (answer may shift context): {n_tight}")
    if n_trunc:
        print("WARNING: prompt truncation suspected for:", [f"{r['id']}|{r['toggle_medium']}" for r in ckpt.results if r.get("truncation_suspected")][:20])
    print(f"\nSummary: {len(ckpt.results)}/{expected} core+OOS item/toggle results | "
          f"{len(ckpt.li_results)}/{0 if only_keys is not None else len(dataset['language_instruction'])} language-instruction | "
          f"empty on first attempt: {first_empty} | hard failures (empty after retry, scored 0): {hard} | "
          f"judge failures/parse errors/invalid: {judge_bad} | recorded failures: {len(ckpt.failures)}")
    if ckpt.failures:
        print("WARNING: some units failed and are NOT in the results (see 'failures' in the file):")
        for fl in ckpt.failures:
            print("  ", fl)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
