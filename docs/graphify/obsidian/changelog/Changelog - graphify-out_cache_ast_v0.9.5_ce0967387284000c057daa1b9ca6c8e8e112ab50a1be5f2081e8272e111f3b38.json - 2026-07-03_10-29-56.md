# Changelog: graphify-out/cache/ast/v0.9.5/ce0967387284000c057daa1b9ca6c8e8e112ab50a1be5f2081e8272e111f3b38.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/ce0967387284000c057daa1b9ca6c8e8e112ab50a1be5f2081e8272e111f3b38.json b/graphify-out/cache/ast/v0.9.5/ce0967387284000c057daa1b9ca6c8e8e112ab50a1be5f2081e8272e111f3b38.json
new file mode 100644
index 0000000..00ce1b9
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/ce0967387284000c057daa1b9ca6c8e8e112ab50a1be5f2081e8272e111f3b38.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_cpp_logger_b_logger_h", "label": "Logger.h", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/cpp_logger/b/Logger.h", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_cpp_logger_b_logger_logger", "label": "Logger", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/cpp_logger/b/Logger.h", "source_location": "L1", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_cpp_logger_b_logger_logger_log", "label": "log", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/cpp_logger/b/Logger.h", "source_location": "L3"}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_cpp_logger_b_logger_h", "target": "d_project_assistan_graphify_repo_tests_fixtures_cpp_logger_b_logger_logger", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/cpp_logger/b/Logger.h", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_cpp_logger_b_logger_logger", "target": "d_project_assistan_graphify_repo_tests_fixtures_cpp_logger_b_logger_logger_log", "relation": "defines", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/cpp_logger/b/Logger.h", "source_location": "L3", "weight": 1.0, "context": "field"}], "raw_calls": []}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
