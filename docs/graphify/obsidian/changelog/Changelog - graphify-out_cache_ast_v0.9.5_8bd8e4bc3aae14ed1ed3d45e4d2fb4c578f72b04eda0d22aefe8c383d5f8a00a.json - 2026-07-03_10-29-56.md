# Changelog: graphify-out/cache/ast/v0.9.5/8bd8e4bc3aae14ed1ed3d45e4d2fb4c578f72b04eda0d22aefe8c383d5f8a00a.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/8bd8e4bc3aae14ed1ed3d45e4d2fb4c578f72b04eda0d22aefe8c383d5f8a00a.json b/graphify-out/cache/ast/v0.9.5/8bd8e4bc3aae14ed1ed3d45e4d2fb4c578f72b04eda0d22aefe8c383d5f8a00a.json
new file mode 100644
index 0000000..aa110b5
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/8bd8e4bc3aae14ed1ed3d45e4d2fb4c578f72b04eda0d22aefe8c383d5f8a00a.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_cpp_samedir_alpha_h", "label": "Alpha.h", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/cpp_samedir/Alpha.h", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_cpp_samedir_alpha_dup", "label": "Dup", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/cpp_samedir/Alpha.h", "source_location": "L1", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_cpp_samedir_alpha_dup_a", "label": "a", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/cpp_samedir/Alpha.h", "source_location": "L3"}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_cpp_samedir_alpha_h", "target": "d_project_assistan_graphify_repo_tests_fixtures_cpp_samedir_alpha_dup", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/cpp_samedir/Alpha.h", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_cpp_samedir_alpha_dup", "target": "d_project_assistan_graphify_repo_tests_fixtures_cpp_samedir_alpha_dup_a", "relation": "defines", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/cpp_samedir/Alpha.h", "source_location": "L3", "weight": 1.0, "context": "field"}], "raw_calls": []}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
