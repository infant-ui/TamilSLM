# Changelog: graphify-out/cache/ast/v0.9.5/31916109aefa73d6cec5b45d3c669050d518931632398a80ef0dc1754e783709.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/31916109aefa73d6cec5b45d3c669050d518931632398a80ef0dc1754e783709.json b/graphify-out/cache/ast/v0.9.5/31916109aefa73d6cec5b45d3c669050d518931632398a80ef0dc1754e783709.json
new file mode 100644
index 0000000..fcdf923
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/31916109aefa73d6cec5b45d3c669050d518931632398a80ef0dc1754e783709.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_preflight_check_py", "label": "preflight_check.py", "file_type": "code", "source_file": "preflight_check.py", "source_location": "L1"}, {"id": "d_project_assistan_preflight_check_test_pdf", "label": "test_pdf()", "file_type": "code", "source_file": "preflight_check.py", "source_location": "L5", "_callable": true}], "edges": [{"source": "d_project_assistan_preflight_check_py", "target": "fitz", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "preflight_check.py", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_preflight_check_py", "target": "re", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "preflight_check.py", "source_location": "L2", "weight": 1.0}, {"source": "d_project_assistan_preflight_check_py", "target": "sys", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "preflight_check.py", "source_location": "L3", "weight": 1.0}, {"source": "d_project_assistan_preflight_check_py", "target": "d_project_assistan_preflight_check_test_pdf", "relation": "contains", "confidence": "EXTRACTED", "source_file": "preflight_check.py", "source_location": "L5", "weight": 1.0}], "raw_calls": [{"caller_nid": "d_project_assistan_preflight_check_test_pdf", "callee": "get_text", "is_member_call": true, "source_file": "D:\\Project Assistan\\preflight_check.py", "source_location": "L15", "receiver": null}, {"caller_nid": "d_project_assistan_preflight_check_test_pdf", "callee": "get_text", "is_member_call": true, "source_file": "D:\\Project Assistan\\preflight_check.py", "source_location": "L24", "receiver": null}, {"caller_nid": "d_project_assistan_preflight_check_test_pdf", "callee": "findall", "is_member_call": true, "source_file": "D:\\Project Assistan\\preflight_check.py", "source_location": "L31", "receiver": "re"}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
