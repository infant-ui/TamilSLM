# Changelog: graphify-out/cache/ast/v0.9.5/a14a60db3b3aa3b334b9678e40e0deabfd2f10c065df6773d7f4f06fb2411666.json
**Date:** 2026-07-03_10-58-05
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/a14a60db3b3aa3b334b9678e40e0deabfd2f10c065df6773d7f4f06fb2411666.json b/graphify-out/cache/ast/v0.9.5/a14a60db3b3aa3b334b9678e40e0deabfd2f10c065df6773d7f4f06fb2411666.json
new file mode 100644
index 0000000..bba5cfa
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/a14a60db3b3aa3b334b9678e40e0deabfd2f10c065df6773d7f4f06fb2411666.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_crate_b_src_lib_rs", "label": "lib.rs", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/crate_b/src/lib.rs", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_crate_b_src_lib_server", "label": "Server", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/crate_b/src/lib.rs", "source_location": "L5"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_crate_b_src_lib_server_run", "label": ".run()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/crate_b/src/lib.rs", "source_location": "L8"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_crate_b_src_lib_server_start", "label": ".start()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/crate_b/src/lib.rs", "source_location": "L15"}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_crate_b_src_lib_rs", "target": "d_project_assistan_graphify_repo_tests_fixtures_crate_b_src_lib_server", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/crate_b/src/lib.rs", "source_location": "L5", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_crate_b_src_lib_server", "target": "d_project_assistan_graphify_repo_tests_fixtures_crate_b_src_lib_server_run", "relation": "method", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/crate_b/src/lib.rs", "source_location": "L8", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_crate_b_src_lib_server", "target": "d_project_assistan_graphify_repo_tests_fixtures_crate_b_src_lib_server_start", "relation": "method", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/crate_b/src/lib.rs", "source_location": "L15", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_crate_b_src_lib_server_run", "target": "d_project_assistan_graphify_repo_tests_fixtures_crate_b_src_lib_server_start", "relation": "calls", "context": "call", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/crate_b/src/lib.rs", "source_location": "L10", "weight": 1.0}], "raw_calls": []}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
