# Changelog: graphify-out/cache/ast/v0.9.5/f8a7d869a1727b6c1002fda479192bd7ffe570826a81982579732ff8db568cad.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/f8a7d869a1727b6c1002fda479192bd7ffe570826a81982579732ff8db568cad.json b/graphify-out/cache/ast/v0.9.5/f8a7d869a1727b6c1002fda479192bd7ffe570826a81982579732ff8db568cad.json
new file mode 100644
index 0000000..1859b80
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/f8a7d869a1727b6c1002fda479192bd7ffe570826a81982579732ff8db568cad.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_sln", "label": "sample.sln", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.sln", "source_location": null}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_src_webapi_webapi_csproj", "label": "WebApi", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/src/WebApi/WebApi.csproj", "source_location": null}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_src_domain_domain_csproj", "label": "Domain", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/src/Domain/Domain.csproj", "source_location": null}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_tests_tests_tests_csproj", "label": "Tests", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/tests/Tests/Tests.csproj", "source_location": null}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_sln", "target": "d_project_assistan_graphify_repo_tests_fixtures_src_webapi_webapi_csproj", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.sln", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_sln", "target": "d_project_assistan_graphify_repo_tests_fixtures_src_domain_domain_csproj", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.sln", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_sln", "target": "d_project_assistan_graphify_repo_tests_fixtures_tests_tests_tests_csproj", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.sln", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_src_webapi_webapi_csproj", "target": "d_project_assistan_graphify_repo_tests_fixtures_src_domain_domain_csproj", "relation": "imports", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.sln", "weight": 1.0}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
