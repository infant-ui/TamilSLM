# Changelog: graphify-out/cache/ast/v0.9.5/7c5841f62f302f2710d925d28da6ec9b4001a112d5866ff7784350e09458c8ba.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/7c5841f62f302f2710d925d28da6ec9b4001a112d5866ff7784350e09458c8ba.json b/graphify-out/cache/ast/v0.9.5/7c5841f62f302f2710d925d28da6ec9b4001a112d5866ff7784350e09458c8ba.json
new file mode 100644
index 0000000..dfb0e2d
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/7c5841f62f302f2710d925d28da6ec9b4001a112d5866ff7784350e09458c8ba.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_main_cpp", "label": "Main.cpp", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/cpp_paired/Main.cpp", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_main_main", "label": "main()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/cpp_paired/Main.cpp", "source_location": "L3", "_callable": true}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_main_cpp", "target": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_foo_h", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/cpp_paired/Main.cpp", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_main_cpp", "target": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_main_main", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/cpp_paired/Main.cpp", "source_location": "L3", "weight": 1.0}], "raw_calls": [{"caller_nid": "d_project_assistan_graphify_repo_tests_fixtures_cpp_paired_main_main", "callee": "bar", "is_member_call": true, "source_file": "D:\\Project Assistan\\graphify-repo\\tests\\fixtures\\cpp_paired\\Main.cpp", "source_location": "L5", "receiver": "f", "lang": "cpp"}], "cpp_type_table": {"path": "D:\\Project Assistan\\graphify-repo\\tests\\fixtures\\cpp_paired\\Main.cpp", "table": {"f": "Foo"}}}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
