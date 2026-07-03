# Changelog: docs/graphify/html/frontend_callflow.html
**Date:** 2026-07-03_13-18-39
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- `+    class BUILD_GRAPH_321CBB04 module;`
- `+    class INGEST_CACHE_UPDATE_FF457338 module;`
- `+    class SERVE_API_35EC8E86 module;`
- `+    class TESTS_FIXTURES_B84B1DCC module;`
- `+    class INDEXJS_REPORTWEBVITALSJS_ROOT_D2DB5670 module;`
- `+    class PROMPTUTILSJS_FEATURES_IMAGE_D6592F87 module;`
- `+    class ADMIN_REVIEW_APPPY_C861DDE8 module;`
- `+    class SETUPTESTSJS_828D6210 module;`
- `+    class package_dependencies_c512ca5e function;`
- `+    class package_582681c2 function;`
- `+    class package_scripts_25cfc1ca function;`
- `+    class package_browserslist_0bdb393c function;`
- `+    class package_eslintconfig_ffa14c10 function;`
- `+    class package_name_b23e1232 function;`
- `+    class package_private_9955bf19 function;`
- `+    class package_version_a7f3cb7e function;`
- `+    class package_dependencies_dagre_2cb67352 function;`
- `+    class package_dependencies_lucide_react_17f0074f function;`
- `+    class package_dependencies_prismjs_ba65545b function;`
- `+    class package_dependencies_react_a04d7d7e function;`
- `+    class package_dependencies_react_dom_87814871 function;`
- `+    class package_dependencies_react_hot_toast_22257a06 function;`
- `+    class package_dependencies_react_markdown_638f7ee8 function;`
- `+    class package_dependencies_react_scripts_0efe107e function;`
- `+    class package_dependencies_reactflow_782bc53d function;`
- `+    class package_dependencies_recharts_303fd7ea function;`
- `+    class public_manifest_388917a5 function;`
- `+    class public_manifest_background_color_5a35b652 function;`
- `+    class public_manifest_display_36ace0b3 function;`
- `+    class public_manifest_icons_8f77cdcc function;`
- `+    class public_manifest_name_15b4c29b function;`
- `+    class public_manifest_short_name_78e974be function;`
- `+    class public_manifest_start_url_8e1f7f7a function;`
- `+    class public_manifest_theme_color_be80c7b7 function;`
- `+    class src_features_image_generation_api_imageapi_94853628 api;`
- `+    class src_features_image_generation_api_imageapi_gener_befc0e01 function;`
- `+    class src_app_46efd68e klass;`
- `+    class src_app_app_f316b20d function;`
- `+    class src_app_rendermessagecontent_bc65dfb5 function;`
- `+    class src_app_messagebubble_0351d1d7 function;`
- `+    class src_app_sourceslist_06dfbb76 function;`
- `+    class src_app_rendermath_feffd621 function;`
- `+    class src_components_mindmapgraph_4223396f klass;`
- `+    class src_components_mindmapgraph_mindmapgraph_9de37b74 function;`
- `+    class src_components_mindmapgraph_dagregraph_4127d068 function;`
- `+    class src_components_mindmapgraph_getlayoutedelements_1f7dccf3 function;`
- `+    class src_app_test_dc8f0460 test;`
- `+    class src_index_811cdc82 module;`
- `+    class src_index_root_73a47705 function;`
- `+    class src_reportwebvitals_efed408c module;`
- `+    class src_reportwebvitals_reportwebvitals_8bc39fb4 function;`
- `+    class src_features_image_generation_utils_promptutils_4caa6c26 module;`
- `+    class src_features_image_generation_utils_promptutils_5a317830 function;`
- `+    class src_features_image_generation_utils_promptutils_590f5e80 function;`
- `+    class admin_review_app_125dfd72 module;`
- `+    class src_setuptests_b9b67ebc test;`

## Diff
```diff
diff --git a/docs/graphify/html/frontend_callflow.html b/docs/graphify/html/frontend_callflow.html
new file mode 100644
index 0000000..e13d99a
--- /dev/null
+++ b/docs/graphify/html/frontend_callflow.html
@@ -0,0 +1,1267 @@
+<!DOCTYPE html>
+<html lang="en">
+<head>
+<meta charset="UTF-8">
+<meta name="viewport" content="width=device-width, initial-scale=1.0">
+<title>frontend — Complete Call Flow &amp; Architecture Documentation</title>
+<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
+<style>
+:root {
+  --bg: #0f172a; --surface: #1e293b; --border: #334155;
+  --text: #e2e8f0; --muted: #94a3b8; --accent: #38bdf8;
+  --warn: #fbbf24; --err: #f87171; --ok: #34d399;
+}
+* { box-sizing: border-box; margin: 0; padding: 0; }
+body { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); line-height: 1.7; }
+.container { max-width: 1200px; margin: 0 auto; padding: 40px 24px; }
+h1 { font-size: 2.4rem; margin-bottom: 8px; background: linear-gradient(135deg, var(--accent), #a78bfa); background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
+h2 { font-size: 1.7rem; margin: 48px 0 16px; padding-bottom: 8px; border-bottom: 2px solid var(--accent); }
+h3 { font-size: 1.25rem; margin: 32px 0 12px; color: var(--accent); }
+h4 { font-size: 1.05rem; margin: 20px 0 8px; color: var(--warn); }
+p { margin: 8px 0; color: var(--muted); }
+.subtitle { color: var(--muted); font-size: 1.1rem; margin-bottom: 32px; }
+.mermaid { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin: 20px 0; overflow-x: auto; position: relative; }
+.mermaid.is-enhanced { padding: 0; overflow: hidden; min-height: 260px; }
+.mermaid-viewport { padding: 54px 24px 24px; overflow: hidden; cursor: grab; touch-action: none; min-height: 260px; }
+.mermaid-viewport.is-dragging { cursor: grabbing; }
+.mermaid-viewport svg { max-width: none !important; height: auto; transform-origin: 0 0; transition: transform 120ms ease; }
+.mermaid-toolbar { position: absolute; top: 10px; right: 10px; z-index: 3; display: flex; align-items: center; gap: 6px; padding: 6px; background: rgba(15,23,42,0.92); border: 1px solid var(--border); border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.28); }
+.mermaid-toolbar button, .mermaid-toolbar .zoom-level { height: 28px; min-width: 32px; border: 1px solid var(--border); border-radius: 6px; background: #1e293b; color: var(--text); font: 600 0.78rem system-ui, sans-serif; display: inline-flex; align-items: center; justify-content: center; }
+.mermaid-toolbar button { cursor: pointer; }
+.mermaid-toolbar button:hover { border-color: var(--accent); color: var(--accent); }
+.mermaid-toolbar .zoom-level { min-width: 52px; color: var(--muted); background: transparent; }
+.call-table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 0.92rem; }
+.call-table th { background: #1a2744; color: var(--accent); text-align: left; padding: 10px 14px; border: 1px solid var(--border); }
+.call-table td { padding: 8px 14px; border: 1px solid var(--border); vertical-align: top; }
+.call-table tr:nth-child(even) { background: rgba(255,255,255,0.02); }
+.tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }
+.tag-async { background: #7c3aed33; color: #a78bfa; }
+.tag-class { background: #05966933; color: var(--ok); }
+.tag-func { background: #2563eb33; color: var(--accent); }
+.tag-cmd { background: #d9770633; color: var(--warn); }
+.tag-endpoint { background: #dc262633; color: var(--err); }
+.tag-hook { background: #db277733; color: #f472b6; }
+.card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px; margin: 16px 0; }
+.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 16px; margin: 16px 0; }
+.arrow-chain { font-family: 'Fira Code', monospace; font-size: 0.85rem; color: var(--accent); padding: 10px; background: rgba(56,189,248,0.06); border-radius: 6px; }
+code { font-family: 'Fira Code', 'Cascadia Code', monospace; background: rgba(255,255,255,0.06); padding: 1px 6px; border-radius: 3px; font-size: 0.88em; }
+ul, ol { margin: 8px 0 8px 24px; color: var(--muted); }
+li { margin: 4px 0; }
+a { color: var(--accent); }
+hr { border: none; border-top: 1px solid var(--border); margin: 40px 0; }
+.nav { position: sticky; top: 0; background: var(--bg); z-index: 10; padding: 12px 0; border-bottom: 1px solid var(--border); display: flex; gap: 20px; flex-wrap: wrap; font-size: 0.9rem; }
+.nav a { text-decoration: none; }
+.nav a:hover { text-decoration: underline; }
+@media (max-width: 768px) { .container { padding: 16px; } h1 { font-size: 1.8rem; } }
+
+</style>
+</head>
+<body>
+<div class="container">
+
+<h1>frontend — Complete Call Flow &amp; Architecture Documentation</h1>
+<p class="subtitle">Generated from graphify knowledge gra  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Docs]]
- [[Home]]
- [[Changelog Index]]
