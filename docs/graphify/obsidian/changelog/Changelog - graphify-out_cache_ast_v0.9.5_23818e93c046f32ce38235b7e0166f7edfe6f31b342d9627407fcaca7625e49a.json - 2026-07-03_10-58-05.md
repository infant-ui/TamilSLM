# Changelog: graphify-out/cache/ast/v0.9.5/23818e93c046f32ce38235b7e0166f7edfe6f31b342d9627407fcaca7625e49a.json
**Date:** 2026-07-03_10-58-05
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/23818e93c046f32ce38235b7e0166f7edfe6f31b342d9627407fcaca7625e49a.json b/graphify-out/cache/ast/v0.9.5/23818e93c046f32ce38235b7e0166f7edfe6f31b342d9627407fcaca7625e49a.json
new file mode 100644
index 0000000..ef2f3d1
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/23818e93c046f32ce38235b7e0166f7edfe6f31b342d9627407fcaca7625e49a.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_test_label_retry_py", "label": "test_label_retry.py", "file_type": "code", "source_file": "graphify-repo/tests/test_label_retry.py", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_test_label_retry_test_label_batch_recovers_via_split_on_invalid_json", "label": "test_label_batch_recovers_via_split_on_invalid_json()", "file_type": "code", "source_file": "graphify-repo/tests/test_label_retry.py", "source_location": "L12", "_callable": true}, {"id": "d_project_assistan_graphify_repo_tests_test_label_retry_rationale_1", "label": "Tests for graphify.llm._label_batch_with_retry \u2014 adaptive split-and-retry on JS", "file_type": "rationale", "source_file": "graphify-repo/tests/test_label_retry.py", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_test_label_retry_rationale_13", "label": "Demonstrates the bug fix.      The full batch of 4 communities triggers malfor", "file_type": "rationale", "source_file": "graphify-repo/tests/test_label_retry.py", "source_location": "L13"}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_test_label_retry_py", "target": "json", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/test_label_retry.py", "source_location": "L6", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_test_label_retry_py", "target": "re", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/test_label_retry.py", "source_location": "L7", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_test_label_retry_py", "target": "graphify", "relation": "imports_from", "context": "import", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/test_label_retry.py", "source_location": "L9", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_test_label_retry_py", "target": "d_project_assistan_graphify_repo_tests_test_label_retry_test_label_batch_recovers_via_split_on_invalid_json", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/test_label_retry.py", "source_location": "L12", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_test_label_retry_rationale_1", "target": "d_project_assistan_graphify_repo_tests_test_label_retry_py", "relation": "rationale_for", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/test_label_retry.py", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_test_label_retry_rationale_13", "target": "d_project_assistan_graphify_repo_tests_test_label_retry_test_label_batch_recovers_via_split_on_invalid_json", "relation": "rationale_for", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/test_label_retry.py", "source_location": "L13", "weight": 1.0}], "raw_calls": [{"caller_nid": "d_project_assistan_graphify_repo_tests_test_label_retry_test_label_batch_recovers_via_split_on_invalid_json", "callee": "llm_mod", "is_member_call": false, "indirect": true, "context": "argument", "source_file": "D:\\Project Assistan\\graphify-repo\\tests\\test_label_retry.py", "source_location": "L39"}, {"caller_nid": "d_project_assistan_graphify_repo_tests_test_label_retry_test_label_batch_recovers_via_split_on_invalid_json", "callee": "fake_call_llm", "is_member_call": false, "indirect": true, "context": "argument", "source_file": "D:\\Project Assistan\\graphify-repo\\tests\\test_label_retry.py", "source_location": "L39"}, {"caller_nid": "d_project_assistan_graphify_repo_tests_test_label_retry_test_label_batch_recovers_via_split_on_invalid_json", "callee": "_label_batch_with_retry", "is_member_call": true, "source_file": "D:\\Project Assistan\\graphify-repo\\tests\\test_label_retry.py", "source_location": "L41", "receiver": "llm_mod"}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
