# Changelog: docs/graphify/reports/GRAPH_REPORT.md
**Date:** 2026-07-03_13-18-39
**Type:** Modified

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/docs/graphify/reports/GRAPH_REPORT.md b/docs/graphify/reports/GRAPH_REPORT.md
index e83f152..f582f1f 100644
--- a/docs/graphify/reports/GRAPH_REPORT.md
+++ b/docs/graphify/reports/GRAPH_REPORT.md
@@ -1,22 +1,22 @@
-# Graph Report - .  (2026-07-02)
+# Graph Report - .  (2026-07-03)
 
 ## Corpus Check
 - cluster-only mode — file stats not available
 
 ## Summary
-- 8221 nodes · 14564 edges · 686 communities (556 shown, 130 thin omitted)
-- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 2523 edges (avg confidence: 0.77)
+- 8249 nodes · 14612 edges · 679 communities (557 shown, 122 thin omitted)
+- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 2526 edges (avg confidence: 0.77)
 - Token cost: 0 input · 0 output
 
 ## Graph Freshness
-- Built from commit: `e3fcec2d`
+- Built from commit: `dcf0a782`
 - Run `git rev-parse HEAD` and compare to check if the graph is stale.
 - Run `graphify update .` after code changes (no API cost).
 
 ## Community Hubs (Navigation)
 - [[_COMMUNITY_classify_file|classify_file]]
 - [[_COMMUNITY_test_extract.py|test_extract.py]]
-- [[_COMMUNITY_extract.py|extract.py]]
+- [[_COMMUNITY__read_text|_read_text]]
 - [[_COMMUNITY_extract_dart|extract_dart]]
 - [[_COMMUNITY_test_install.py|test_install.py]]
 - [[_COMMUNITY___main__.py|__main__.py]]
@@ -24,18 +24,18 @@
 - [[_COMMUNITY_test_import_extension_resolution.py|test_import_extension_resolution.py]]
 - [[_COMMUNITY_test_multilang.py|test_multilang.py]]
 - [[_COMMUNITY_test_mcp_ingest.py|test_mcp_ingest.py]]
-- [[_COMMUNITY_Path|Path]]
+- [[_COMMUNITY_extract.py|extract.py]]
 - [[_COMMUNITY_test_dotnet.py|test_dotnet.py]]
 - [[_COMMUNITY_test_codebuddy.py|test_codebuddy.py]]
 - [[_COMMUNITY_to_wiki|to_wiki]]
 - [[_COMMUNITY_llm.py|llm.py]]
 - [[_COMMUNITY_test_detect.py|test_detect.py]]
 - [[_COMMUNITY_test_js_import_resolution.py|test_js_import_resolution.py]]
-- [[_COMMUNITY_test_serve.py|test_serve.py]]
+- [[_COMMUNITY__find_node|_find_node]]
 - [[_COMMUNITY_test_build.py|test_build.py]]
 - [[_COMMUNITY__labels|_labels]]
 - [[_COMMUNITY_extract_js|extract_js]]
-- [[_COMMUNITY_gemini_install|gemini_install]]
+- [[_COMMUNITY__get_extractor|_get_extractor]]
 - [[_COMMUNITY_Graph|Graph]]
 - [[_COMMUNITY_detect.py|detect.py]]
 - [[_COMMUNITY_test_pascal.py|test_pascal.py]]
@@ -55,7 +55,7 @@
 - [[_COMMUNITY_test_semantic_cleanup.py|test_semantic_cleanup.py]]
 - [[_COMMUNITY_extract_objc|extract_objc]]
 - [[_COMMUNITY_extract_python|extract_python]]
-- [[_COMMUNITY__make_graph|_make_graph]]
+- [[_COMMUNITY_test_serve.py|test_serve.py]]
 - [[_COMMUNITY_test_cli_export.py|test_cli_export.py]]
 - [[_COMMUNITY_test_indirect_dispatch.py|test_indirect_dispatch.py]]
 - [[_COMMUNITY__edge_labels|_edge_labels]]
@@ -65,7 +65,7 @@
 - [[_COMMUNITY_FileSlice|FileSlice]]
 - [[_COMMUNITY_test_install_references.py|test_install_references.py]]
 - [[_COMMUNITY_test_transcribe.py|test_transcribe.py]]
-- [[_COMMUNITY_extract_json|extract_json]]
+- [[_COMMUNITY_extract_csharp|extract_csharp]]
 - [[_COMMUNITY_LayoutBlock|LayoutBlock]]
 - [[_COMMUNITY_test_watch.py|test_watch.py]]
 - [[_COMMUNITY_Auth|Auth]]
@@ -167,7 +167,7 @@
 - [[_COMMUNITY_sample.ps1|sample.ps1]]
 - [[_COMMUNITY_callflow_html.py|callflow_html.py]]
 - [[_COMMUNITY_backup_if_protected|backup_if_protected]]
-- [[_COMMUNITY__extract_pascal_regex|_extract_pascal_regex]]
+- [[_COMMUNITY_test_terraform.py|test_terraform.py]]
 - [[_COMMUNITY_Platform|Platform]]
 - [[_COMMUNITY_utils.py|utils.py]]
 - [[_COMMUNITY_sample.php|sample.php]]
@@ -186,7 +186,7 @@
 - [[_COMMUNITY_Window|Window]]
 - [[_COMMUNITY_test_languages.py|test_languages.py]]
 - [[_COMMUNITY_save_cached|save_cached]]
-- [[_COMMUNITY_extract_groovy|extract_groovy]]
+- [[_COMMUNITY__query_terms|_query_terms]]
 - [[_COMMUNITY_extract_powershell_manifest|extract_powershell_manifest]]
 - [[_COMMUNITY_paths.py|paths.py]]
 - [[_COMMUNITY_test_confidence.py|test_confidence.py]]
@@ -223,7 +223,7 @@
 - [[_COMMUNITY_DataProcessor|DataProcessor]]
 - [[_COMMUNITY_sample.go|sample.go]]
 - [[_COMMUNITY_affected.py|affected.py]]
-- [[_COMMUNITY_collect_files|collect_files]]
+- [[_COMMUNITY_PDFCleaner|PDFCleaner]]
 - [[_COMMUNITY_test_install_strings.py|test_install_strings.py]]
 - [[_COMMUNITY_sample.dmf|sample.dmf]]
 - [[_COMMUNITY_safe_fetch|safe_fetch]]
@@ -253,7 +253,7 @@
 - [[_COMMUNITY_main|main]]
 - [[_COMMUNITY_app.py|app.py]]
 - [[_COMMUNITY_knn_graph.py|knn_graph.py]]
-- [[_COMMUNITY_to_json|to_json]]
+- [[_COMMUNITY_generate_changelog_kb.py|generate_changelog_kb.py]]
 - [[_COMMUNITY_push_to_falkordb|push_to_falkordb]]
 - [[_COMMUNITY__resolve_cross_file_csharp_imports|_resolve_cross_file_csharp_imports]]
 - [[_COMMUNITY_load_memory_docs|load_memory_docs]]
@@ -276,12 +276,12 @@
 - [[_COMMUNITY_sample_calls.py|sample_calls.py]]
 - [[_COMMUNITY_test_callflow_html.py|test_callflow_html.py]]
 - [[_COMMUNITY_corrections_db.py|corrections_db.py]]
-- [[_COMMUNITY_get_hardware_level|get_hardware  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Docs]]
- [[Home]]
- [[Changelog Index]]
