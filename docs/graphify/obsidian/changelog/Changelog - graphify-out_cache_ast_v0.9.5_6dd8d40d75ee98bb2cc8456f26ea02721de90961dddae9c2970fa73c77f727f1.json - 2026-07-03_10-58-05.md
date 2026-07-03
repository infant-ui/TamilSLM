# Changelog: graphify-out/cache/ast/v0.9.5/6dd8d40d75ee98bb2cc8456f26ea02721de90961dddae9c2970fa73c77f727f1.json
**Date:** 2026-07-03_10-58-05
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/6dd8d40d75ee98bb2cc8456f26ea02721de90961dddae9c2970fa73c77f727f1.json b/graphify-out/cache/ast/v0.9.5/6dd8d40d75ee98bb2cc8456f26ea02721de90961dddae9c2970fa73c77f727f1.json
new file mode 100644
index 0000000..d08faf4
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/6dd8d40d75ee98bb2cc8456f26ea02721de90961dddae9c2970fa73c77f727f1.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_spock_groovy", "label": "sample_spock.groovy", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_spock.groovy", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_spock_samplespec", "label": "SampleSpec", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_spock.groovy", "source_location": "L5"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_spock_samplespec_setup", "label": ".setup()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_spock.groovy", "source_location": "L7"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_spock_samplespec_should_process_valid_input", "label": "\"should process valid input\"", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_spock.groovy", "source_location": "L11"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_spock_samplespec_should_not_change_value_when_it_s_already_correct", "label": "\"should not change value when it's already correct\"", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_spock.groovy", "source_location": "L22"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_spock_samplespec_should_handle_input_and_return_expected", "label": "\"should handle #input and return #expected\"", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample_spock.groovy", "source_location": "L33"}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_spock_groovy", "target": "specification", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_spock.groovy", "source_location": "L3", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_spock_groovy", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_spock_samplespec", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_spock.groovy", "source_location": "L5", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_spock_samplespec", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_spock_samplespec_setup", "relation": "method", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_spock.groovy", "source_location": "L7", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_spock_samplespec", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_spock_samplespec_should_process_valid_input", "relation": "method", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_spock.groovy", "source_location": "L11", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_spock_samplespec", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_spock_samplespec_should_not_change_value_when_it_s_already_correct", "relation": "method", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_spock.groovy", "source_location": "L22", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_spock_samplespec", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_spock_samplespec_should_handle_input_and_return_expected", "relation": "method", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample_spock.groovy", "source_location": "L33", "weight": 1.0}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
