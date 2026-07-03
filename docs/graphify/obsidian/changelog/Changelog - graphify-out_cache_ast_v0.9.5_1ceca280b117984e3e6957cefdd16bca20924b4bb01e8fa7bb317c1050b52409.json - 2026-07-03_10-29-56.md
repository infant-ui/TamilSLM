# Changelog: graphify-out/cache/ast/v0.9.5/1ceca280b117984e3e6957cefdd16bca20924b4bb01e8fa7bb317c1050b52409.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/1ceca280b117984e3e6957cefdd16bca20924b4bb01e8fa7bb317c1050b52409.json b/graphify-out/cache/ast/v0.9.5/1ceca280b117984e3e6957cefdd16bca20924b4bb01e8fa7bb317c1050b52409.json
new file mode 100644
index 0000000..6883eb8
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/1ceca280b117984e3e6957cefdd16bca20924b4bb01e8fa7bb317c1050b52409.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_conftest_py", "label": "conftest.py", "file_type": "code", "source_file": "graphify-repo/tests/conftest.py", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_conftest_pytest_collection_modifyitems", "label": "pytest_collection_modifyitems()", "file_type": "code", "source_file": "graphify-repo/tests/conftest.py", "source_location": "L15", "_callable": true}, {"id": "any", "label": "Any", "file_type": "code", "source_file": "", "source_location": "", "origin_file": "D:\\Project Assistan\\graphify-repo\\tests\\conftest.py"}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_conftest_py", "target": "typing", "relation": "imports_from", "context": "import", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/conftest.py", "source_location": "L3", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_conftest_py", "target": "pytest", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/conftest.py", "source_location": "L5", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_conftest_py", "target": "d_project_assistan_graphify_repo_tests_conftest_pytest_collection_modifyitems", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/conftest.py", "source_location": "L15", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_conftest_pytest_collection_modifyitems", "target": "any", "relation": "references", "context": "generic_arg", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/conftest.py", "source_location": "L15", "weight": 1.0}], "raw_calls": [{"caller_nid": "d_project_assistan_graphify_repo_tests_conftest_pytest_collection_modifyitems", "callee": "add_marker", "is_member_call": true, "source_file": "D:\\Project Assistan\\graphify-repo\\tests\\conftest.py", "source_location": "L20", "receiver": "item"}, {"caller_nid": "d_project_assistan_graphify_repo_tests_conftest_pytest_collection_modifyitems", "callee": "filterwarnings", "is_member_call": true, "source_file": "D:\\Project Assistan\\graphify-repo\\tests\\conftest.py", "source_location": "L20", "receiver": null}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
