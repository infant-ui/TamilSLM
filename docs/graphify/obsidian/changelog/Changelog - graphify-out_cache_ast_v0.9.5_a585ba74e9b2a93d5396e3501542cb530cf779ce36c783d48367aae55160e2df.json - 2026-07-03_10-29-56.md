# Changelog: graphify-out/cache/ast/v0.9.5/a585ba74e9b2a93d5396e3501542cb530cf779ce36c783d48367aae55160e2df.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/a585ba74e9b2a93d5396e3501542cb530cf779ce36c783d48367aae55160e2df.json b/graphify-out/cache/ast/v0.9.5/a585ba74e9b2a93d5396e3501542cb530cf779ce36c783d48367aae55160e2df.json
new file mode 100644
index 0000000..aa4976e
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/a585ba74e9b2a93d5396e3501542cb530cf779ce36c783d48367aae55160e2df.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_swift_cross_file_foo_ext_swift", "label": "Foo+Ext.swift", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/swift_cross_file/Foo+Ext.swift", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_swift_cross_file_foo_ext_foo", "label": "Foo", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/swift_cross_file/Foo+Ext.swift", "source_location": "L1", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_swift_cross_file_foo_ext_foo_two", "label": ".two()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/swift_cross_file/Foo+Ext.swift", "source_location": "L2", "_callable": true}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_swift_cross_file_foo_ext_swift", "target": "d_project_assistan_graphify_repo_tests_fixtures_swift_cross_file_foo_ext_foo", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/swift_cross_file/Foo+Ext.swift", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_swift_cross_file_foo_ext_foo", "target": "d_project_assistan_graphify_repo_tests_fixtures_swift_cross_file_foo_ext_foo_two", "relation": "method", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/swift_cross_file/Foo+Ext.swift", "source_location": "L2", "weight": 1.0}], "raw_calls": [], "swift_extensions": [{"nid": "d_project_assistan_graphify_repo_tests_fixtures_swift_cross_file_foo_ext_foo", "label": "Foo"}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
