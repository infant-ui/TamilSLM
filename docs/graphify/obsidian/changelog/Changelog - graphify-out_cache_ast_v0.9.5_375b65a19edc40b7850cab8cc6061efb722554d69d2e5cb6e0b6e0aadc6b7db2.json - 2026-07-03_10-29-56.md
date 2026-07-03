# Changelog: graphify-out/cache/ast/v0.9.5/375b65a19edc40b7850cab8cc6061efb722554d69d2e5cb6e0b6e0aadc6b7db2.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/375b65a19edc40b7850cab8cc6061efb722554d69d2e5cb6e0b6e0aadc6b7db2.json b/graphify-out/cache/ast/v0.9.5/375b65a19edc40b7850cab8cc6061efb722554d69d2e5cb6e0b6e0aadc6b7db2.json
new file mode 100644
index 0000000..da5a28a
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/375b65a19edc40b7850cab8cc6061efb722554d69d2e5cb6e0b6e0aadc6b7db2.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_prismorderview_xaml", "label": "PrismOrderView.xaml", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/xaml_viewmodel/Views/PrismOrderView.xaml", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_prismorderview_usercontrol", "label": "UserControl", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/xaml_viewmodel/Views/PrismOrderView.xaml", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_viewmodels_prismorderviewmodel_demo_viewmodels_prismorderviewmodel", "label": "PrismOrderViewModel", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/xaml_viewmodel/ViewModels/PrismOrderViewModel.cs", "source_location": "L3", "metadata": {"namespace": "Demo.ViewModels", "scope_chain": ["s0"]}, "_callable": true}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_prismorderview_xaml", "target": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_prismorderview_usercontrol", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/xaml_viewmodel/Views/PrismOrderView.xaml", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_prismorderview_usercontrol", "target": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_viewmodels_prismorderviewmodel_demo_viewmodels_prismorderviewmodel", "relation": "references", "confidence": "INFERRED", "source_file": "graphify-repo/tests/fixtures/xaml_viewmodel/Views/PrismOrderView.xaml", "source_location": "L1", "weight": 1.0, "context": "view_model"}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
