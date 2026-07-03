# Changelog: graphify-out/cache/ast/v0.9.5/a975a3c7c595e8e8d0710b5f50c625c2e333ad208bf9fb2ed4053fc9971cbebe.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/a975a3c7c595e8e8d0710b5f50c625c2e333ad208bf9fb2ed4053fc9971cbebe.json b/graphify-out/cache/ast/v0.9.5/a975a3c7c595e8e8d0710b5f50c625c2e333ad208bf9fb2ed4053fc9971cbebe.json
new file mode 100644
index 0000000..70b022d
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/a975a3c7c595e8e8d0710b5f50c625c2e333ad208bf9fb2ed4053fc9971cbebe.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_lpk", "label": "sample.lpk", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.lpk", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_samplepackage", "label": "SamplePackage", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.lpk", "source_location": "L1"}, {"id": "fcl", "label": "FCL", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.lpk", "source_location": "L1"}, {"id": "lcl", "label": "LCL", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.lpk", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_pas", "label": "sample", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.lpk", "source_location": "L1"}, {"id": "sampleutils", "label": "sampleutils", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.lpk", "source_location": "L1"}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_lpk", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_samplepackage", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.lpk", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_samplepackage", "target": "fcl", "relation": "imports", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.lpk", "source_location": "L1", "weight": 1.0, "context": "import"}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_samplepackage", "target": "lcl", "relation": "imports", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.lpk", "source_location": "L1", "weight": 1.0, "context": "import"}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_samplepackage", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_pas", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.lpk", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_samplepackage", "target": "sampleutils", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.lpk", "source_location": "L1", "weight": 1.0}], "input_tokens": 0, "output_tokens": 0}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
