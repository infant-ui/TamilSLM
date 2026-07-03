# Changelog: graphify-out/cache/ast/v0.9.5/86464f2d4e4edc939d382b4fef0075ac4704b5148277a2f669abdec125a40952.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/86464f2d4e4edc939d382b4fef0075ac4704b5148277a2f669abdec125a40952.json b/graphify-out/cache/ast/v0.9.5/86464f2d4e4edc939d382b4fef0075ac4704b5148277a2f669abdec125a40952.json
new file mode 100644
index 0000000..e0c9684
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/86464f2d4e4edc939d382b4fef0075ac4704b5148277a2f669abdec125a40952.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_import_ps1", "label": "sample_import.ps1", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_import.ps1", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_import_invoke_main", "label": "Invoke-Main()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_import.ps1", "source_location": "L6"}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_import_ps1", "target": "foo", "relation": "imports_from", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_import.ps1", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_import_ps1", "target": "bar", "relation": "imports_from", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_import.ps1", "source_location": "L2", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_import_ps1", "target": "shared", "relation": "imports_from", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_import.ps1", "source_location": "L3", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_import_ps1", "target": "utils", "relation": "imports_from", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_import.ps1", "source_location": "L4", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_import_ps1", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_import_invoke_main", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_import.ps1", "source_location": "L6", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_import_ps1", "target": "innermod", "relation": "imports_from", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_import.ps1", "source_location": "L7", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_import_ps1", "target": "innershared", "relation": "imports_from", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_import.ps1", "source_location": "L8", "weight": 1.0}], "raw_calls": [{"caller_nid": "d_project_assistan_graphify_repo_tests_fixtures_sample_import_invoke_main", "callee": "Get-Data", "is_member_call": false, "source_file": "D:\\Project Assistan\\graphify-repo\\tests\\fixtures\\sample_import.ps1", "source_location": "L9"}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
