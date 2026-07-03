# Changelog: graphify-out/cache/ast/v0.9.5/9e8f6958b5fc89ad554c82646cfcdb7d004b495a79b04110a1c77b1c5ef988f3.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/9e8f6958b5fc89ad554c82646cfcdb7d004b495a79b04110a1c77b1c5ef988f3.json b/graphify-out/cache/ast/v0.9.5/9e8f6958b5fc89ad554c82646cfcdb7d004b495a79b04110a1c77b1c5ef988f3.json
new file mode 100644
index 0000000..bb3745e
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/9e8f6958b5fc89ad554c82646cfcdb7d004b495a79b04110a1c77b1c5ef988f3.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_test_class7_py", "label": "test_class7.py", "file_type": "code", "source_file": "test_class7.py", "source_location": "L1"}, {"id": "d_project_assistan_test_class7_test_file", "label": "test_file()", "file_type": "code", "source_file": "test_class7.py", "source_location": "L4", "_callable": true}], "edges": [{"source": "d_project_assistan_test_class7_py", "target": "fitz", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "test_class7.py", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_test_class7_py", "target": "re", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "test_class7.py", "source_location": "L2", "weight": 1.0}, {"source": "d_project_assistan_test_class7_py", "target": "d_project_assistan_test_class7_test_file", "relation": "contains", "confidence": "EXTRACTED", "source_file": "test_class7.py", "source_location": "L4", "weight": 1.0}], "raw_calls": [{"caller_nid": "d_project_assistan_test_class7_test_file", "callee": "get_text", "is_member_call": true, "source_file": "D:\\Project Assistan\\test_class7.py", "source_location": "L11", "receiver": null}, {"caller_nid": "d_project_assistan_test_class7_test_file", "callee": "find", "is_member_call": true, "source_file": "D:\\Project Assistan\\test_class7.py", "source_location": "L18", "receiver": "text"}, {"caller_nid": "d_project_assistan_test_class7_test_file", "callee": "ascii", "is_member_call": false, "source_file": "D:\\Project Assistan\\test_class7.py", "source_location": "L20", "receiver": null}, {"caller_nid": "d_project_assistan_test_class7_test_file", "callee": "ord", "is_member_call": false, "source_file": "D:\\Project Assistan\\test_class7.py", "source_location": "L23", "receiver": null}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
