# Changelog: graphify-out/cache/ast/v0.9.5/3c20c79943e4761aca08d1b7da91a1eef3384b46b78c3188f74aa986d252e1ba.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/3c20c79943e4761aca08d1b7da91a1eef3384b46b78c3188f74aa986d252e1ba.json b/graphify-out/cache/ast/v0.9.5/3c20c79943e4761aca08d1b7da91a1eef3384b46b78c3188f74aa986d252e1ba.json
new file mode 100644
index 0000000..679f74f
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/3c20c79943e4761aca08d1b7da91a1eef3384b46b78c3188f74aa986d252e1ba.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_m", "label": "Widget.m", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/objc_mixed/Widget.m", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_widget", "label": "Widget", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/objc_mixed/Widget.m", "source_location": "L3"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_widget_render", "label": "-render", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/objc_mixed/Widget.m", "source_location": "L4"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_widget_refresh", "label": "-refresh", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/objc_mixed/Widget.m", "source_location": "L7"}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_m", "target": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_h", "relation": "imports", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/objc_mixed/Widget.m", "source_location": "L1", "weight": 1.0, "context": "import"}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_m", "target": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_widget", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/objc_mixed/Widget.m", "source_location": "L3", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_widget", "target": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_widget_render", "relation": "method", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/objc_mixed/Widget.m", "source_location": "L4", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_widget", "target": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_widget_refresh", "relation": "method", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/objc_mixed/Widget.m", "source_location": "L7", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_widget_render", "target": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_widget_refresh", "relation": "calls", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/objc_mixed/Widget.m", "source_location": "L5", "weight": 1.0, "context": "call"}], "raw_calls": [{"caller_nid": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widget_widget_render", "callee": "refresh", "is_member_call": true, "source_file": "D:\\Project Assistan\\graphify-repo\\tests\\fixtures\\objc_mixed\\Widget.m", "source_location": "L5", "receiver": "self", "lang": "objc"}], "input_tokens": 0, "output_tokens": 0}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
