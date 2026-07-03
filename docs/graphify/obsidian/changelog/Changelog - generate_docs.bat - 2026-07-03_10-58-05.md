# Changelog: generate_docs.bat
**Date:** 2026-07-03_10-58-05
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/generate_docs.bat b/generate_docs.bat
new file mode 100644
index 0000000..9a37b54
--- /dev/null
+++ b/generate_docs.bat
@@ -0,0 +1,61 @@
+@echo off
+echo Starting full documentation regeneration...
+
+echo.
+echo ============================================
+echo Generating Obsidian Knowledge Base...
+echo ============================================
+python generate_obsidian_kb.py
+if %ERRORLEVEL% neq 0 (
+    echo [ERROR] generate_obsidian_kb.py failed.
+    pause
+    exit /b %ERRORLEVEL%
+)
+
+echo.
+echo ============================================
+echo Running Graphify graph generation...
+echo ============================================
+call .venv\Scripts\activate.bat
+
+echo Running graphify for the entire repository (AST only)...
+graphify update .
+
+echo Generating Graphify Obsidian vault...
+graphify cluster-only . --obsidian --obsidian-dir docs\graphify\obsidian
+
+echo Generating global Callflow HTML...
+graphify export callflow-html --output docs\graphify\html\callflow.html
+
+echo Generating modular graphs...
+:: If the folders exist, create separate graphs for them to avoid size limits
+if exist "backend" (
+    graphify extract backend
+    graphify export callflow-html backend\graphify-out --output docs\graphify\html\backend_callflow.html
+)
+if exist "frontend" (
+    graphify extract frontend
+    graphify export callflow-html frontend\graphify-out --output docs\graphify\html\frontend_callflow.html
+)
+
+copy graphify-out\GRAPH_REPORT.md docs\graphify\reports\ 2>nul
+copy graphify-out\graph.json docs\graphify\graphs\ 2>nul
+
+echo.
+echo ============================================
+echo Generating Changelog Knowledge Base...
+echo ============================================
+python generate_changelog_kb.py
+if %ERRORLEVEL% neq 0 (
+    echo [ERROR] generate_changelog_kb.py failed with exit code %ERRORLEVEL%
+    echo Check the output above for the traceback.
+    pause
+    exit /b %ERRORLEVEL%
+)
+echo Changelog generation complete.
+
+echo.
+echo ============================================
+echo All documentation regenerated successfully!
+echo ============================================
+pause  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Root]]
- [[Home]]
- [[Changelog Index]]
