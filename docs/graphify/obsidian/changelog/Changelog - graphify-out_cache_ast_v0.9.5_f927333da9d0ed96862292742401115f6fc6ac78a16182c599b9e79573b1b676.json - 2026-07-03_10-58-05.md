# Changelog: graphify-out/cache/ast/v0.9.5/f927333da9d0ed96862292742401115f6fc6ac78a16182c599b9e79573b1b676.json
**Date:** 2026-07-03_10-58-05
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/f927333da9d0ed96862292742401115f6fc6ac78a16182c599b9e79573b1b676.json b/graphify-out/cache/ast/v0.9.5/f927333da9d0ed96862292742401115f6fc6ac78a16182c599b9e79573b1b676.json
new file mode 100644
index 0000000..de77e5a
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/f927333da9d0ed96862292742401115f6fc6ac78a16182c599b9e79573b1b676.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_verify_task3b_py", "label": "verify_task3b.py", "file_type": "code", "source_file": "verify_task3b.py", "source_location": "L1"}, {"id": "d_project_assistan_verify_task3b_kill_port", "label": "kill_port()", "file_type": "code", "source_file": "verify_task3b.py", "source_location": "L9", "_callable": true}, {"id": "d_project_assistan_verify_task3b_stream_reader", "label": "stream_reader()", "file_type": "code", "source_file": "verify_task3b.py", "source_location": "L41", "_callable": true}], "edges": [{"source": "d_project_assistan_verify_task3b_py", "target": "subprocess", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "verify_task3b.py", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_verify_task3b_py", "target": "time", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "verify_task3b.py", "source_location": "L2", "weight": 1.0}, {"source": "d_project_assistan_verify_task3b_py", "target": "requests", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "verify_task3b.py", "source_location": "L3", "weight": 1.0}, {"source": "d_project_assistan_verify_task3b_py", "target": "json", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "verify_task3b.py", "source_location": "L4", "weight": 1.0}, {"source": "d_project_assistan_verify_task3b_py", "target": "os", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "verify_task3b.py", "source_location": "L5", "weight": 1.0}, {"source": "d_project_assistan_verify_task3b_py", "target": "d_project_assistan_verify_task3b_kill_port", "relation": "contains", "confidence": "EXTRACTED", "source_file": "verify_task3b.py", "source_location": "L9", "weight": 1.0}, {"source": "d_project_assistan_verify_task3b_py", "target": "threading", "relation": "imports", "context": "import", "confidence": "EXTRACTED", "source_file": "verify_task3b.py", "source_location": "L39", "weight": 1.0}, {"source": "d_project_assistan_verify_task3b_py", "target": "d_project_assistan_verify_task3b_stream_reader", "relation": "contains", "confidence": "EXTRACTED", "source_file": "verify_task3b.py", "source_location": "L41", "weight": 1.0}], "raw_calls": [{"caller_nid": "d_project_assistan_verify_task3b_kill_port", "callee": "run", "is_member_call": true, "source_file": "D:\\Project Assistan\\verify_task3b.py", "source_location": "L10", "receiver": "subprocess"}, {"caller_nid": "d_project_assistan_verify_task3b_stream_reader", "callee": "strip", "is_member_call": true, "source_file": "D:\\Project Assistan\\verify_task3b.py", "source_location": "L43", "receiver": null}, {"caller_nid": "d_project_assistan_verify_task3b_stream_reader", "callee": "decode", "is_member_call": true, "source_file": "D:\\Project Assistan\\verify_task3b.py", "source_location": "L43", "receiver": "line"}, {"caller_nid": "d_project_assistan_verify_task3b_stream_reader", "callee": "decode", "is_member_call": true, "source_file": "D:\\Project Assistan\\verify_task3b.py", "source_location": "L45", "receiver": null}, {"caller_nid": "d_project_assistan_verify_task3b_stream_reader", "callee": "encode", "is_member_call": true, "source_file": "D:\\Project Assistan\\verify_task3b.py", "source_location": "L45", "receiver": null}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
