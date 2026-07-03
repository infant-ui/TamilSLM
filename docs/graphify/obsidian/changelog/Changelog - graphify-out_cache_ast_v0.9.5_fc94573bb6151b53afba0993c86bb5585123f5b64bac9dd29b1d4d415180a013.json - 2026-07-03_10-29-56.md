# Changelog: graphify-out/cache/ast/v0.9.5/fc94573bb6151b53afba0993c86bb5585123f5b64bac9dd29b1d4d415180a013.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/fc94573bb6151b53afba0993c86bb5585123f5b64bac9dd29b1d4d415180a013.json b/graphify-out/cache/ast/v0.9.5/fc94573bb6151b53afba0993c86bb5585123f5b64bac9dd29b1d4d415180a013.json
new file mode 100644
index 0000000..c7f94d4
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/fc94573bb6151b53afba0993c86bb5585123f5b64bac9dd29b1d4d415180a013.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_settingsview_xaml", "label": "SettingsView.xaml", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/xaml_viewmodel/Views/SettingsView.xaml", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_settingsview_usercontrol", "label": "UserControl", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/xaml_viewmodel/Views/SettingsView.xaml", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_settingsview_settingsview", "label": "SettingsView", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/xaml_viewmodel/Views/SettingsView.xaml", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_viewmodels_settingsviewmodel_demo_viewmodels_settingsviewmodel", "label": "SettingsViewModel", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/xaml_viewmodel/ViewModels/SettingsViewModel.cs", "source_location": "L3", "metadata": {"namespace": "Demo.ViewModels", "scope_chain": ["s0"]}, "_callable": true}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_settingsview_xaml", "target": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_settingsview_usercontrol", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/xaml_viewmodel/Views/SettingsView.xaml", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_settingsview_usercontrol", "target": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_settingsview_settingsview", "relation": "references", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/xaml_viewmodel/Views/SettingsView.xaml", "source_location": "L1", "weight": 1.0, "context": "x_class"}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_settingsview_usercontrol", "target": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_viewmodels_settingsviewmodel_demo_viewmodels_settingsviewmodel", "relation": "references", "confidence": "INFERRED", "source_file": "graphify-repo/tests/fixtures/xaml_viewmodel/Views/SettingsView.xaml", "source_location": "L1", "weight": 1.0, "context": "view_model"}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
