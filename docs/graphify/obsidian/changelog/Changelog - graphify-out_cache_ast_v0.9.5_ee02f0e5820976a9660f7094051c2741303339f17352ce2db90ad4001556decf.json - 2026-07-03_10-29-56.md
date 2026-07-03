# Changelog: graphify-out/cache/ast/v0.9.5/ee02f0e5820976a9660f7094051c2741303339f17352ce2db90ad4001556decf.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/ee02f0e5820976a9660f7094051c2741303339f17352ce2db90ad4001556decf.json b/graphify-out/cache/ast/v0.9.5/ee02f0e5820976a9660f7094051c2741303339f17352ce2db90ad4001556decf.json
new file mode 100644
index 0000000..e533414
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/ee02f0e5820976a9660f7094051c2741303339f17352ce2db90ad4001556decf.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_cpp_samedir_beta_h", "label": "Beta.h", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/cpp_samedir/Beta.h", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_cpp_samedir_beta_dup", "label": "Dup", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/cpp_samedir/Beta.h", "source_location": "L1", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_cpp_samedir_beta_dup_b", "label": "b", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/cpp_samedir/Beta.h", "source_location": "L3"}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_cpp_samedir_beta_h", "target": "d_project_assistan_graphify_repo_tests_fixtures_cpp_samedir_beta_dup", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/cpp_samedir/Beta.h", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_cpp_samedir_beta_dup", "target": "d_project_assistan_graphify_repo_tests_fixtures_cpp_samedir_beta_dup_b", "relation": "defines", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/cpp_samedir/Beta.h", "source_location": "L3", "weight": 1.0, "context": "field"}], "raw_calls": []}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
