# Changelog: graphify-out/cache/ast/v0.9.5/abe00a561e94424441e5f39eeaa35b7278eab552d5b79536e351a2f37c77c680.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/abe00a561e94424441e5f39eeaa35b7278eab552d5b79536e351a2f37c77c680.json b/graphify-out/cache/ast/v0.9.5/abe00a561e94424441e5f39eeaa35b7278eab552d5b79536e351a2f37c77c680.json
new file mode 100644
index 0000000..8740dab
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/abe00a561e94424441e5f39eeaa35b7278eab552d5b79536e351a2f37c77c680.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_h", "label": "Widget.h", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/objc_mixed/Widget.h", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_widget", "label": "Widget", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/objc_mixed/Widget.h", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_widget_render", "label": "-render", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/objc_mixed/Widget.h", "source_location": "L2"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_widget_refresh", "label": "-refresh", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/objc_mixed/Widget.h", "source_location": "L3"}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_h", "target": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_widget", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/objc_mixed/Widget.h", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_widget", "target": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_widget_render", "relation": "method", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/objc_mixed/Widget.h", "source_location": "L2", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_widget", "target": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_widget_refresh", "relation": "method", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/objc_mixed/Widget.h", "source_location": "L3", "weight": 1.0}], "raw_calls": [], "input_tokens": 0, "output_tokens": 0}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
