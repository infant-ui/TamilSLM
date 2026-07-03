# Changelog: graphify-out/cache/ast/v0.9.5/e9aca668dbe61f5e53dea906e7809f2caa1261fbe1e4394674096968c45c7c3c.json
**Date:** 2026-07-03_10-58-05
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/e9aca668dbe61f5e53dea906e7809f2caa1261fbe1e4394674096968c45c7c3c.json b/graphify-out/cache/ast/v0.9.5/e9aca668dbe61f5e53dea906e7809f2caa1261fbe1e4394674096968c45c7c3c.json
new file mode 100644
index 0000000..496056b
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/e9aca668dbe61f5e53dea906e7809f2caa1261fbe1e4394674096968c45c7c3c.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_csproj", "label": "sample.csproj", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.csproj", "source_location": null}, {"id": "framework_net8_0", "label": "net8.0", "file_type": "concept", "source_file": "graphify-repo/tests/fixtures/sample.csproj", "source_location": null}, {"id": "nuget_microsoft_aspnetcore_authentication_jwtbearer", "label": "Microsoft.AspNetCore.Authentication.JwtBearer (8.0.0)", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.csproj", "source_location": null}, {"id": "nuget_swashbuckle_aspnetcore", "label": "Swashbuckle.AspNetCore (6.5.0)", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.csproj", "source_location": null}, {"id": "nuget_mediatr", "label": "MediatR (12.2.0)", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.csproj", "source_location": null}, {"id": "nuget_fluentvalidation", "label": "FluentValidation (11.9.0)", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.csproj", "source_location": null}, {"id": "d_project_assistan_graphify_repo_tests_domain_domain_csproj", "label": "Domain.csproj", "file_type": "code", "source_file": "graphify-repo/tests/Domain/Domain.csproj", "source_location": null}, {"id": "d_project_assistan_graphify_repo_tests_infrastructure_infrastructure_csproj", "label": "Infrastructure.csproj", "file_type": "code", "source_file": "graphify-repo/tests/Infrastructure/Infrastructure.csproj", "source_location": null}, {"id": "sdk_microsoft_net_sdk_web", "label": "Microsoft.NET.Sdk.Web", "file_type": "concept", "source_file": "graphify-repo/tests/fixtures/sample.csproj", "source_location": null}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_csproj", "target": "framework_net8_0", "relation": "references", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.csproj", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_csproj", "target": "nuget_microsoft_aspnetcore_authentication_jwtbearer", "relation": "imports", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.csproj", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_csproj", "target": "nuget_swashbuckle_aspnetcore", "relation": "imports", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.csproj", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_csproj", "target": "nuget_mediatr", "relation": "imports", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.csproj", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_csproj", "target": "nuget_fluentvalidation", "relation": "imports", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.csproj", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_csproj", "target": "d_project_assistan_graphify_repo_tests_domain_domain_csproj", "relation": "imports", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.csproj", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_csproj", "target": "d_project_assistan_graphify_repo_tests_infrastructure_infrastructure_csproj", "relation": "imports", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.csproj", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_csproj", "target": "sdk_microsoft_net_sdk_web", "relation": "references", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.csproj", "weight": 1.0}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
