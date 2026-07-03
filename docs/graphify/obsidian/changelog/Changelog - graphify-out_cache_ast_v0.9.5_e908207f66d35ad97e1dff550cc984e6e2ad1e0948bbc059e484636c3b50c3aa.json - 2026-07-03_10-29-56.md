# Changelog: graphify-out/cache/ast/v0.9.5/e908207f66d35ad97e1dff550cc984e6e2ad1e0948bbc059e484636c3b50c3aa.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/e908207f66d35ad97e1dff550cc984e6e2ad1e0948bbc059e484636c3b50c3aa.json b/graphify-out/cache/ast/v0.9.5/e908207f66d35ad97e1dff550cc984e6e2ad1e0948bbc059e484636c3b50c3aa.json
new file mode 100644
index 0000000..73672b1
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/e908207f66d35ad97e1dff550cc984e6e2ad1e0948bbc059e484636c3b50c3aa.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_cpp_logger_a_logger_h", "label": "Logger.h", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/cpp_logger/a/Logger.h", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_cpp_logger_a_logger_logger", "label": "Logger", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/cpp_logger/a/Logger.h", "source_location": "L1", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_cpp_logger_a_logger_logger_log", "label": "log", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/cpp_logger/a/Logger.h", "source_location": "L3"}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_cpp_logger_a_logger_h", "target": "d_project_assistan_graphify_repo_tests_fixtures_cpp_logger_a_logger_logger", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/cpp_logger/a/Logger.h", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_cpp_logger_a_logger_logger", "target": "d_project_assistan_graphify_repo_tests_fixtures_cpp_logger_a_logger_logger_log", "relation": "defines", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/cpp_logger/a/Logger.h", "source_location": "L3", "weight": 1.0, "context": "field"}], "raw_calls": []}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
