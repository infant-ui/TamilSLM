# Changelog: graphify-out/cache/ast/v0.9.5/53a434521d0520796e54266c9f7399949ae10f270a978897eb840834e6ca8cf0.json
**Date:** 2026-07-03_10-58-05
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/53a434521d0520796e54266c9f7399949ae10f270a978897eb840834e6ca8cf0.json b/graphify-out/cache/ast/v0.9.5/53a434521d0520796e54266c9f7399949ae10f270a978897eb840834e6ca8cf0.json
new file mode 100644
index 0000000..1e7d26c
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/53a434521d0520796e54266c9f7399949ae10f270a978897eb840834e6ca8cf0.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_py", "label": "sample.py", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.py", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_transformer", "label": "Transformer", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.py", "source_location": "L1", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_transformer_init", "label": ".__init__()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.py", "source_location": "L2", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_transformer_forward", "label": ".forward()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.py", "source_location": "L5", "_callable": true}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_py", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_transformer", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.py", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_transformer", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_transformer_init", "relation": "method", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.py", "source_location": "L2", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_transformer", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_transformer_forward", "relation": "method", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.py", "source_location": "L5", "weight": 1.0}], "raw_calls": []}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
