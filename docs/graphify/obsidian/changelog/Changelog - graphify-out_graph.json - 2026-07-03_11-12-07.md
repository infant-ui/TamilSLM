# Changelog: graphify-out/graph.json
**Date:** 2026-07-03_11-12-07
**Type:** Modified

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/graph.json b/graphify-out/graph.json
index e047359..ae05381 100644
--- a/graphify-out/graph.json
+++ b/graphify-out/graph.json
@@ -251,10 +251,10 @@
       "source_file": "",
       "source_location": "",
       "_origin": "ast",
-      "community": 140,
+      "community": 178,
       "norm_label": "sentencetransformer",
       "id": "sentencetransformer",
-      "community_name": "ChunkResult"
+      "community_name": "BookScanner"
     },
     {
       "label": "embed_chunks()",
@@ -3474,10 +3474,10 @@
       "source_file": "backend/retrieval-service/app/api/schemas.py",
       "source_location": "L1",
       "_origin": "ast",
-      "community": 73,
+      "community": 140,
       "norm_label": "schemas.py",
       "id": "backend_retrieval_service_app_api_schemas",
-      "community_name": "BaseModel"
+      "community_name": "ChunkResult"
     },
     {
       "label": "RetrieveRequest",
@@ -3507,10 +3507,10 @@
       "source_file": "backend/retrieval-service/app/api/schemas.py",
       "source_location": "L38",
       "_origin": "ast",
-      "community": 73,
+      "community": 140,
       "norm_label": "retrieveresponse",
       "id": "backend_retrieval_service_app_api_schemas_retrieveresponse",
-      "community_name": "BaseModel"
+      "community_name": "ChunkResult"
     },
     {
       "label": "FeedbackRequest",
@@ -3518,10 +3518,10 @@
       "source_file": "backend/retrieval-service/app/api/schemas.py",
       "source_location": "L45",
       "_origin": "ast",
-      "community": 73,
+      "community": 262,
       "norm_label": "feedbackrequest",
       "id": "backend_retrieval_service_app_api_schemas_feedbackrequest",
-      "community_name": "BaseModel"
+      "community_name": "main.py"
     },
     {
       "label": "DashboardResponse",
@@ -3529,10 +3529,10 @@
       "source_file": "backend/retrieval-service/app/api/schemas.py",
       "source_location": "L55",
       "_origin": "ast",
-      "community": 73,
+      "community": 262,
       "norm_label": "dashboardresponse",
       "id": "backend_retrieval_service_app_api_schemas_dashboardresponse",
-      "community_name": "BaseModel"
+      "community_name": "main.py"
     },
     {
       "label": "__init__.py",
@@ -3615,7 +3615,7 @@
       "label": "._save_to_history()",
       "file_type": "code",
       "source_file": "backend/retrieval-service/app/evaluation/evaluator.py",
-      "source_location": "L193",
+      "source_location": "L195",
       "_origin": "ast",
       "community": 79,
       "norm_label": "._save_to_history()",
@@ -3626,7 +3626,7 @@
       "label": "._compute_deltas()",
       "file_type": "code",
       "source_file": "backend/retrieval-service/app/evaluation/evaluator.py",
-      "source_location": "L205",
+      "source_location": "L209",
       "_origin": "ast",
       "community": 79,
       "norm_label": "._compute_deltas()",
@@ -3637,7 +3637,7 @@
       "label": "._write_markdown_report()",
       "file_type": "code",
       "source_file": "backend/retrieval-service/app/evaluation/evaluator.py",
-      "source_location": "L221",
+      "source_location": "L225",
       "_origin": "ast",
       "community": 79,
       "norm_label": "._write_markdown_report()",
@@ -3648,7 +3648,7 @@
       "label": "run_auto_evaluation()",
       "file_type": "code",
       "source_file": "backend/retrieval-service/app/evaluation/evaluator.py",
-      "source_location": "L276",
+      "source_location": "L280",
       "_origin": "ast",
       "community": 79,
       "norm_label": "run_auto_evaluation()",
@@ -3681,22 +3681,22 @@
       "label": "Outputs a comprehensive markdown evaluation report.",
       "file_type": "rationale",
       "source_file": "backend/retrieval-service/app/evaluation/evaluator.py",
-      "source_location": "L222",
+      "source_location": "L226",
       "_origin": "ast",
       "community": 79,
       "norm_label": "outputs a comprehensive markdown evaluation report.",
-      "id": "backend_retrieval_service_app_evaluation_evaluator_rationale_222",
+      "id": "backend_retrieval_service_app_evaluation_evaluator_rationale_226",
       "community_name": ".run_evaluation"
     },
     {
       "label": "Standard runner triggered automatically post indexing.",
       "file_type": "rationale",
       "source_file": "backend/retrieval-service/app/evaluation/evaluator.py",
-      "source_location": "L277",
+      "source_location": "L281",
       "_origin": "ast",
       "community": 79,
       "norm_label": "standard runner triggered automatically post indexing.",
-      "id": "backend_retrieval_service_app_evaluation_evaluator_rationale_277",
+      "id": "backend_retrieval_service_app_evaluation_evaluator_rationale_281",
       "community_name": ".run_evaluation"
     },
     {
@@ -3824,7 +3824,7 @@
       "label": "ScanSummary",
       "file_type": "code",
       "source_file": "backend/retrieval-service/app/ingestion/book_scanner.py",
-      "source_location": "L9",
+    # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
