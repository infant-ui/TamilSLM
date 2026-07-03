# Changelog: graphify-out/cache/ast/v0.9.5/13debd3c1d09926011c770c498a853d1ea03e1b2e36ffeed01b607287eea8926.json
**Date:** 2026-07-03_10-58-05
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/13debd3c1d09926011c770c498a853d1ea03e1b2e36ffeed01b607287eea8926.json b/graphify-out/cache/ast/v0.9.5/13debd3c1d09926011c770c498a853d1ea03e1b2e36ffeed01b607287eea8926.json
new file mode 100644
index 0000000..9a1098b
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/13debd3c1d09926011c770c498a853d1ea03e1b2e36ffeed01b607287eea8926.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_slnx", "label": "sample.slnx", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.slnx", "source_location": null}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_src_domain_domain_csproj", "label": "Domain", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/src/Domain/Domain.csproj", "source_location": null}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_src_webapi_webapi_csproj", "label": "WebApi", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/src/WebApi/WebApi.csproj", "source_location": null}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_tests_tests_tests_csproj", "label": "Tests", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/tests/Tests/Tests.csproj", "source_location": null}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_slnx", "target": "d_project_assistan_graphify_repo_tests_fixtures_src_domain_domain_csproj", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.slnx", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_slnx", "target": "d_project_assistan_graphify_repo_tests_fixtures_src_webapi_webapi_csproj", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.slnx", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_slnx", "target": "d_project_assistan_graphify_repo_tests_fixtures_tests_tests_tests_csproj", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.slnx", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_src_webapi_webapi_csproj", "target": "d_project_assistan_graphify_repo_tests_fixtures_src_domain_domain_csproj", "relation": "imports", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.slnx", "weight": 1.0}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
