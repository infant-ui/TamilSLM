# Deprecated Evaluation Pipeline

These files are NOT a valid LLM-as-judge evaluation and must not be cited.

## Files

- `judge_scorer.py`
- `judge_scores.json`
- `human_scores.json`
- `analyze_agreement.py`

## Why these are invalid

`judge_scorer.py` contains `mock_llm_judge()`, a regex function that returns
score=3 if any unbracketed English word is found in the answer, score=5
otherwise. It never calls an LLM.

`human_scores.json` is identical to `judge_scores.json` on all 10 items —
the human scores are not independent of the mock judge output, so any
agreement metric computed from this pair (e.g. Cohen's Kappa = 1.000) is
guaranteed by construction and measures nothing.

Any prior document or note citing a kappa value or "judge score" from this
pipeline (including a previously-referenced ~0.699 figure, which does not
reproduce from this pipeline or any other file on disk) should be treated
as unverified until replaced by the output of the real pipelines below.

## Use instead

Use `run_actual_llm_judge.py` / `run_actual_llm_judge_large.py` +
`analyze_messy.py` / `analyze_large.py` instead. See `/eval_results/` for
the current recorded kappa values.
