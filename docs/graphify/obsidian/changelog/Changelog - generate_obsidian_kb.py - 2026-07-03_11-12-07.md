# Changelog: generate_obsidian_kb.py
**Date:** 2026-07-03_11-12-07
**Type:** Modified

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/generate_obsidian_kb.py b/generate_obsidian_kb.py
index 2275b56..624bd93 100644
--- a/generate_obsidian_kb.py
+++ b/generate_obsidian_kb.py
@@ -50,6 +50,25 @@ def create_markdown(title, content):
     global write_count
     safe_title = title.replace("/", "-")
     filepath = os.path.join(OBSIDIAN_DIR, f"{safe_title}.md")
+    
+    manual_content = ""
+    if os.path.exists(filepath):
+        try:
+            with open(filepath, 'r', encoding='utf-8') as f:
+                old_text = f.read()
+                match = re.search(r'<!-- MANUAL:START -->(.*?)<!-- MANUAL:END -->', old_text, re.DOTALL)
+                if match:
+                    manual_content = match.group(1)
+        except Exception:
+            pass
+            
+    manual_block = f"## Manual Notes\n<!-- MANUAL:START -->{manual_content}\n<!-- MANUAL:END -->\n\n"
+    
+    if "## Related Documentation" in content:
+        content = content.replace("## Related Documentation", manual_block + "## Related Documentation")
+    else:
+        content = content.strip() + "\n\n" + manual_block
+        
     try:
         with open(filepath, 'w', encoding='utf-8') as f:
             f.write(content)  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Root]]
- [[Home]]
- [[Changelog Index]]
