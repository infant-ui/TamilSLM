# Changelog: graphify-out/cache/ast/v0.9.5/c39411625cc0b38fce3f62a919b96bcee0268381d84104c85225f47460f28bc8.json
**Date:** 2026-07-03_10-58-05
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/c39411625cc0b38fce3f62a919b96bcee0268381d84104c85225f47460f28bc8.json b/graphify-out/cache/ast/v0.9.5/c39411625cc0b38fce3f62a919b96bcee0268381d84104c85225f47460f28bc8.json
new file mode 100644
index 0000000..9ee9a16
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/c39411625cc0b38fce3f62a919b96bcee0268381d84104c85225f47460f28bc8.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_run_actual_llm_judge_fixed_py", "label": "run_actual_llm_judge_fixed.py", "file_type": "code", "source_file": "run_actual_llm_judge_fixed.py", "source_location": "L1"}, {"id": "d_project_assistan_run_actual_llm_judge_fixed_normalize_brackets", "label": "normalize_brackets()", "file_type": "code", "source_file": "run_actual_llm_judge_fixed.py", "source_location": "L7", "_callable": true}], "edges": [{"source": "d_project_assistan_run_actual_llm_judge_fixed_py", "target": "json", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "run_actual_llm_judge_fixed.py", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_run_actual_llm_judge_fixed_py", "target": "re", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "run_actual_llm_judge_fixed.py", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_run_actual_llm_judge_fixed_py", "target": "requests", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "run_actual_llm_judge_fixed.py", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_run_actual_llm_judge_fixed_py", "target": "d_project_assistan_run_actual_llm_judge_fixed_normalize_brackets", "relation": "contains", "confidence": "EXTRACTED", "source_file": "run_actual_llm_judge_fixed.py", "source_location": "L7", "weight": 1.0}], "raw_calls": [{"caller_nid": "d_project_assistan_run_actual_llm_judge_fixed_normalize_brackets", "callee": "sub", "is_member_call": true, "source_file": "D:\\Project Assistan\\run_actual_llm_judge_fixed.py", "source_location": "L9", "receiver": "re"}, {"caller_nid": "d_project_assistan_run_actual_llm_judge_fixed_normalize_brackets", "callee": "sub", "is_member_call": true, "source_file": "D:\\Project Assistan\\run_actual_llm_judge_fixed.py", "source_location": "L11", "receiver": "re"}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
