import os
import ast
import sys

def get_imports(directory):
    imports = set()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    try:
                        tree = ast.parse(f.read(), filename=path)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    imports.add(alias.name.split('.')[0])
                            elif isinstance(node, ast.ImportFrom):
                                if node.module and node.level == 0:
                                    imports.add(node.module.split('.')[0])
                    except Exception as e:
                        print(f"Error parsing {path}: {e}")
    return imports

import sysconfig
stdlib = set(sysconfig.get_paths().keys()) # Just to get a rough idea, wait actually sys.stdlib_module_names is available in 3.10+
stdlib_modules = sys.stdlib_module_names if hasattr(sys, 'stdlib_module_names') else set()

for service in ['retrieval-service', 'generation-service']:
    print(f"--- {service} ---")
    service_dir = os.path.join('d:\\Project Assistan\\backend', service)
    all_imports = get_imports(service_dir)
    external = [m for m in all_imports if m not in stdlib_modules and m != 'app' and m != 'image']
    print(sorted(external))
