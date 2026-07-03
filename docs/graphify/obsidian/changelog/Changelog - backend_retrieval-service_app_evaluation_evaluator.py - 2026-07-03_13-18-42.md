# Changelog: backend/retrieval-service/app/evaluation/evaluator.py
**Date:** 2026-07-03_13-18-42
**Type:** Modified

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/backend/retrieval-service/app/evaluation/evaluator.py b/backend/retrieval-service/app/evaluation/evaluator.py
index bae6b58..b5daf92 100644
--- a/backend/retrieval-service/app/evaluation/evaluator.py
+++ b/backend/retrieval-service/app/evaluation/evaluator.py
@@ -186,8 +186,10 @@ class RAGEvaluator:
                         # Sort by timestamp to get the last one
                         history.sort(key=lambda x: x["timestamp"])
                         return history[-1]
-            except Exception:
-                pass
+            except json.JSONDecodeError as e:
+                logger.error(f"Failed to parse history {self.history_file}: {e}. Skipping history comparison.", exc_info=True)
+            except OSError as e:
+                logger.error(f"Failed to read history {self.history_file}: {e}. Skipping history comparison.", exc_info=True)
         return {}
 
     def _save_to_history(self, record: dict):
@@ -196,8 +198,10 @@ class RAGEvaluator:
             try:
                 with open(self.history_file, "r", encoding="utf-8") as f:
                     history = json.load(f)
-            except Exception:
-                pass
+            except json.JSONDecodeError as e:
+                logger.error(f"Failed to parse history {self.history_file}: {e}. Starting fresh history.", exc_info=True)
+            except OSError as e:
+                logger.error(f"Failed to read history {self.history_file}: {e}. Starting fresh history.", exc_info=True)
         history.append(record)
         with open(self.history_file, "w", encoding="utf-8") as f:
             json.dump(history, f, indent=2, ensure_ascii=False)  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Backend]]
- [[Home]]
- [[Changelog Index]]
