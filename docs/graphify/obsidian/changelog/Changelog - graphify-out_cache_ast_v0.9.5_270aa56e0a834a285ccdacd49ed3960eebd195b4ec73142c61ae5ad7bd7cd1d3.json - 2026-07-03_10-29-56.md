# Changelog: graphify-out/cache/ast/v0.9.5/270aa56e0a834a285ccdacd49ed3960eebd195b4ec73142c61ae5ad7bd7cd1d3.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/270aa56e0a834a285ccdacd49ed3960eebd195b4ec73142c61ae5ad7bd7cd1d3.json b/graphify-out/cache/ast/v0.9.5/270aa56e0a834a285ccdacd49ed3960eebd195b4ec73142c61ae5ad7bd7cd1d3.json
new file mode 100644
index 0000000..de8db85
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/270aa56e0a834a285ccdacd49ed3960eebd195b4ec73142c61ae5ad7bd7cd1d3.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_luau", "label": "sample.luau", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.luau", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_server_new", "label": "Server.new()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.luau", "source_location": "L13", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_server_start", "label": "Server:start()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.luau", "source_location": "L20", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_server_stop", "label": "Server:stop()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.luau", "source_location": "L24", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_main", "label": "main()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.luau", "source_location": "L28", "_callable": true}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_luau", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_server_new", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.luau", "source_location": "L13", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_luau", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_server_start", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.luau", "source_location": "L20", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_luau", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_server_stop", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.luau", "source_location": "L24", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_luau", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_main", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.luau", "source_location": "L28", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_main", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_server_new", "relation": "calls", "context": "call", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.luau", "source_location": "L29", "weight": 1.0}], "raw_calls": [{"caller_nid": "d_project_assistan_graphify_repo_tests_fixtures_sample_server_new", "callee": "setmetatable", "is_member_call": false, "source_file": "D:\\Project Assistan\\graphify-repo\\tests\\fixtures\\sample.luau", "source_location": "L14", "receiver": null}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
