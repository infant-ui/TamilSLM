# Changelog: graphify-out/cache/ast/v0.9.5/4efda6646834060eda81b19c161f8edc156a119831ba301ce9b62ff411485947.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/4efda6646834060eda81b19c161f8edc156a119831ba301ce9b62ff411485947.json b/graphify-out/cache/ast/v0.9.5/4efda6646834060eda81b19c161f8edc156a119831ba301ce9b62ff411485947.json
new file mode 100644
index 0000000..0d373a2
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/4efda6646834060eda81b19c161f8edc156a119831ba301ce9b62ff411485947.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_swift_cross_file_foo_swift", "label": "Foo.swift", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/swift_cross_file/Foo.swift", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_swift_cross_file_foo_foo", "label": "Foo", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/swift_cross_file/Foo.swift", "source_location": "L1", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_swift_cross_file_foo_foo_one", "label": ".one()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/swift_cross_file/Foo.swift", "source_location": "L2", "_callable": true}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_swift_cross_file_foo_swift", "target": "d_project_assistan_graphify_repo_tests_fixtures_swift_cross_file_foo_foo", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/swift_cross_file/Foo.swift", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_swift_cross_file_foo_foo", "target": "d_project_assistan_graphify_repo_tests_fixtures_swift_cross_file_foo_foo_one", "relation": "method", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/swift_cross_file/Foo.swift", "source_location": "L2", "weight": 1.0}], "raw_calls": []}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
