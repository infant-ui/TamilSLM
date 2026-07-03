# Changelog: graphify-out/cache/ast/v0.9.5/00c12fb6d3434ea3d300836aab59a9ba04c5e03e7095ee7789a49640273202f7.json
**Date:** 2026-07-03_10-58-05
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/00c12fb6d3434ea3d300836aab59a9ba04c5e03e7095ee7789a49640273202f7.json b/graphify-out/cache/ast/v0.9.5/00c12fb6d3434ea3d300836aab59a9ba04c5e03e7095ee7789a49640273202f7.json
new file mode 100644
index 0000000..fc5dd31
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/00c12fb6d3434ea3d300836aab59a9ba04c5e03e7095ee7789a49640273202f7.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_foo_h", "label": "Foo.h", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/cpp_paired/Foo.h", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_foo_foo", "label": "Foo", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/cpp_paired/Foo.h", "source_location": "L4", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_foo_foo_bar", "label": "bar", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/cpp_paired/Foo.h", "source_location": "L6"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_foo_foo_value", "label": "value", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/cpp_paired/Foo.h", "source_location": "L7"}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_foo_h", "target": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_foo_foo", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/cpp_paired/Foo.h", "source_location": "L4", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_foo_foo", "target": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_foo_foo_bar", "relation": "defines", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/cpp_paired/Foo.h", "source_location": "L6", "weight": 1.0, "context": "field"}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_foo_foo", "target": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_foo_foo_value", "relation": "defines", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/cpp_paired/Foo.h", "source_location": "L7", "weight": 1.0, "context": "field"}], "raw_calls": []}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
