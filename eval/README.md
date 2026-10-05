# Evaluation

LLM-as-judge vs. human scoring for the bilingual answer-quality rubric.

- Scripts and their input/score JSONs live together in this folder and use relative paths: **run them from `eval/`** (e.g. `cd eval && python run_actual_llm_judge_large.py && python analyze_large.py`).
- `results/` has the recorded Cohen's kappa values (cite these).
- `deprecated/` is an invalid mock-judge pipeline; do not cite it.
