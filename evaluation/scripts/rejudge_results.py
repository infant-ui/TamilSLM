# evaluation/scripts/rejudge_results.py
"""
Re-judge the stored answers of a finished generation run with a judge window large enough to hold
the WHOLE judge prompt.

WHY: the judge (llama3.1 via Ollama /api/generate) ran at Ollama's default 4096-token window. Ollama's
own engine silently keeps only the LAST ~2050 tokens of an over-long prompt, so for long retrieved
contexts (especially Tamil script, ~1 token/char) the judge never saw the start of its own rubric
(measured: TA_009 evaluated 2,050 of 11,324 tokens; English EN_004 2,050 of 4,659).

For every entry with a real answer it calls the SAME judge_answer() (same prompt, same validation) with
num_ctx=--judge-num-ctx, keeps the previous judgement under "judge_pre_ctxfix", and records the size of
the judge prompt (`_judge_prompt_eval_count`). Blank answers / hard failures keep their zero scores and
are never sent to the judge. Resumable: entries already re-judged (`judge_num_ctx` set) are skipped, and
an existing --output file is continued.

USAGE:
    python evaluation/scripts/rejudge_results.py --input <results.json> --output <rejudged.json>
"""
import argparse
import importlib.util
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("evgen", os.path.join(HERE, "evaluate_generation.py"))
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)

DIMS = ev.NUMERIC_DIMS


def composite(j):
    v = [j.get(k) for k in DIMS]
    return sum(v) / len(v) if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v) else None


def is_blank(entry):
    j = entry.get("judge")
    return not (entry.get("answer") or "").strip() or (isinstance(j, dict) and bool(j.get("_hard_failure")))


def rejudge(data, items, snap, judge_model, num_ctx, save=lambda: None, log=print):
    """Mutates data['core_and_out_of_scope'] in place. Returns (n_rejudged_now, n_blank_kept, n_already_done)."""
    ev.JUDGE_NUM_CTX = num_ctx
    entries = data["core_and_out_of_scope"]
    todo = [e for e in entries if not is_blank(e) and e.get("judge_num_ctx") != num_ctx]
    for idx, e in enumerate(todo, 1):
        key = f"{e['id']}|{e['toggle_medium']}"
        ctx = e.get("retrieved_context")
        if ctx is None:
            ctx = snap[key]["context"]
        item = items[e["id"]]
        log(f"[rejudge {idx}/{len(todo)}] {key}")
        new = ev.judge_answer(judge_model, item["q"], ctx, e["answer"], item.get("key_facts", []))
        e.setdefault("judge_pre_ctxfix", e.get("judge"))
        e["judge"], e["judge_num_ctx"] = new, num_ctx
        save()
    done = len(todo)
    blank = sum(1 for e in entries if is_blank(e))
    already = sum(1 for e in entries if not is_blank(e) and e.get("judge_num_ctx") == num_ctx) - done
    return done, blank, already


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--judge-model", default="llama3.1:latest")
    ap.add_argument("--judge-num-ctx", type=int, default=16384)
    ap.add_argument("--contexts-from", default=os.path.join(HERE, "..", "results", "retrieval_contexts_snapshot.json"))
    args = ap.parse_args()

    src = args.output if os.path.exists(args.output) else args.input
    if src == args.output:
        print(f"Continuing existing output {args.output}")
    data = json.load(open(src, encoding="utf-8"))
    ds = json.load(open(ev.DATASET_PATH, encoding="utf-8"))
    items = {i["id"]: i for i in ds["core"] + ds["out_of_scope"]}
    snap = json.load(open(args.contexts_from, encoding="utf-8"))["entries"]

    def save():
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    done, blank, already = rejudge(data, items, snap, args.judge_model, args.judge_num_ctx, save=save)
    data["rejudge"] = {"judge_model": args.judge_model, "judge_num_ctx": args.judge_num_ctx,
                       "reason": "judge prompts longer than the default 4096 window were silently truncated by Ollama"}
    save()

    # what changed
    E = [e for e in data["core_and_out_of_scope"] if not is_blank(e) and e.get("judge_pre_ctxfix") is not None]
    big = [e for e in E if (e["judge"].get("_judge_prompt_eval_count") or 0) > 4096]
    both = [(composite(e["judge_pre_ctxfix"]), composite(e["judge"]), e) for e in E]
    both = [(o, n, e) for o, n, e in both if o is not None and n is not None]
    print(f"\nre-judged now: {done} | already at this window: {already} | blank/hard-failure kept: {blank}")
    print(f"judge prompts that exceeded the old 4096 window (i.e. WERE truncated): {len(big)}/{len(E)}")
    if both:
        print(f"composite changed for {sum(1 for o, n, _ in both if abs(o - n) > 1e-9)}/{len(both)} entries | "
              f"mean old {statistics.mean(o for o, _, _ in both):.3f} -> new {statistics.mean(n for _, n, _ in both):.3f}")
        tr = [(o, n) for o, n, e in both if (e['judge'].get('_judge_prompt_eval_count') or 0) > 4096]
        if tr:
            print(f"  among the truncated-judge entries: mean old {statistics.mean(o for o, _ in tr):.3f} -> new {statistics.mean(n for _, n in tr):.3f}")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
