# Changelog: graphify-out/cache/ast/v0.9.5/0b46ddb74891a10f409c3284bdd1cbdf8d74efa19ac5679d9c69a81d1728e9f1.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/0b46ddb74891a10f409c3284bdd1cbdf8d74efa19ac5679d9c69a81d1728e9f1.json b/graphify-out/cache/ast/v0.9.5/0b46ddb74891a10f409c3284bdd1cbdf8d74efa19ac5679d9c69a81d1728e9f1.json
new file mode 100644
index 0000000..ee97bec
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/0b46ddb74891a10f409c3284bdd1cbdf8d74efa19ac5679d9c69a81d1728e9f1.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_static_prop_php", "label": "sample_php_static_prop.php", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_php_static_prop.php", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_static_prop_defaultpalette", "label": "DefaultPalette", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_php_static_prop.php", "source_location": "L5", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_static_prop_colorresolver", "label": "ColorResolver", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_php_static_prop.php", "source_location": "L11", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_static_prop_colorresolver_primary", "label": ".primary()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_php_static_prop.php", "source_location": "L13", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_static_prop_colorresolver_accent", "label": ".accent()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_php_static_prop.php", "source_location": "L18", "_callable": true}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_static_prop_php", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_static_prop_defaultpalette", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_php_static_prop.php", "source_location": "L5", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_static_prop_php", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_static_prop_colorresolver", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_php_static_prop.php", "source_location": "L11", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_static_prop_colorresolver", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_static_prop_colorresolver_primary", "relation": "method", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_php_static_prop.php", "source_location": "L13", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_static_prop_colorresolver", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_static_prop_colorresolver_accent", "relation": "method", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_php_static_prop.php", "source_location": "L18", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_static_prop_colorresolver_primary", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_static_prop_defaultpalette", "relation": "uses_static_prop", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "graphify-repo/tests/fixtures/sample_php_static_prop.php", "source_location": "L15", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_static_prop_colorresolver_accent", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_static_prop_defaultpalette", "relation": "uses_static_prop", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "graphify-repo/tests/fixtures/sample_php_static_prop.php", "source_location": "L20", "weight": 1.0}], "raw_calls": []}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
