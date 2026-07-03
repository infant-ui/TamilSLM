# Changelog: graphify-out/GRAPH_REPORT.md
**Date:** 2026-07-03_10-58-05
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/GRAPH_REPORT.md b/graphify-out/GRAPH_REPORT.md
new file mode 100644
index 0000000..e83f152
--- /dev/null
+++ b/graphify-out/GRAPH_REPORT.md
@@ -0,0 +1,2643 @@
+# Graph Report - .  (2026-07-02)
+
+## Corpus Check
+- cluster-only mode — file stats not available
+
+## Summary
+- 8221 nodes · 14564 edges · 686 communities (556 shown, 130 thin omitted)
+- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 2523 edges (avg confidence: 0.77)
+- Token cost: 0 input · 0 output
+
+## Graph Freshness
+- Built from commit: `e3fcec2d`
+- Run `git rev-parse HEAD` and compare to check if the graph is stale.
+- Run `graphify update .` after code changes (no API cost).
+
+## Community Hubs (Navigation)
+- [[_COMMUNITY_classify_file|classify_file]]
+- [[_COMMUNITY_test_extract.py|test_extract.py]]
+- [[_COMMUNITY_extract.py|extract.py]]
+- [[_COMMUNITY_extract_dart|extract_dart]]
+- [[_COMMUNITY_test_install.py|test_install.py]]
+- [[_COMMUNITY___main__.py|__main__.py]]
+- [[_COMMUNITY__edges_with_relation|_edges_with_relation]]
+- [[_COMMUNITY_test_import_extension_resolution.py|test_import_extension_resolution.py]]
+- [[_COMMUNITY_test_multilang.py|test_multilang.py]]
+- [[_COMMUNITY_test_mcp_ingest.py|test_mcp_ingest.py]]
+- [[_COMMUNITY_Path|Path]]
+- [[_COMMUNITY_test_dotnet.py|test_dotnet.py]]
+- [[_COMMUNITY_test_codebuddy.py|test_codebuddy.py]]
+- [[_COMMUNITY_to_wiki|to_wiki]]
+- [[_COMMUNITY_llm.py|llm.py]]
+- [[_COMMUNITY_test_detect.py|test_detect.py]]
+- [[_COMMUNITY_test_js_import_resolution.py|test_js_import_resolution.py]]
+- [[_COMMUNITY_test_serve.py|test_serve.py]]
+- [[_COMMUNITY_test_build.py|test_build.py]]
+- [[_COMMUNITY__labels|_labels]]
+- [[_COMMUNITY_extract_js|extract_js]]
+- [[_COMMUNITY_gemini_install|gemini_install]]
+- [[_COMMUNITY_Graph|Graph]]
+- [[_COMMUNITY_detect.py|detect.py]]
+- [[_COMMUNITY_test_pascal.py|test_pascal.py]]
+- [[_COMMUNITY_test_multigraph_diagnostics.py|test_multigraph_diagnostics.py]]
+- [[_COMMUNITY_test_reflect.py|test_reflect.py]]
+- [[_COMMUNITY_process_book_pipeline|process_book_pipeline]]
+- [[_COMMUNITY_test_chunking.py|test_chunking.py]]
+- [[_COMMUNITY__file_stem|_file_stem]]
+- [[_COMMUNITY_extract|extract]]
+- [[_COMMUNITY_test_devin.py|test_devin.py]]
+- [[_COMMUNITY_reflect.py|reflect.py]]
+- [[_COMMUNITY_deduplicate_entities|deduplicate_entities]]
+- [[_COMMUNITY_serve.py|serve.py]]
+- [[_COMMUNITY_test_global_graph.py|test_global_graph.py]]
+- [[_COMMUNITY_scip_ingest.py|scip_ingest.py]]
+- [[_COMMUNITY_test_security.py|test_security.py]]
+- [[_COMMUNITY_test_semantic_cleanup.py|test_semantic_cleanup.py]]
+- [[_COMMUNITY_extract_objc|extract_objc]]
+- [[_COMMUNITY_extract_python|extract_python]]
+- [[_COMMUNITY__make_graph|_make_graph]]
+- [[_COMMUNITY_test_cli_export.py|test_cli_export.py]]
+- [[_COMMUNITY_test_indirect_dispatch.py|test_indirect_dispatch.py]]
+- [[_COMMUNITY__edge_labels|_edge_labels]]
+- [[_COMMUNITY_validate_extraction|validate_extraction]]
+- [[_COMMUNITY_ingest_scip_json|ingest_scip_json]]
+- [[_COMMUNITY_sample.swift|sample.swift]]
+- [[_COMMUNITY_FileSlice|FileSlice]]
+- [[_COMMUNITY_test_install_references.py|test_install_references.py]]
+- [[_COMMUNITY_test_transcribe.py|test_transcribe.py]]
+- [[_COMMUNITY_extract_json|extract_json]]
+- [[_COMMUNITY_LayoutBlock|LayoutBlock]]
+- [[_COMMUNITY_test_watch.py|test_watch.py]]
+- [[_COMMUNITY_Auth|Auth]]
+- [[_COMMUNITY_test_labeling.py|test_labeling.py]]
+- [[_COMMUNITY_test_scip_ingest.py|test_scip_ingest.py]]
+- [[_COMMUNITY_Response|Response]]
+- [[_COMMUNITY_exceptions.py|exceptions.py]]
+- [[_COMMUNITY_test_benchmark.py|test_benchmark.py]]
+- [[_COMMUNITY_test_export.py|test_export.py]]
+- [[_COMMUNITY_BaseClient|BaseClient]]
+- [[_COMMUNITY_test_hooks.py|test_hooks.py]]
+- [[_COMMUNITY_test_serve_http.py|test_serve_http.py]]
+- [[_COMMUNITY_Request|Request]]
+- [[_COMMUNITY_HttpClient|HttpClient]]
+- [[_COMMUNITY_dedup.py|dedup.py]]
+- [[_COMMUNITY_manifest_ingest.py|manifest_ingest.py]]
+- [[_COMMUNITY__rebuild_code|_rebuild_code]]
+- [[_COMMUNITY_app.py|app.py]]
+- [[_COMMUNITY_build.py|build.py]]
+- [[_COMMUNITY__ImageRef|_ImageRef]]
+- [[_COMMUNITY_test_minhash.py|test_minhash.py]]
+- [[_COMMUNITY_BaseModel|BaseModel]]
+- [[_COMMUNITY_cache_dir|cache_dir]]
+- [[_COMMUNITY_TestSubprocessEncoding|TestSubprocessEncoding]]
+- [[_COMMUNITY_write_callflow_html|write_callflow_html]]
+- [[_COMMUNITY__extract_generic|_extract_generic]]
+- [[_COMMUNITY__platform_artifacts|_platform_artifacts]]
+- [[_COMMUNITY_.run_evaluation|.run_evaluation]]
+- [[_COMMUNITY_analyze.py|analyze.py]]
+- [[_COMMUNITY_cluster.py|cluster.py]]
+- [[_COMMUNITY_load_manifest|load_manifest]]
+- [[_COMMUNITY__relations|_relations]]
+- [[_COMMUNITY_claude_install|claude_install]]
+- [[_COMMUNITY_test_claude_cli_backend.py|test_claude_cli_backend.py]]
+- [[_COMMUNITY_test_image_vision.py|test_image_vision.py]]
+- [[_COMMUNITY_test_install_roundtrip.py|test_install_roundt  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
