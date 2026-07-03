# Changelog: graphify-out/cache/ast/v0.9.5/d48e9fb7de4f798ebcf802a897a23a083084e1a0fd62faaad94812c2328917ab.json
**Date:** 2026-07-03_10-58-05
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/d48e9fb7de4f798ebcf802a897a23a083084e1a0fd62faaad94812c2328917ab.json b/graphify-out/cache/ast/v0.9.5/d48e9fb7de4f798ebcf802a897a23a083084e1a0fd62faaad94812c2328917ab.json
new file mode 100644
index 0000000..1e2b2ff
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/d48e9fb7de4f798ebcf802a897a23a083084e1a0fd62faaad94812c2328917ab.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_graphify_init_py", "label": "__init__.py", "file_type": "code", "source_file": "graphify-repo/graphify/__init__.py", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_graphify_init_getattr", "label": "__getattr__()", "file_type": "code", "source_file": "graphify-repo/graphify/__init__.py", "source_location": "L4", "_callable": true}, {"id": "d_project_assistan_graphify_repo_graphify_init_rationale_1", "label": "graphify - extract \u00b7 build \u00b7 cluster \u00b7 analyze \u00b7 report.", "file_type": "rationale", "source_file": "graphify-repo/graphify/__init__.py", "source_location": "L1"}], "edges": [{"source": "d_project_assistan_graphify_repo_graphify_init_py", "target": "d_project_assistan_graphify_repo_graphify_init_getattr", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/graphify/__init__.py", "source_location": "L4", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_graphify_init_rationale_1", "target": "d_project_assistan_graphify_repo_graphify_init_py", "relation": "rationale_for", "confidence": "EXTRACTED", "source_file": "graphify-repo/graphify/__init__.py", "source_location": "L1", "weight": 1.0}], "raw_calls": [{"caller_nid": "d_project_assistan_graphify_repo_graphify_init_getattr", "callee": "import_module", "is_member_call": true, "source_file": "D:\\Project Assistan\\graphify-repo\\graphify\\__init__.py", "source_location": "L28", "receiver": "importlib"}, {"caller_nid": "d_project_assistan_graphify_repo_graphify_init_getattr", "callee": "AttributeError", "is_member_call": false, "source_file": "D:\\Project Assistan\\graphify-repo\\graphify\\__init__.py", "source_location": "L30", "receiver": null}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
