# Changelog: graphify-out/cache/ast/v0.9.5/158f1d188213061f80fef45bab98088b3f2c3d41f356ac701a036aee177ccccb.json
**Date:** 2026-07-03_10-41-42
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/158f1d188213061f80fef45bab98088b3f2c3d41f356ac701a036aee177ccccb.json b/graphify-out/cache/ast/v0.9.5/158f1d188213061f80fef45bab98088b3f2c3d41f356ac701a036aee177ccccb.json
new file mode 100644
index 0000000..4b1e94a
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/158f1d188213061f80fef45bab98088b3f2c3d41f356ac701a036aee177ccccb.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_run_actual_llm_judge_large_py", "label": "run_actual_llm_judge_large.py", "file_type": "code", "source_file": "run_actual_llm_judge_large.py", "source_location": "L1"}, {"id": "d_project_assistan_run_actual_llm_judge_large_normalize_brackets", "label": "normalize_brackets()", "file_type": "code", "source_file": "run_actual_llm_judge_large.py", "source_location": "L6", "_callable": true}], "edges": [{"source": "d_project_assistan_run_actual_llm_judge_large_py", "target": "json", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "run_actual_llm_judge_large.py", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_run_actual_llm_judge_large_py", "target": "re", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "run_actual_llm_judge_large.py", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_run_actual_llm_judge_large_py", "target": "requests", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "run_actual_llm_judge_large.py", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_run_actual_llm_judge_large_py", "target": "d_project_assistan_run_actual_llm_judge_large_normalize_brackets", "relation": "contains", "confidence": "EXTRACTED", "source_file": "run_actual_llm_judge_large.py", "source_location": "L6", "weight": 1.0}], "raw_calls": [{"caller_nid": "d_project_assistan_run_actual_llm_judge_large_normalize_brackets", "callee": "sub", "is_member_call": true, "source_file": "D:\\Project Assistan\\run_actual_llm_judge_large.py", "source_location": "L7", "receiver": "re"}, {"caller_nid": "d_project_assistan_run_actual_llm_judge_large_normalize_brackets", "callee": "sub", "is_member_call": true, "source_file": "D:\\Project Assistan\\run_actual_llm_judge_large.py", "source_location": "L8", "receiver": "re"}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
