# Changelog: graphify-out/cache/ast/v0.9.5/4a2f5002c526c8eb75c05d76955a36d7a67d4f6eb213ab41e41dcba12820eb13.json
**Date:** 2026-07-03_10-58-05
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/4a2f5002c526c8eb75c05d76955a36d7a67d4f6eb213ab41e41dcba12820eb13.json b/graphify-out/cache/ast/v0.9.5/4a2f5002c526c8eb75c05d76955a36d7a67d4f6eb213ab41e41dcba12820eb13.json
new file mode 100644
index 0000000..ec10606
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/4a2f5002c526c8eb75c05d76955a36d7a67d4f6eb213ab41e41dcba12820eb13.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_foo_cpp", "label": "Foo.cpp", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/cpp_paired/Foo.cpp", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_foo_foo_bar", "label": "Foo::bar()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/cpp_paired/Foo.cpp", "source_location": "L3", "_callable": true}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_foo_cpp", "target": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_foo_h", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/cpp_paired/Foo.cpp", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_foo_cpp", "target": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_foo_foo_bar", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/cpp_paired/Foo.cpp", "source_location": "L3", "weight": 1.0}], "raw_calls": []}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
