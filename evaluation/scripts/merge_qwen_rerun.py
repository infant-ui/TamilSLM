# evaluation/scripts/merge_qwen_rerun.py
"""
Fold a targeted rerun (evaluate_generation.py --only-keys ... --output <rerun.json>) back into the full
results file, replacing exactly the rerun item/toggles and nothing else.

Safety: the original file is copied to evaluation/results/archive/ first; every replaced entry keeps its
previous answer/judgement under "pre_fix"; the merge refuses to proceed unless (a) the rerun is complete,
(b) every replaced entry recorded prompt_eval_count and none is flagged truncation_suspected, and
(c) the merged file still holds exactly one entry per original item/toggle.

USAGE:
    python evaluation/scripts/merge_qwen_rerun.py --rerun evaluation/results/qwen_rerun_ctx12000.json \\
        --breakdown evaluation/results/qwen_rerun_keys_breakdown.json
"""
import argparse
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "results")


def merge(orig, rerun, breakdown=None):
    keys = lambda es: [f"{e['id']}|{e['toggle_medium']}" for e in es]
    new = {f"{e['id']}|{e['toggle_medium']}": e for e in rerun["core_and_out_of_scope"]}
    problems = []
    if rerun.get("status") != "complete":
        problems.append(f"rerun status is {rerun.get('status')!r}, not complete")
    if rerun.get("failures"):
        problems.append(f"rerun has {len(rerun['failures'])} recorded failures: {rerun['failures'][:3]}")
    for k, e in new.items():
        if e.get("prompt_eval_count") is None:
            problems.append(f"{k}: prompt_eval_count was not recorded")
        if e.get("truncation_suspected"):
            problems.append(f"{k}: still flagged truncation_suspected ({e.get('truncation_reason')})")
    orig_keys = keys(orig["core_and_out_of_scope"])
    missing = [k for k in new if k not in orig_keys]
    if missing:
        problems.append(f"rerun keys not in the original file: {missing[:5]}")
    if problems:
        return None, problems
    reason = {}
    for why, ks in (breakdown or {}).items():
        for k in ks:
            reason[k] = why
    merged = dict(orig)
    out = []
    for e in orig["core_and_out_of_scope"]:
        k = f"{e['id']}|{e['toggle_medium']}"
        if k in new:
            ne = dict(new[k])
            if rerun.get("judge_num_ctx") and (ne.get("answer") or "").strip():
                ne["judge_num_ctx"] = rerun["judge_num_ctx"]   # already judged with the large window
            ne["rerun_reason"] = reason.get(k, "rerun")
            ne["pre_fix"] = {"answer": e.get("answer"), "judge": e.get("judge"), "n_chunks_retrieved": e.get("n_chunks_retrieved")}
            out.append(ne)
        else:
            out.append(e)
    merged["core_and_out_of_scope"] = out
    merged["ctxfix_rerun"] = {"n_replaced": len(new), "num_ctx": next(iter(new.values())).get("num_ctx"),
                              "tokenizer_guard": rerun.get("tokenizer"), "breakdown_counts": {w: len(v) for w, v in (breakdown or {}).items()}}
    if len(keys(out)) != len(set(keys(out))) or len(out) != len(orig["core_and_out_of_scope"]):
        return None, ["merged file lost or duplicated entries"]
    return merged, []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rerun", required=True)
    ap.add_argument("--original", default=os.path.join(RESULTS, "generation_results.json"))
    ap.add_argument("--breakdown", default=None)
    ap.add_argument("--archive-name", default="generation_results_qwen_pre_ctxfix.json")
    args = ap.parse_args()
    orig = json.load(open(args.original, encoding="utf-8"))
    rerun = json.load(open(args.rerun, encoding="utf-8"))
    bd = json.load(open(args.breakdown, encoding="utf-8")) if args.breakdown else None
    merged, problems = merge(orig, rerun, bd)
    if problems:
        print("REFUSING to merge:"); [print("  -", p) for p in problems]; sys.exit(1)
    os.makedirs(os.path.join(RESULTS, "archive"), exist_ok=True)
    arch = os.path.join(RESULTS, "archive", args.archive_name)
    if not os.path.exists(arch):
        shutil.copy2(args.original, arch)
        print("archived original ->", arch)
    with open(args.original, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"merged: replaced {merged['ctxfix_rerun']['n_replaced']} entries in {args.original}; total entries {len(merged['core_and_out_of_scope'])}")


if __name__ == "__main__":
    main()
