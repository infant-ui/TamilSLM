# Changelog: graphify-out/cache/ast/v0.9.5/055b788fd29a5857a1387c6aaf097c88cb2994845dddf07ac85d56bc080d5f0f.json
**Date:** 2026-07-03_10-41-42
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/055b788fd29a5857a1387c6aaf097c88cb2994845dddf07ac85d56bc080d5f0f.json b/graphify-out/cache/ast/v0.9.5/055b788fd29a5857a1387c6aaf097c88cb2994845dddf07ac85d56bc080d5f0f.json
new file mode 100644
index 0000000..8ba8332
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/055b788fd29a5857a1387c6aaf097c88cb2994845dddf07ac85d56bc080d5f0f.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_analyze_agreement_py", "label": "analyze_agreement.py", "file_type": "code", "source_file": "analyze_agreement.py", "source_location": "L1"}, {"id": "d_project_assistan_analyze_agreement_main", "label": "main()", "file_type": "code", "source_file": "analyze_agreement.py", "source_location": "L4", "_callable": true}], "edges": [{"source": "d_project_assistan_analyze_agreement_py", "target": "json", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "analyze_agreement.py", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_analyze_agreement_py", "target": "sklearn_metrics", "relation": "imports_from", "context": "import", "confidence": "EXTRACTED", "source_file": "analyze_agreement.py", "source_location": "L2", "weight": 1.0}, {"source": "d_project_assistan_analyze_agreement_py", "target": "d_project_assistan_analyze_agreement_main", "relation": "contains", "confidence": "EXTRACTED", "source_file": "analyze_agreement.py", "source_location": "L4", "weight": 1.0}], "raw_calls": [{"caller_nid": "d_project_assistan_analyze_agreement_main", "callee": "load", "is_member_call": true, "source_file": "D:\\Project Assistan\\analyze_agreement.py", "source_location": "L7", "receiver": "json"}, {"caller_nid": "d_project_assistan_analyze_agreement_main", "callee": "f", "is_member_call": false, "indirect": true, "context": "argument", "source_file": "D:\\Project Assistan\\analyze_agreement.py", "source_location": "L7"}, {"caller_nid": "d_project_assistan_analyze_agreement_main", "callee": "load", "is_member_call": true, "source_file": "D:\\Project Assistan\\analyze_agreement.py", "source_location": "L10", "receiver": "json"}, {"caller_nid": "d_project_assistan_analyze_agreement_main", "callee": "f", "is_member_call": false, "indirect": true, "context": "argument", "source_file": "D:\\Project Assistan\\analyze_agreement.py", "source_location": "L10"}, {"caller_nid": "d_project_assistan_analyze_agreement_main", "callee": "items", "is_member_call": true, "source_file": "D:\\Project Assistan\\analyze_agreement.py", "source_location": "L23", "receiver": "human_data"}, {"caller_nid": "d_project_assistan_analyze_agreement_main", "callee": "append", "is_member_call": true, "source_file": "D:\\Project Assistan\\analyze_agreement.py", "source_location": "L26", "receiver": "y_judge"}, {"caller_nid": "d_project_assistan_analyze_agreement_main", "callee": "append", "is_member_call": true, "source_file": "D:\\Project Assistan\\analyze_agreement.py", "source_location": "L27", "receiver": "y_human"}, {"caller_nid": "d_project_assistan_analyze_agreement_main", "callee": "append", "is_member_call": true, "source_file": "D:\\Project Assistan\\analyze_agreement.py", "source_location": "L31", "receiver": "disagreements"}, {"caller_nid": "d_project_assistan_analyze_agreement_main", "callee": "cohen_kappa_score", "is_member_call": false, "source_file": "D:\\Project Assistan\\analyze_agreement.py", "source_location": "L43", "receiver": null}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
