# evaluation/scripts/metrics.py
"""
Verbatim copy of backend/retrieval-service/app/evaluation/metrics.py, so this
evaluation suite has no import dependency on the production package (it is
mathematically identical -- see final report section "Retrieval Evaluation"
for the correctness check performed on these formulas before reuse).
"""
import math
from typing import List


def calculate_recall_at_k(retrieved_pages: List[int], expected_pages: List[int], k: int) -> float:
    top_k_retrieved = retrieved_pages[:k]
    for exp_page in expected_pages:
        if exp_page in top_k_retrieved:
            return 1.0
    return 0.0


def calculate_precision_at_k(retrieved_pages: List[int], expected_pages: List[int], k: int) -> float:
    top_k_retrieved = retrieved_pages[:k]
    matches = sum(1 for p in top_k_retrieved if p in expected_pages)
    return matches / k if k > 0 else 0.0


def calculate_mrr(retrieved_pages: List[int], expected_pages: List[int]) -> float:
    for idx, page in enumerate(retrieved_pages):
        if page in expected_pages:
            return 1.0 / (idx + 1)
    return 0.0


def calculate_ndcg_at_k(retrieved_pages: List[int], expected_pages: List[int], k: int) -> float:
    top_k_retrieved = retrieved_pages[:k]
    dcg = 0.0
    for idx, page in enumerate(top_k_retrieved):
        if page in expected_pages:
            dcg += 1.0 / math.log2(idx + 2)
    idcg = 0.0
    ideal_count = min(len(expected_pages), k)
    for idx in range(ideal_count):
        idcg += 1.0 / math.log2(idx + 2)
    if idcg == 0.0:
        return 0.0
    return dcg / idcg


def calculate_hit_rate(retrieved_pages: List[int], expected_pages: List[int], k: int) -> float:
    """Not present in the production metrics.py -- added here since the brief
    asks for Hit Rate specifically. Identical definition to Recall@k under a
    single gold item (both are 1.0 iff any expected page appears in top-k);
    kept separate/named for clarity in reports that expect a Hit Rate column."""
    return calculate_recall_at_k(retrieved_pages, expected_pages, k)
