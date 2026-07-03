# Changelog: graphify-out/cache/ast/v0.9.5/2b06303553758eae70586d4f0fba3d086e5dda7dae80ce7db4ad1e02ddc37ef2.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/2b06303553758eae70586d4f0fba3d086e5dda7dae80ce7db4ad1e02ddc37ef2.json b/graphify-out/cache/ast/v0.9.5/2b06303553758eae70586d4f0fba3d086e5dda7dae80ce7db4ad1e02ddc37ef2.json
new file mode 100644
index 0000000..57bf83a
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/2b06303553758eae70586d4f0fba3d086e5dda7dae80ce7db4ad1e02ddc37ef2.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_test_pymupdf2_py", "label": "test_pymupdf2.py", "file_type": "code", "source_file": "test_pymupdf2.py", "source_location": "L1"}, {"id": "d_project_assistan_test_pymupdf2_fix_text", "label": "fix_text()", "file_type": "code", "source_file": "test_pymupdf2.py", "source_location": "L3", "_callable": true}], "edges": [{"source": "d_project_assistan_test_pymupdf2_py", "target": "fitz", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "test_pymupdf2.py", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_test_pymupdf2_py", "target": "d_project_assistan_test_pymupdf2_fix_text", "relation": "contains", "confidence": "EXTRACTED", "source_file": "test_pymupdf2.py", "source_location": "L3", "weight": 1.0}], "raw_calls": [{"caller_nid": "d_project_assistan_test_pymupdf2_fix_text", "callee": "decode", "is_member_call": true, "source_file": "D:\\Project Assistan\\test_pymupdf2.py", "source_location": "L5", "receiver": null}, {"caller_nid": "d_project_assistan_test_pymupdf2_fix_text", "callee": "encode", "is_member_call": true, "source_file": "D:\\Project Assistan\\test_pymupdf2.py", "source_location": "L5", "receiver": "text"}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
