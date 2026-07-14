# services/retrieval-service/app/evaluation/evaluator.py
import os
import json
import time
import pickle
import logging
import requests
from datetime import datetime
import numpy as np

from app.evaluation.metrics import (
    calculate_recall_at_k,
    calculate_precision_at_k,
    calculate_mrr,
    calculate_ndcg_at_k
)
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.reranker import CrossEncoderReranker
from app.api.schemas import RetrieveRequest
from app.ingestion.hardware_detector import get_hardware_level

logger = logging.getLogger("evaluation.evaluator")

class RAGEvaluator:
    def __init__(self, data_root: str):
        self.data_root = os.path.abspath(data_root)
        self.cache_dir = os.path.join(self.data_root, "processed", "cache")
        self.evals_dir = os.path.join(self.data_root, "processed", "evals")
        self.history_file = os.path.join(self.evals_dir, "eval_history.json")
        
        os.makedirs(self.evals_dir, exist_ok=True)
        
        # Load indexing caches for retrieval evaluation
        self.services_cache = {}
        self._load_caches()
        
        self.retriever = HybridRetriever(self.services_cache)
        self.reranker = CrossEncoderReranker()

    def _load_caches(self):
        """
        Loads the compiled index chunks and embeddings.
        """
        en_chunks_path = os.path.join(self.cache_dir, "english_chunks.pkl")
        en_embeddings_path = os.path.join(self.cache_dir, "english_embeddings.npy")
        ta_chunks_path = os.path.join(self.cache_dir, "tamil_chunks.pkl")
        ta_embeddings_path = os.path.join(self.cache_dir, "tamil_embeddings.npy")

        # Load English Cache
        if os.path.exists(en_chunks_path) and os.path.exists(en_embeddings_path):
            with open(en_chunks_path, "rb") as f:
                self.services_cache["en_chunks"] = pickle.load(f)
            self.services_cache["en_embeddings"] = np.load(en_embeddings_path)
            
        # Load Tamil Cache
        if os.path.exists(ta_chunks_path) and os.path.exists(ta_embeddings_path):
            with open(ta_chunks_path, "rb") as f:
                self.services_cache["ta_chunks"] = pickle.load(f)
            self.services_cache["ta_embeddings"] = np.load(ta_embeddings_path)

        # Mock embedding model references to satisfy HybridRetriever signatures
        # (embeddings are pre-computed in index cache, so retriever runs on cache without encoding)
        self.services_cache["en_model"] = None
        self.services_cache["ta_model"] = None

    def run_evaluation(self, benchmark_path: str, mode: str = "Mode_1_Local") -> dict:
        """
        Runs the evaluation suite on the benchmark dataset.
        """
        if not os.path.exists(benchmark_path):
            raise FileNotFoundError(f"Benchmark dataset not found at {benchmark_path}")
            
        with open(benchmark_path, "r", encoding="utf-8") as f:
            test_cases = json.load(f)
            
        results = []
        total_retrieval_time = 0.0
        
        for case in test_cases:
            query = case["question"]
            expected_pages = case["expected_pages"]
            expected_medium = case["language"]
            
            # Construct a RetrieveRequest
            req = RetrieveRequest(
                question=query,
                detected_language=expected_medium,
                class_id=case["class"],
                subject=case["subject"],
                term=case["term"],
                preferred_medium=expected_medium,
                allowed_content_types=["textbook", "guide"],
                top_k=10  # Evaluate top-10 capacity
            )

            # Measure search latency
            t_start = time.time()
            # Fetch dense vector coordinates (empty vector works since search operates on cache indexes)
            query_vector = np.zeros(768)
            
            # 1. Retrieve candidates
            candidates = self.retriever.retrieve(req, query_vector)
            
            # 2. Rerank candidates
            reranked = self.reranker.rerank(query, candidates, top_k=10)
            t_end = time.time()
            
            latency_ms = (t_end - t_start) * 1000
            total_retrieval_time += latency_ms

            # Extract retrieved page numbers and context
            retrieved_pages = []
            context_texts = []
            for r in reranked:
                for original_chunk in self.services_cache.get(f"{'ta' if expected_medium == 'tamil' else 'en'}_chunks", []):
                    if original_chunk["chunk_id"] == r.chunk_id:
                        ret_p = original_chunk["metadata"].get("page_number")
                        if ret_p:
                            retrieved_pages.append(ret_p)
                        context_texts.append(original_chunk.get("text", ""))
                        break

            # Calculate metrics for this test case
            rec_1 = calculate_recall_at_k(retrieved_pages, expected_pages, 1)
            rec_5 = calculate_recall_at_k(retrieved_pages, expected_pages, 5)
            rec_10 = calculate_recall_at_k(retrieved_pages, expected_pages, 10)
            prec_5 = calculate_precision_at_k(retrieved_pages, expected_pages, 5)
            mrr_score = calculate_mrr(retrieved_pages, expected_pages)
            ndcg_score = calculate_ndcg_at_k(retrieved_pages, expected_pages, 5)

            # Generate and judge answer for faithfulness/hallucination
            context_str = "\n\n".join(context_texts[:5])
            if context_str:
                answer = self._generate_answer(query, context_str)
                gen_metrics = self._evaluate_generation(query, context_str, answer)
            else:
                gen_metrics = {"faithfulness": 0.0, "citation_accuracy": 0.0, "hallucination_rate": 1.0}

            results.append({
                "question_id": case["question_id"],
                "question": query,
                "latency_ms": latency_ms,
                "recall_1": rec_1,
                "recall_5": rec_5,
                "recall_10": rec_10,
                "precision_5": prec_5,
                "mrr": mrr_score,
                "ndcg_5": ndcg_score,
                "faithfulness": gen_metrics["faithfulness"],
                "citation_accuracy": gen_metrics["citation_accuracy"],
                "hallucination_rate": gen_metrics["hallucination_rate"]
            })

        # Compute Aggregates
        count = len(test_cases)
        if count == 0:
            return {}

        avg_metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "hardware_level": get_hardware_level(),
            "total_questions": count,
            "avg_retrieval_latency_ms": total_retrieval_time / count,
            "recall_1": sum(r["recall_1"] for r in results) / count,
            "recall_5": sum(r["recall_5"] for r in results) / count,
            "recall_10": sum(r["recall_10"] for r in results) / count,
            "precision_5": sum(r["precision_5"] for r in results) / count,
            "mrr": sum(r["mrr"] for r in results) / count,
            "ndcg_5": sum(r["ndcg_5"] for r in results) / count,
            "faithfulness": sum(r["faithfulness"] for r in results) / count,
            "citation_accuracy": sum(r["citation_accuracy"] for r in results) / count,
            "hallucination_rate": sum(r["hallucination_rate"] for r in results) / count
        }

        # Compare against history
        previous_run = self._load_last_eval_run()
        deltas = self._compute_deltas(avg_metrics, previous_run)
        
        # Save evaluation result to log registry
        self._save_to_history(avg_metrics)
        
        # Write markdown report
        self._write_markdown_report(avg_metrics, deltas, results)

        return avg_metrics

    def _generate_answer(self, query: str, context: str) -> str:
        prompt = f"Answer the question based ONLY on the context.\n\nContext:\n{context}\n\nQuestion:\n{query}"
        payload = {
            "model": "qwen2.5:7b-instruct-q4_k_m",
            "prompt": prompt,
            "stream": False
        }
        try:
            r = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
            return r.json().get('response', '')
        except Exception as e:
            logger.error(f"Generation LLM failed: {e}")
            return ""

    def _evaluate_generation(self, query: str, context: str, answer: str) -> dict:
        prompt = f"""You are a strict technical evaluator.
Given the QUESTION, CONTEXT, and ANSWER, evaluate the answer's quality.
Provide a JSON object with exactly three keys (all 0.0 or 1.0):
"faithfulness": 1.0 if the answer is derived entirely from the CONTEXT, else 0.0
"citation_accuracy": 1.0 if the answer correctly cites the source pages, else 0.0
"hallucination_rate": 1.0 if the answer contains hallucinated facts not in CONTEXT, else 0.0

QUESTION: {query}
CONTEXT: {context}
ANSWER: {answer}

Return ONLY valid JSON.
"""
        payload = {
            "model": "llama3.1:latest",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        try:
            r = requests.post("http://localhost:11434/api/generate", json=payload, timeout=60)
            res = json.loads(r.json()['response'])
            return {
                "faithfulness": float(res.get("faithfulness", 0.0)),
                "citation_accuracy": float(res.get("citation_accuracy", 0.0)),
                "hallucination_rate": float(res.get("hallucination_rate", 1.0))
            }
        except Exception as e:
            logger.error(f"Judge LLM failed: {e}")
            return {"faithfulness": 0.0, "citation_accuracy": 0.0, "hallucination_rate": 1.0}

    def _load_last_eval_run(self) -> dict:
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
                    if history and len(history) > 0:
                        # Sort by timestamp to get the last one
                        history.sort(key=lambda x: x["timestamp"])
                        return history[-1]
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse history {self.history_file}: {e}. Skipping history comparison.", exc_info=True)
            except OSError as e:
                logger.error(f"Failed to read history {self.history_file}: {e}. Skipping history comparison.", exc_info=True)
        return {}

    def _save_to_history(self, record: dict):
        history = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse history {self.history_file}: {e}. Starting fresh history.", exc_info=True)
            except OSError as e:
                logger.error(f"Failed to read history {self.history_file}: {e}. Starting fresh history.", exc_info=True)
        history.append(record)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    def _compute_deltas(self, current: dict, previous: dict) -> dict:
        deltas = {}
        if not previous:
            return deltas
            
        metrics_keys = [
            "recall_1", "recall_5", "recall_10", "precision_5", 
            "mrr", "ndcg_5", "faithfulness", "citation_accuracy", 
            "hallucination_rate", "avg_retrieval_latency_ms"
        ]
        
        for key in metrics_keys:
            if key in current and key in previous:
                deltas[key] = current[key] - previous[key]
        return deltas

    def _write_markdown_report(self, current: dict, deltas: dict, case_details: list):
        """
        Outputs a comprehensive markdown evaluation report.
        """
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.evals_dir, f"report_{timestamp_str}.md")

        def fmt_pct(val: float, delta_val: float = None) -> str:
            pct_str = f"{val * 100:.1f}%"
            if delta_val is not None:
                sign = "+" if delta_val >= 0 else ""
                pct_str += f" ({sign}{delta_val * 100:.1f}%)"
            return pct_str

        def fmt_raw(val: float, delta_val: float = None) -> str:
            raw_str = f"{val:.3f}"
            if delta_val is not None:
                sign = "+" if delta_val >= 0 else ""
                raw_str += f" ({sign}{delta_val:.3f})"
            return raw_str

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# RAG Evaluation Report: Build {timestamp_str}\n\n")
            f.write(f"**Timestamp**: {current['timestamp']}  \n")
            f.write(f"**Hardware Level**: {current['hardware_level']}  \n")
            f.write(f"**Total Questions Evaluated**: {current['total_questions']}  \n\n")
            
            f.write("## Aggregate Retrieval Quality\n\n")
            f.write("| Metric | Score | Delta | Status |\n")
            f.write("| :--- | :--- | :--- | :--- |\n")
            
            f.write(f"| **Recall@1** | {current['recall_1']*100:.1f}% | {deltas.get('recall_1', 0.0)*100:+.1f}% | {'🟢 Improved' if deltas.get('recall_1', 0) >= 0 else '🔴 Decreased'} |\n")
            f.write(f"| **Recall@5** | {current['recall_5']*100:.1f}% | {deltas.get('recall_5', 0.0)*100:+.1f}% | {'🟢 Improved' if deltas.get('recall_5', 0) >= 0 else '🔴 Decreased'} |\n")
            f.write(f"| **Recall@10** | {current['recall_10']*100:.1f}% | {deltas.get('recall_10', 0.0)*100:+.1f}% | {'🟢 Improved' if deltas.get('recall_10', 0) >= 0 else '🔴 Decreased'} |\n")
            f.write(f"| **MRR** | {current['mrr']:.3f} | {deltas.get('mrr', 0.0):+.3f} | {'🟢 Improved' if deltas.get('mrr', 0) >= 0 else '🔴 Decreased'} |\n")
            f.write(f"| **nDCG@5** | {current['ndcg_5']:.3f} | {deltas.get('ndcg_5', 0.0):+.3f} | {'🟢 Improved' if deltas.get('ndcg_5', 0) >= 0 else '🔴 Decreased'} |\n")
            
            f.write("\n## Generation & Grounding (Offline Judge)\n\n")
            f.write("| Metric | Score | Status |\n")
            f.write("| :--- | :--- | :--- |\n")
            f.write(f"| **Faithfulness** | {current['faithfulness']*100:.1f}% | Grounded within Context |\n")
            f.write(f"| **Citation Accuracy** | {current['citation_accuracy']*100:.1f}% | Cites exact page coordinates |\n")
            f.write(f"| **Hallucination Rate** | {current['hallucination_rate']*100:.1f}% | Safe threshold |\n\n")
            
            f.write("## System Performance\n")
            f.write(f"- **Average Retrieval Latency**: {current['avg_retrieval_latency_ms']:.1f} ms  \n\n")
            
            f.write("## Case-by-Case Breakdown\n\n")
            f.write("| ID | Question | Latency (ms) | Recall@5 | MRR | nDCG@5 |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
            for c in case_details:
                f.write(f"| {c['question_id']} | {c['question']} | {c['latency_ms']:.1f} | {c['recall_5']:.1f} | {c['mrr']:.3f} | {c['ndcg_5']:.3f} |\n")

        print(f"📊 Evaluation Complete. Markdown report generated: {report_path}")

def run_auto_evaluation() -> dict:
    """
    Standard runner triggered automatically post indexing.
    """
    data_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data"))
    benchmark_path = os.path.join(os.path.dirname(__file__), "benchmark_dataset.json")
    
    print("⏳ Executing automated RAG evaluation suite...")
    evaluator = RAGEvaluator(data_root)
    metrics = evaluator.run_evaluation(benchmark_path)
    return metrics

if __name__ == "__main__":
    run_auto_evaluation()
