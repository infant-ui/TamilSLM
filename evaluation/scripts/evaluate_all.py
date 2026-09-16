# evaluation/scripts/evaluate_all.py
"""
Orchestrator: runs whichever evaluation stages are possible in the current
environment, then combines whatever results/*.json files exist into a single
evaluation/results/final_report.json plus a printed summary table.

Always runs:
  - evaluate_retrieval_bm25.py     (numpy-only, works anywhere)
Runs only if explicitly requested (they need the full venv / a live stack):
  - evaluate_retrieval_full.py     --with-full
  - evaluate_generation.py         --with-generation

USAGE (from repo root):
    .\\.venv\\Scripts\\python.exe evaluation\\scripts\\evaluate_all.py --with-full --with-generation
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "..", "results")


def run(script_name, extra_args=None):
    cmd = [sys.executable, os.path.join(HERE, script_name)] + (extra_args or [])
    print(f"\n=== Running {script_name} ===")
    subprocess.run(cmd, check=False)


def load_if_exists(name):
    path = os.path.join(RESULTS_DIR, name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-full", action="store_true", help="Also run the dense+rerank pipeline eval")
    parser.add_argument("--with-generation", action="store_true", help="Also run the live generation+judge eval")
    parser.add_argument("--gen-limit", type=int, default=None)
    args = parser.parse_args()

    run("evaluate_retrieval_bm25.py")
    if args.with_full:
        run("evaluate_retrieval_full.py")
    if args.with_generation:
        extra = ["--limit", str(args.gen_limit)] if args.gen_limit else []
        run("evaluate_generation.py", extra)

    bm25 = load_if_exists("retrieval_bm25_results.json")
    full = load_if_exists("retrieval_full_results.json")
    gen = load_if_exists("generation_results.json")

    report = {"retrieval_bm25": bm25, "retrieval_full": full, "generation": gen}
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(RESULTS_DIR, "final_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nWrote {out_path}")

    if bm25:
        print("\n=== BM25 retrieval summary (Recall@5 by language) ===")
        for lang, entry in bm25["summary_by_language"].items():
            if "recall_5" in entry:
                print(f"  {lang:10s} recall@5={entry['recall_5']:.2f}  mrr={entry['mrr']:.2f}  n={entry['n']}")
            else:
                print(f"  {lang:10s} vs EN corpus recall@5={entry['against_en_corpus']['recall_5']:.2f} | "
                      f"vs TA corpus recall@5={entry['against_ta_corpus']['recall_5']:.2f}  n={entry['n']}")
    if not full:
        print("\n(retrieval_full_results.json not present -- run with --with-full to include dense+rerank numbers)")
    if not gen:
        print("(generation_results.json not present -- run with --with-generation to include answer-quality numbers)")


if __name__ == "__main__":
    main()
