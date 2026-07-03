# Changelog: graphify-out/cache/ast/v0.9.5/7590ba3fefeb5d4bec87be21a80174c2010ee5e0b25c8bd29e9dddc77cea34bc.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/7590ba3fefeb5d4bec87be21a80174c2010ee5e0b25c8bd29e9dddc77cea34bc.json b/graphify-out/cache/ast/v0.9.5/7590ba3fefeb5d4bec87be21a80174c2010ee5e0b25c8bd29e9dddc77cea34bc.json
new file mode 100644
index 0000000..ff43f69
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/7590ba3fefeb5d4bec87be21a80174c2010ee5e0b25c8bd29e9dddc77cea34bc.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_cross_lingual_retrieval_20260625t150607z_3_001_cross_lingual_retrieval_ret_py", "label": "ret.py", "file_type": "code", "source_file": "Cross Lingual Retrieval -20260625T150607Z-3-001/Cross Lingual Retrieval/ret.py", "source_location": "L1"}, {"id": "d_project_assistan_cross_lingual_retrieval_20260625t150607z_3_001_cross_lingual_retrieval_ret_generate_tamil_answer", "label": "generate_tamil_answer()", "file_type": "code", "source_file": "Cross Lingual Retrieval -20260625T150607Z-3-001/Cross Lingual Retrieval/ret.py", "source_location": "L33", "_callable": true}, {"id": "d_project_assistan_cross_lingual_retrieval_20260625t150607z_3_001_cross_lingual_retrieval_ret_rationale_1", "label": "ret.py \u2014 Tamil LLaMA Answer Generator -------------------------------------- T", "file_type": "rationale", "source_file": "Cross Lingual Retrieval -20260625T150607Z-3-001/Cross Lingual Retrieval/ret.py", "source_location": "L1"}, {"id": "d_project_assistan_cross_lingual_retrieval_20260625t150607z_3_001_cross_lingual_retrieval_ret_rationale_34", "label": "Generate a Tamil answer from retrieved RAG content.      Args:         retrie", "file_type": "rationale", "source_file": "Cross Lingual Retrieval -20260625T150607Z-3-001/Cross Lingual Retrieval/ret.py", "source_location": "L34"}], "edges": [{"source": "d_project_assistan_cross_lingual_retrieval_20260625t150607z_3_001_cross_lingual_retrieval_ret_py", "target": "sys", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "Cross Lingual Retrieval -20260625T150607Z-3-001/Cross Lingual Retrieval/ret.py", "source_location": "L23", "weight": 1.0}, {"source": "d_project_assistan_cross_lingual_retrieval_20260625t150607z_3_001_cross_lingual_retrieval_ret_py", "target": "ollama", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "Cross Lingual Retrieval -20260625T150607Z-3-001/Cross Lingual Retrieval/ret.py", "source_location": "L26", "weight": 1.0}, {"source": "d_project_assistan_cross_lingual_retrieval_20260625t150607z_3_001_cross_lingual_retrieval_ret_py", "target": "d_project_assistan_cross_lingual_retrieval_20260625t150607z_3_001_cross_lingual_retrieval_ret_generate_tamil_answer", "relation": "contains", "confidence": "EXTRACTED", "source_file": "Cross Lingual Retrieval -20260625T150607Z-3-001/Cross Lingual Retrieval/ret.py", "source_location": "L33", "weight": 1.0}, {"source": "d_project_assistan_cross_lingual_retrieval_20260625t150607z_3_001_cross_lingual_retrieval_ret_rationale_1", "target": "d_project_assistan_cross_lingual_retrieval_20260625t150607z_3_001_cross_lingual_retrieval_ret_py", "relation": "rationale_for", "confidence": "EXTRACTED", "source_file": "Cross Lingual Retrieval -20260625T150607Z-3-001/Cross Lingual Retrieval/ret.py", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_cross_lingual_retrieval_20260625t150607z_3_001_cross_lingual_retrieval_ret_rationale_34", "target": "d_project_assistan_cross_lingual_retrieval_20260625t150607z_3_001_cross_lingual_retrieval_ret_generate_tamil_answer", "relation": "rationale_for", "confidence": "EXTRACTED", "source_file": "Cross Lingual Retrieval -20260625T150607Z-3-001/Cross Lingual Retrieval/ret.py", "source_location": "L34", "weight": 1.0}], "raw_calls": [{"caller_nid": "d_project_assistan_cross_lingual_retrieval_20260625t150607z_3_001_cross_lingual_retrieval_ret_generate_tamil_answer", "callee": "chat", "is_member_call": true, "source_file": "D:\\Project Assistan\\Cross Lingual Retrieval -20260625T150607Z-3-001\\Cross Lingual Retrieval\\ret.py", "source_location": "L61", "receiver": "ollama"}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
