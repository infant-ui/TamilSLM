# Changelog: graphify-out/cache/ast/v0.9.5/60e2e6091d24db04cb60bc6fea635ed96e378ff1eaa5ee5b64048750c9807b96.json
**Date:** 2026-07-03_10-58-05
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/60e2e6091d24db04cb60bc6fea635ed96e378ff1eaa5ee5b64048750c9807b96.json b/graphify-out/cache/ast/v0.9.5/60e2e6091d24db04cb60bc6fea635ed96e378ff1eaa5ee5b64048750c9807b96.json
new file mode 100644
index 0000000..6d8f179
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/60e2e6091d24db04cb60bc6fea635ed96e378ff1eaa5ee5b64048750c9807b96.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_preprocessed_f90", "label": "sample_preprocessed.F90", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_preprocessed.F90", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_preprocessed_shapes", "label": "shapes", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_preprocessed.F90", "source_location": "L3"}, {"id": "mpi", "label": "mpi", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_preprocessed.F90", "source_location": "L5"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_preprocessed_compute_volume", "label": "compute_volume()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_preprocessed.F90", "source_location": "L11"}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_preprocessed_f90", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_preprocessed_shapes", "relation": "defines", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_preprocessed.F90", "source_location": "L3", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_preprocessed_shapes", "target": "mpi", "relation": "imports", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_preprocessed.F90", "source_location": "L5", "weight": 1.0, "context": "use"}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_preprocessed_shapes", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_preprocessed_compute_volume", "relation": "defines", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_preprocessed.F90", "source_location": "L11", "weight": 1.0}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
