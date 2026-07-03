# Changelog: graphify-out/cache/ast/v0.9.5/961bf095d7be7e03b58fc4787f48de9ee1d0fe1467e1059c44bac98a8d452e99.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/961bf095d7be7e03b58fc4787f48de9ee1d0fe1467e1059c44bac98a8d452e99.json b/graphify-out/cache/ast/v0.9.5/961bf095d7be7e03b58fc4787f48de9ee1d0fe1467e1059c44bac98a8d452e99.json
new file mode 100644
index 0000000..5505850
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/961bf095d7be7e03b58fc4787f48de9ee1d0fe1467e1059c44bac98a8d452e99.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_config_php", "label": "sample_php_config.php", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_php_config.php", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_config_throttle", "label": "Throttle", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_php_config.php", "source_location": "L5", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_config_ratelimiter", "label": "RateLimiter", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_php_config.php", "source_location": "L11", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_config_ratelimiter_persecond", "label": ".perSecond()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_php_config.php", "source_location": "L13", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_config_ratelimiter_perday", "label": ".perDay()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_php_config.php", "source_location": "L18", "_callable": true}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_config_php", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_config_throttle", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_php_config.php", "source_location": "L5", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_config_php", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_config_ratelimiter", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_php_config.php", "source_location": "L11", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_config_ratelimiter", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_config_ratelimiter_persecond", "relation": "method", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_php_config.php", "source_location": "L13", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_config_ratelimiter", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_config_ratelimiter_perday", "relation": "method", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_php_config.php", "source_location": "L18", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_config_ratelimiter_persecond", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_config_throttle", "relation": "uses_config", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "graphify-repo/tests/fixtures/sample_php_config.php", "source_location": "L15", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_config_ratelimiter_perday", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_config_throttle", "relation": "uses_config", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "graphify-repo/tests/fixtures/sample_php_config.php", "source_location": "L20", "weight": 1.0}], "raw_calls": [{"caller_nid": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_config_ratelimiter_persecond", "callee": "config", "is_member_call": false, "source_file": "D:\\Project Assistan\\graphify-repo\\tests\\fixtures\\sample_php_config.php", "source_location": "L15", "receiver": null}, {"caller_nid": "d_project_assistan_graphify_repo_tests_fixtures_sample_php_config_ratelimiter_perday", "callee": "config", "is_member_call": false, "source_file": "D:\\Project Assistan\\graphify-repo\\tests\\fixtures\\sample_php_config.php", "source_location": "L20", "receiver": null}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
