# services/retrieval-service/app/evaluation/metrics.py
import math
from typing import List, Dict, Any

def calculate_recall_at_k(retrieved_pages: List[int], expected_pages: List[int], k: int) -> float:
    """
    Recall@k: 1 if any expected page is found in the top-k retrieved pages, else 0.
    """
    top_k_retrieved = retrieved_pages[:k]
    for exp_page in expected_pages:
        if exp_page in top_k_retrieved:
            return 1.0
    return 0.0

def calculate_precision_at_k(retrieved_pages: List[int], expected_pages: List[int], k: int) -> float:
    """
    Precision@k: Number of relevant retrieved pages in top-k divided by k.
    """
    top_k_retrieved = retrieved_pages[:k]
    matches = sum(1 for p in top_k_retrieved if p in expected_pages)
    return matches / k if k > 0 else 0.0

def calculate_mrr(retrieved_pages: List[int], expected_pages: List[int]) -> float:
    """
    Mean Reciprocal Rank (MRR): Reciprocal of the rank of the first correct page retrieved.
    """
    for idx, page in enumerate(retrieved_pages):
        if page in expected_pages:
            return 1.0 / (idx + 1)
    return 0.0

def calculate_ndcg_at_k(retrieved_pages: List[int], expected_pages: List[int], k: int) -> float:
    """
    Normalized Discounted Cumulative Gain (nDCG@k) with binary relevance.
    """
    top_k_retrieved = retrieved_pages[:k]
    
    dcg = 0.0
    for idx, page in enumerate(top_k_retrieved):
        if page in expected_pages:
            dcg += 1.0 / math.log2(idx + 2)
            
    # Calculate Ideal DCG (IDCG) - assume all expected pages could be ranked at top
    idcg = 0.0
    ideal_count = min(len(expected_pages), k)
    for idx in range(ideal_count):
        idcg += 1.0 / math.log2(idx + 2)
        
    if idcg == 0.0:
        return 0.0
        
    return dcg / idcg
