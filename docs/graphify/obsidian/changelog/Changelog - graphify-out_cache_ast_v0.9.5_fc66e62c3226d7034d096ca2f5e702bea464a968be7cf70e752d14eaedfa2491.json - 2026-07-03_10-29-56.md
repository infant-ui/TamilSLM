# Changelog: graphify-out/cache/ast/v0.9.5/fc66e62c3226d7034d096ca2f5e702bea464a968be7cf70e752d14eaedfa2491.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/fc66e62c3226d7034d096ca2f5e702bea464a968be7cf70e752d14eaedfa2491.json b/graphify-out/cache/ast/v0.9.5/fc66e62c3226d7034d096ca2f5e702bea464a968be7cf70e752d14eaedfa2491.json
new file mode 100644
index 0000000..fbfe8e5
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/fc66e62c3226d7034d096ca2f5e702bea464a968be7cf70e752d14eaedfa2491.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widgetextras_swift", "label": "WidgetExtras.swift", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/objc_mixed/WidgetExtras.swift", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widgetextras_widget", "label": "Widget", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/objc_mixed/WidgetExtras.swift", "source_location": "L1", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widgetextras_widget_describe", "label": ".describe()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/objc_mixed/WidgetExtras.swift", "source_location": "L2", "_callable": true}, {"id": "string", "label": "String", "file_type": "code", "source_file": "", "source_location": "", "origin_file": "D:\\Project Assistan\\graphify-repo\\tests\\fixtures\\objc_mixed\\WidgetExtras.swift"}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widgetextras_swift", "target": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widgetextras_widget", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/objc_mixed/WidgetExtras.swift", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widgetextras_widget", "target": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widgetextras_widget_describe", "relation": "method", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/objc_mixed/WidgetExtras.swift", "source_location": "L2", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widgetextras_widget_describe", "target": "string", "relation": "references", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/objc_mixed/WidgetExtras.swift", "source_location": "L2", "weight": 1.0, "context": "return_type"}], "raw_calls": [], "swift_extensions": [{"nid": "d_project_assistan_graphify_repo_tests_fixtures_objc_mixed_widgetextras_widget", "label": "Widget"}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
