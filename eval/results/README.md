# Judge Pipeline Evaluation Results

Last computed: 2026-07-14

## Messy set (10 items, IDs 101-110)
Judge: llama3.1:latest via run_actual_llm_judge.py
Human: independently authored, messy_human_scores.json
Cohen's Kappa (quadratic weighted): 0.610

**Interpretation**: 
The disagreement pattern is highly systematic. In almost every disagreement, the LLM scored the response 1 to 2 points strictly lower than the human rater (e.g., Human 4 vs LLM 2, Human 5 vs LLM 4, Human 3 vs LLM 2). The LLM is penalizing partial English usage much more harshly than the human rater. Because this is systematic, it is likely fixable via a prompt/rubric adjustment to calibrate the LLM's strictness to match the human expectations.

## Large set (30 items, IDs 101-130)
Judge: llama3.1:latest via run_actual_llm_judge_large.py
Human: independently authored, large_human_scores.json
Cohen's Kappa (quadratic weighted): 0.699

**Interpretation**: 
The disagreement pattern here is slightly more bidirectional (e.g., LLM was more lenient on items 110 and 114 scoring 4 vs Human 2, while being stricter on items 106 and 109). However, achieving a kappa of 0.699 demonstrates a solid baseline of agreement. The mixed nature of the major disagreements suggests that the rubric itself may need slight tightening to clarify edge cases where human intuition diverges in both directions.

---
These are the only two evaluation pipelines in this project with verified independent judge and human scores. Cite these values, not any figure from the deprecated/ pipeline.
