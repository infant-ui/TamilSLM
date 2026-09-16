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
    .\\.venv\\Scripts\\python.exe evaluation\\scripts\\evaluate_generation.py [--limit N] [--judge-model MODEL]

Writes: evaluation/results/generation_results.json
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
ANSWER_MODEL = "qwen2.5:7b-instruct-q4_k_m"  # the model actually configured in generation-service/app.py

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
    r = requests.post(GENERATION_URL, json=payload, stream=True, timeout=180)
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
    return answer


def judge_answer(judge_model, question, context, answer, key_facts):
    prompt = JUDGE_RUBRIC_PROMPT.format(
        question=question, context=(context or "(no context retrieved)"),
        key_facts="; ".join(key_facts) if key_facts else "(none listed)", answer=answer,
    )
    payload = {"model": judge_model, "prompt": prompt, "stream": False, "format": "json",
               "options": {"temperature": 0.0}}
    r = requests.post(OLLAMA_GENERATE_URL, json=payload, timeout=120)
    r.raise_for_status()
    raw = r.json().get("response", "{}")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
        return {"_judge_parse_error": True, "_raw": raw}


def run_core_and_oos(dataset, judge_model, limit=None):
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
    if limit:
        items = items[:limit]

    results = []
    for i, item in enumerate(items):
        lang = item["lang"]
        toggles = {"english": ["english"], "tamil": ["tamil"],
                   "bilingual": ["english", "tamil"], "tanglish": ["english", "tamil"]}[lang]
        for medium in toggles:
            print(f"[{i+1}/{len(items)}] {item['id']} (toggle={medium}) ...")
            try:
                retrieval = call_retrieve(item["q"], item.get("class_"), item.get("term"), medium)
            except Exception as e:
                print(f"  retrieval failed: {e}")
                continue
            chunks = retrieval.get("results", [])
            context_text = "\n".join(c["text"] for c in chunks)
            resolved_medium = retrieval.get("medium", medium)
            system_prompt = retrieval.get("diagnostics", {}).get("system_prompt")

            t0 = time.time()
            try:
                answer = call_generate(item["q"], context_text, resolved_medium, system_prompt)
            except Exception as e:
                print(f"  generation failed: {e}")
                continue
            gen_latency_ms = (time.time() - t0) * 1000

            judged = judge_answer(judge_model, item["q"], context_text, answer, item.get("key_facts", []))

            results.append({
                "id": item["id"], "lang": lang, "toggle_medium": medium,
                "resolved_medium": resolved_medium, "fallback_applied": retrieval.get("fallback_applied"),
                "n_chunks_retrieved": len(chunks), "gen_latency_ms": gen_latency_ms,
                "answer": answer, "judge": judged,
            })
    return results


def run_language_instruction(dataset, judge_model):
    results = []
    for item in dataset["language_instruction"]:
        # This suite bypasses retrieval and sends the instruction directly as
        # part of the query, using a neutral system prompt, to isolate pure
        # instruction-following behaviour from retrieval/grounding effects.
        combined_query = f"{item['instruction']}\n\n{item['underlying_q']}"
        neutral_system_prompt = (
            "You are a helpful bilingual (Tamil/English) science tutor. Follow the student's "
            "language instruction exactly."
        )
        try:
            answer = call_generate(combined_query, "", "english", neutral_system_prompt)
        except Exception as e:
            print(f"  generation failed for {item['id']}: {e}")
            continue
        has_tamil = bool(re.search(r"[஀-௿]", answer))
        has_latin = bool(re.search(r"[A-Za-z]{3,}", answer))
        detected_script = "mixed" if (has_tamil and has_latin) else ("tamil" if has_tamil else "latin")
        results.append({
            "id": item["id"], "instruction": item["instruction"], "expected_script": item["expect_script"],
            "detected_script": detected_script, "answer": answer,
        })
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Limit number of core items (for a quick smoke run)")
    parser.add_argument("--judge-model", type=str, default=None)
    args = parser.parse_args()

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    judge_model = pick_judge_model(args.judge_model)
    print(f"Using judge model: {judge_model} (answer model is always {ANSWER_MODEL}, per generation-service/app.py)")

    core_results = run_core_and_oos(dataset, judge_model, limit=args.limit)
    li_results = run_language_instruction(dataset, judge_model)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(RESULTS_DIR, "generation_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "answer_model": ANSWER_MODEL, "judge_model": judge_model,
            "core_and_out_of_scope": core_results, "language_instruction": li_results,
        }, f, ensure_ascii=False, indent=2)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
