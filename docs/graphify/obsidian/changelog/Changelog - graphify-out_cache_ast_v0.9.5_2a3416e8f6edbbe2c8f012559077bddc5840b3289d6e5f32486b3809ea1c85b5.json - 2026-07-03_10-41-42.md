# Changelog: graphify-out/cache/ast/v0.9.5/2a3416e8f6edbbe2c8f012559077bddc5840b3289d6e5f32486b3809ea1c85b5.json
**Date:** 2026-07-03_10-41-42
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/2a3416e8f6edbbe2c8f012559077bddc5840b3289d6e5f32486b3809ea1c85b5.json b/graphify-out/cache/ast/v0.9.5/2a3416e8f6edbbe2c8f012559077bddc5840b3289d6e5f32486b3809ea1c85b5.json
new file mode 100644
index 0000000..0825588
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/2a3416e8f6edbbe2c8f012559077bddc5840b3289d6e5f32486b3809ea1c85b5.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_mock_human_scorer_py", "label": "mock_human_scorer.py", "file_type": "code", "source_file": "mock_human_scorer.py", "source_location": "L1"}, {"id": "d_project_assistan_mock_human_scorer_generate_mock_human_scores", "label": "generate_mock_human_scores()", "file_type": "code", "source_file": "mock_human_scorer.py", "source_location": "L3", "_callable": true}], "edges": [{"source": "d_project_assistan_mock_human_scorer_py", "target": "json", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "mock_human_scorer.py", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_mock_human_scorer_py", "target": "d_project_assistan_mock_human_scorer_generate_mock_human_scores", "relation": "contains", "confidence": "EXTRACTED", "source_file": "mock_human_scorer.py", "source_location": "L3", "weight": 1.0}], "raw_calls": [{"caller_nid": "d_project_assistan_mock_human_scorer_generate_mock_human_scores", "callee": "dump", "is_member_call": true, "source_file": "D:\\Project Assistan\\mock_human_scorer.py", "source_location": "L19", "receiver": "json"}, {"caller_nid": "d_project_assistan_mock_human_scorer_generate_mock_human_scores", "callee": "f", "is_member_call": false, "indirect": true, "context": "argument", "source_file": "D:\\Project Assistan\\mock_human_scorer.py", "source_location": "L19"}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
