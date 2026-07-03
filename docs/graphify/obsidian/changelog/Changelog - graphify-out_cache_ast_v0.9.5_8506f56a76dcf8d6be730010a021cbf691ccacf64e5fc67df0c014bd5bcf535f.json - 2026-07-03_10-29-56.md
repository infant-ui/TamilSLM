# Changelog: graphify-out/cache/ast/v0.9.5/8506f56a76dcf8d6be730010a021cbf691ccacf64e5fc67df0c014bd5bcf535f.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/8506f56a76dcf8d6be730010a021cbf691ccacf64e5fc67df0c014bd5bcf535f.json b/graphify-out/cache/ast/v0.9.5/8506f56a76dcf8d6be730010a021cbf691ccacf64e5fc67df0c014bd5bcf535f.json
new file mode 100644
index 0000000..5a721e5
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/8506f56a76dcf8d6be730010a021cbf691ccacf64e5fc67df0c014bd5bcf535f.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_lfm", "label": "sample.lfm", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.lfm", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_tsampleform", "label": "TSampleForm", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.lfm", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_tpanel", "label": "TPanel", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.lfm", "source_location": "L7"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_tbutton", "label": "TButton", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.lfm", "source_location": "L12"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_buttonokclick", "label": "ButtonOKClick()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.lfm", "source_location": "L18"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_tlabel", "label": "TLabel", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.lfm", "source_location": "L20"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_ttimer", "label": "TTimer", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.lfm", "source_location": "L26"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_sample_timerrefreshtimer", "label": "TimerRefreshTimer()", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/sample.lfm", "source_location": "L28"}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_lfm", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_tsampleform", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.lfm", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_tsampleform", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_tpanel", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.lfm", "source_location": "L7", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_tpanel", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_tbutton", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.lfm", "source_location": "L12", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_tbutton", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_buttonokclick", "relation": "references", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.lfm", "source_location": "L18", "weight": 1.0, "context": "event"}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_tpanel", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_tlabel", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.lfm", "source_location": "L20", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_tsampleform", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_ttimer", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.lfm", "source_location": "L26", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_sample_ttimer", "target": "d_project_assistan_graphify_repo_tests_fixtures_sample_timerrefreshtimer", "relation": "references", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/sample.lfm", "source_location": "L28", "weight": 1.0, "context": "event"}], "input_tokens": 0, "output_tokens": 0}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
