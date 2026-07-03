# Changelog: graphify-out/cache/ast/v0.9.5/fe59cea2a3b30397abaded9d871df9cb2030af6f3b66a745f125b0802f8825f3.json
**Date:** 2026-07-03_10-29-56
**Type:** Added

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/graphify-out/cache/ast/v0.9.5/fe59cea2a3b30397abaded9d871df9cb2030af6f3b66a745f125b0802f8825f3.json b/graphify-out/cache/ast/v0.9.5/fe59cea2a3b30397abaded9d871df9cb2030af6f3b66a745f125b0802f8825f3.json
new file mode 100644
index 0000000..0e4f147
--- /dev/null
+++ b/graphify-out/cache/ast/v0.9.5/fe59cea2a3b30397abaded9d871df9cb2030af6f3b66a745f125b0802f8825f3.json
@@ -0,0 +1 @@
+{"nodes": [{"id": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_designview_xaml", "label": "DesignView.xaml", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/xaml_viewmodel/Views/DesignView.xaml", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_designview_usercontrol", "label": "UserControl", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/xaml_viewmodel/Views/DesignView.xaml", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_designview_designview", "label": "DesignView", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/xaml_viewmodel/Views/DesignView.xaml", "source_location": "L1"}, {"id": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_viewmodels_designviewmodel_demo_viewmodels_designviewmodel", "label": "DesignViewModel", "file_type": "code", "source_file": "graphify-repo/tests/fixtures/xaml_viewmodel/ViewModels/DesignViewModel.cs", "source_location": "L3", "metadata": {"namespace": "Demo.ViewModels", "scope_chain": ["s0"]}, "_callable": true}], "edges": [{"source": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_designview_xaml", "target": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_designview_usercontrol", "relation": "contains", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/xaml_viewmodel/Views/DesignView.xaml", "source_location": "L1", "weight": 1.0}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_designview_usercontrol", "target": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_designview_designview", "relation": "references", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/xaml_viewmodel/Views/DesignView.xaml", "source_location": "L1", "weight": 1.0, "context": "x_class"}, {"source": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_views_designview_usercontrol", "target": "d_project_assistan_graphify_repo_tests_fixtures_xaml_viewmodel_viewmodels_designviewmodel_demo_viewmodels_designviewmodel", "relation": "references", "confidence": "EXTRACTED", "source_file": "graphify-repo/tests/fixtures/xaml_viewmodel/Views/DesignView.xaml", "source_location": "L6", "weight": 1.0, "context": "view_model"}]}
\ No newline at end of file  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Graphify-out]]
- [[Home]]
- [[Changelog Index]]
