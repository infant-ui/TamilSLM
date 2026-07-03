# Changelog: graphify-out/cache/ast/v0.9.5/23df39ffed8bb75a0bb359e3b6bf0fdb9575c9288e0c65408cf994c61fc5d1fe.json
**Date:** 2026-07-03_10-58-05
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/23df39ffed8bb75a0bb359e3b6bf0fdb9575c9288e0c65408cf994c61fc5d1fe.json b/graphify-out/cache/ast/v0.9.5/23df39ffed8bb75a0bb359e3b6bf0fdb9575c9288e0c65408cf994c61fc5d1fe.json
new file mode 100644
index 0000000..8787579
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/23df39ffed8bb75a0bb359e3b6bf0fdb9575c9288e0c65408cf994c61fc5d1fe.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_trigger", "label": "sample.trigger", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.trigger", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_accounttrigger", "label": "AccountTrigger", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.trigger", "source_location": "L1"}, {"id": "account", "label": "Account", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.trigger", "source_location": "L1"}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_trigger", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_accounttrigger", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.trigger", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_accounttrigger", "target": "account", "relation": "uses", "confidence": "INFERRED", "source_file": "graphify-repo/tests/fixtures/sample.trigger", "source_location": "L1", "weight": 1.0}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
