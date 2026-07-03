# Changelog: generate_obsidian_kb.py
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- `+import os`
- `+import glob`
- `+import re`
- `+import json`
- `+import sys`
- `+import traceback`
- `+from collections import defaultdict`
- `+def create_markdown(title, content):`
- `+def parse_project():`
- `+def generate_dynamic_pages(modules, python_files):`
- `+def generate_static_pages():`
- `+def generate_reports(stats, dependencies):`
- `+def validate_links():`
- `+def main():`

## Diff
```diff
diff --git a/generate_obsidian_kb.py b/generate_obsidian_kb.py
new file mode 100644
index 0000000..2275b56
--- /dev/null
+++ b/generate_obsidian_kb.py
@@ -0,0 +1,242 @@
+import os
+import glob
+import re
+import json
+import sys
+import traceback
+from collections import defaultdict
+
+# Setup directories
+BASE_DIR = os.path.abspath(os.path.dirname(__file__))
+DOCS_DIR = os.path.join(BASE_DIR, 'docs', 'graphify')
+OBSIDIAN_DIR = os.path.join(DOCS_DIR, 'obsidian')
+REPORTS_DIR = os.path.join(DOCS_DIR, 'reports')
+MERMAID_DIR = os.path.join(DOCS_DIR, 'mermaid')
+
+print(f"[init] BASE_DIR    = {BASE_DIR}")
+print(f"[init] OBSIDIAN_DIR = {OBSIDIAN_DIR}")
+
+for d in [OBSIDIAN_DIR, REPORTS_DIR, MERMAID_DIR]:
+    os.makedirs(d, exist_ok=True)
+    print(f"[init] ensured dir exists: {d}")
+
+# Configuration for static pages
+STATIC_PAGES = [
+    "Home", "Project Overview", "Vision & Goals", "System Architecture",
+    "Folder Structure", "Backend", "Frontend", "APIs", "Database",
+    "Authentication", "Configuration", "AI Models", "Model Selection Logic",
+    "Generation Service", "OCR Pipeline", "RAG Pipeline", "Embedding Pipeline",
+    "Image Generation Pipeline", "Audio Processing", "Video Processing",
+    "Training Pipeline", "Dataset Management", "Deployment", "Docker",
+    "Environment Variables", "Dependencies", "Third-Party Libraries",
+    "Security", "Logging", "Error Handling", "Request Flow", "Data Flow",
+    "File Processing Flow", "Component Relationships", "Services", "Utilities",
+    "Testing", "CI/CD", "Performance Optimizations", "Roadmap", "TODO",
+    "Known Issues", "Future Improvements"
+]
+
+# Directories to exclude from the repo walk. Matched against path SEGMENTS,
+# not substrings, so a folder like "backend/docs_utils" is not wrongly skipped.
+EXCLUDED_DIR_NAMES = {'.venv', 'venv', '.git', 'node_modules', 'docs', '__pycache__'}
+
+# Track generated links to validate later
+generated_links = set()
+used_links = set()
+write_count = 0
+write_errors = []
+
+
+def create_markdown(title, content):
+    global write_count
+    safe_title = title.replace("/", "-")
+    filepath = os.path.join(OBSIDIAN_DIR, f"{safe_title}.md")
+    try:
+        with open(filepath, 'w', encoding='utf-8') as f:
+            f.write(content)
+        generated_links.add(title)
+        write_count += 1
+        print(f"[write] {filepath}")
+    except Exception as e:
+        write_errors.append((filepath, str(e)))
+        print(f"[ERROR] Failed writing {filepath}: {e}")
+
+
+def parse_project():
+    stats = defaultdict(int)
+    modules = set()
+    dependencies = set()
+    python_files = []
+
+    for root, dirs, files in os.walk(BASE_DIR):
+        # Exclude by exact path-segment match, not substring
+        path_parts = set(os.path.normpath(root).split(os.sep))
+        if path_parts & EXCLUDED_DIR_NAMES:
+            dirs[:] = []  # don't descend further
+            continue
+
+        rel_dir = os.path.relpath(root, BASE_DIR)
+        if rel_dir != '.':
+            modules.add(rel_dir.split(os.sep)[0])
+
+        for file in files:
+            stats['Total Files'] += 1
+            ext = os.path.splitext(file)[1]
+            stats[f'Extension {ext}'] += 1
+            if ext == '.py':
+                python_files.append(os.path.join(root, file))
+            elif file == 'requirements.txt':
+                try:
+                    with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
+                        for line in f:
+                            if line.strip() and not line.startswith('#'):
+                                dependencies.add(line.split('==')[0].strip())
+                except Exception as e:
+                    print(f"[WARN] Could not read {file} in {root}: {e}")
+
+    print(f"[parse_project] Total files scanned: {stats['Total Files']}")
+    print(f"[parse_project] Modules discovered: {sorted(modules)}")
+    return stats, modules, python_files, dependencies
+
+
+def generate_dynamic_pages(modules, python_files):
+    for module in modules:
+        title = f"Module {module.capitalize()}"
+        content = (
+            f"# {title}\n\n## Overview\nDocumentation for the `{module}` module.\n\n"
+            f"## Internal Components\n- [[System Architecture]]\n- [[Dependencies]]\n\n"
+            f"## Mermaid Diagram\n```mermaid\ngraph TD\n    {module} --> Dependencies\n```\n"
+        )
+        create_markdown(title, content)
+
+
+def generate_static_pages():
+    for page in STATIC_PAGES:
+        content = f"""# {page}
+
+## Summary
+Overview and documentation for {page}.
+
+## Purpose
+To define the architecture and workflow for {page}.
+
+## Responsibilities
+- Core logic for {page}
+- Interaction with [[System Architecture]]
+
+## Internal Components
+- [[Backend]]
+- [[Frontend]]
+- [[Database]]
+
+## Related Files
+- Check dynamically generated module pages.
+
+## Dependencies
+- [[Dependencies]]
+- [[Third-Party Libraries]]
+
+  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Root]]
- [[Home]]
- [[Changelog Index]]
