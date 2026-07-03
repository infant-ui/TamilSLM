# Changelog: graphify-out/cache/ast/v0.9.5/a877dfb48c8c005477bde35a3813cbb59f642fac437e911f7b5d8715d1af39a4.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/a877dfb48c8c005477bde35a3813cbb59f642fac437e911f7b5d8715d1af39a4.json b/graphify-out/cache/ast/v0.9.5/a877dfb48c8c005477bde35a3813cbb59f642fac437e911f7b5d8715d1af39a4.json
new file mode 100644
index 0000000..c2b33cb
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/a877dfb48c8c005477bde35a3813cbb59f642fac437e911f7b5d8715d1af39a4.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_test_cpp_preprocess_py", "label": "test_cpp_preprocess.py", "file_type": "code", "source_file": "graphify-repo/tests/test_cpp_preprocess.py", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_test_cpp_preprocess_test_cpp_preprocess_passes_absolute_path", "label": "test_cpp_preprocess_passes_absolute_path()", "file_type": "code", "source_file": "graphify-repo/tests/test_cpp_preprocess.py", "source_location": "L10", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_test_cpp_preprocess_rationale_1", "label": "The Fortran C-preprocessor path is hardened against argument injection (F5).", "file_type": "rationale", "source_file": "graphify-repo/tests/test_cpp_preprocess.py", "source_location": "L1"}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_test_cpp_preprocess_py", "target": "graphify", "relation": "imports_from", "context": "import", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/test_cpp_preprocess.py", "source_location": "L7", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_test_cpp_preprocess_py", "target": "d_project_assistan_graphify_repo_tests_test_cpp_preprocess_test_cpp_preprocess_passes_absolute_path", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/test_cpp_preprocess.py", "source_location": "L10", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_test_cpp_preprocess_rationale_1", "target": "d_project_assistan_graphify_repo_tests_test_cpp_preprocess_py", "relation": "rationale_for", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/test_cpp_preprocess.py", "source_location": "L1", "weight": 1.0}], "raw_calls": [{"caller_nid": "d_project_assistan_graphify_repo_tests_test_cpp_preprocess_test_cpp_preprocess_passes_absolute_path", "callee": "write_text", "is_member_call": true, "source_file": "D:\\Project Assistan\\graphify-repo\\tests\\test_cpp_preprocess.py", "source_location": "L12", "receiver": "f"}, {"caller_nid": "d_project_assistan_graphify_repo_tests_test_cpp_preprocess_test_cpp_preprocess_passes_absolute_path", "callee": "fake_run", "is_member_call": false, "indirect": true, "context": "argument", "source_file": "D:\\Project Assistan\\graphify-repo\\tests\\test_cpp_preprocess.py", "source_location": "L26"}, {"caller_nid": "d_project_assistan_graphify_repo_tests_test_cpp_preprocess_test_cpp_preprocess_passes_absolute_path", "callee": "_cpp_preprocess", "is_member_call": true, "source_file": "D:\\Project Assistan\\graphify-repo\\tests\\test_cpp_preprocess.py", "source_location": "L28", "receiver": "extract"}, {"caller_nid": "d_project_assistan_graphify_repo_tests_test_cpp_preprocess_test_cpp_preprocess_passes_absolute_path", "callee": "startswith", "is_member_call": true, "source_file": "D:\\Project Assistan\\graphify-repo\\tests\\test_cpp_preprocess.py", "source_location": "L31", "receiver": "last_arg"}, {"caller_nid": "d_project_assistan_graphify_repo_tests_test_cpp_preprocess_test_cpp_preprocess_passes_absolute_path", "callee": "startswith", "is_member_call": true, "source_file": "D:\\Project Assistan\\graphify-repo\\tests\\test_cpp_preprocess.py", "source_location": "L32", "receiver": "last_arg"}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
