import os
import glob
import re
import json
import sys
import traceback
from collections import defaultdict

# Setup directories
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DOCS_DIR = os.path.join(BASE_DIR, 'docs', 'graphify')
OBSIDIAN_DIR = os.path.join(DOCS_DIR, 'obsidian')
REPORTS_DIR = os.path.join(DOCS_DIR, 'reports')
MERMAID_DIR = os.path.join(DOCS_DIR, 'mermaid')

print(f"[init] BASE_DIR    = {BASE_DIR}")
print(f"[init] OBSIDIAN_DIR = {OBSIDIAN_DIR}")

for d in [OBSIDIAN_DIR, REPORTS_DIR, MERMAID_DIR]:
    os.makedirs(d, exist_ok=True)
    print(f"[init] ensured dir exists: {d}")

# Configuration for static pages
STATIC_PAGES = [
    "Home", "Project Overview", "Vision & Goals", "System Architecture",
    "Folder Structure", "Backend", "Frontend", "APIs", "Database",
    "Authentication", "Configuration", "AI Models", "Model Selection Logic",
    "Generation Service", "OCR Pipeline", "RAG Pipeline", "Embedding Pipeline",
    "Image Generation Pipeline", "Audio Processing", "Video Processing",
    "Training Pipeline", "Dataset Management", "Deployment", "Docker",
    "Environment Variables", "Dependencies", "Third-Party Libraries",
    "Security", "Logging", "Error Handling", "Request Flow", "Data Flow",
    "File Processing Flow", "Component Relationships", "Services", "Utilities",
    "Testing", "CI/CD", "Performance Optimizations", "Roadmap", "TODO",
    "Known Issues", "Future Improvements"
]

# Directories to exclude from the repo walk. Matched against path SEGMENTS,
# not substrings, so a folder like "backend/docs_utils" is not wrongly skipped.
EXCLUDED_DIR_NAMES = {'.venv', 'venv', '.git', 'node_modules', 'docs', '__pycache__'}

# Track generated links to validate later
generated_links = set()
used_links = set()
write_count = 0
write_errors = []


def create_markdown(title, content):
    global write_count
    safe_title = title.replace("/", "-")
    filepath = os.path.join(OBSIDIAN_DIR, f"{safe_title}.md")
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        generated_links.add(title)
        write_count += 1
        print(f"[write] {filepath}")
    except Exception as e:
        write_errors.append((filepath, str(e)))
        print(f"[ERROR] Failed writing {filepath}: {e}")


def parse_project():
    stats = defaultdict(int)
    modules = set()
    dependencies = set()
    python_files = []

    for root, dirs, files in os.walk(BASE_DIR):
        # Exclude by exact path-segment match, not substring
        path_parts = set(os.path.normpath(root).split(os.sep))
        if path_parts & EXCLUDED_DIR_NAMES:
            dirs[:] = []  # don't descend further
            continue

        rel_dir = os.path.relpath(root, BASE_DIR)
        if rel_dir != '.':
            modules.add(rel_dir.split(os.sep)[0])

        for file in files:
            stats['Total Files'] += 1
            ext = os.path.splitext(file)[1]
            stats[f'Extension {ext}'] += 1
            if ext == '.py':
                python_files.append(os.path.join(root, file))
            elif file == 'requirements.txt':
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            if line.strip() and not line.startswith('#'):
                                dependencies.add(line.split('==')[0].strip())
                except Exception as e:
                    print(f"[WARN] Could not read {file} in {root}: {e}")

    print(f"[parse_project] Total files scanned: {stats['Total Files']}")
    print(f"[parse_project] Modules discovered: {sorted(modules)}")
    return stats, modules, python_files, dependencies


def generate_dynamic_pages(modules, python_files):
    for module in modules:
        title = f"Module {module.capitalize()}"
        content = (
            f"# {title}\n\n## Overview\nDocumentation for the `{module}` module.\n\n"
            f"## Internal Components\n- [[System Architecture]]\n- [[Dependencies]]\n\n"
            f"## Mermaid Diagram\n```mermaid\ngraph TD\n    {module} --> Dependencies\n```\n"
        )
        create_markdown(title, content)


def generate_static_pages():
    for page in STATIC_PAGES:
        content = f"""# {page}

## Summary
Overview and documentation for {page}.

## Purpose
To define the architecture and workflow for {page}.

## Responsibilities
- Core logic for {page}
- Interaction with [[System Architecture]]

## Internal Components
- [[Backend]]
- [[Frontend]]
- [[Database]]

## Related Files
- Check dynamically generated module pages.

## Dependencies
- [[Dependencies]]
- [[Third-Party Libraries]]

## Technologies Used
- Python, Node.js, Graphify, Antigravity

## Mermaid Diagram
```mermaid
graph TD
    A[{page}] --> B[System Architecture]
    B --> C[Dependencies]
```

## Important Notes
- Auto-generated via Graphify Documentation Pipeline.

## Related Documentation
- [[Home]]
- [[Project Overview]]
"""
        create_markdown(page, content)


def generate_reports(stats, dependencies):
    report_content = "# Project Statistics\n\n"
    for k, v in stats.items():
        report_content += f"- **{k}**: {v}\n"
    create_markdown("Project Statistics", report_content)

    dep_content = "# Dependency Report\n\n## Libraries\n"
    for dep in dependencies:
        dep_content += f"- {dep}\n"
    create_markdown("Dependency Report", dep_content)

    create_markdown("Architecture Report", "# Architecture Report\n\nAnalyzed through [[System Architecture]].\n")

    stats_path = os.path.join(REPORTS_DIR, 'statistics.json')
    try:
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=4)
        print(f"[write] {stats_path}")
    except Exception as e:
        print(f"[ERROR] Failed writing {stats_path}: {e}")


def validate_links():
    broken_links = []
    link_pattern = re.compile(r'\[\[(.*?)\]\]')

    md_files = glob.glob(os.path.join(OBSIDIAN_DIR, '*.md'))
    print(f"[validate_links] Scanning {len(md_files)} markdown files")

    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            links = link_pattern.findall(content)
            for link in links:
                used_links.add(link)
                if link not in generated_links and not link.startswith("Module "):
                    broken_links.append((os.path.basename(md_file), link))

    validation_report = "# Validation Report\n\n"
    if broken_links:
        validation_report += "## Broken Links\n"
        for source, link in broken_links:
            validation_report += f"- In `{source}`: [[{link}]]\n"
    else:
        validation_report += "## Broken Links\nNone found! All wiki links are valid.\n"

    validation_report += f"\n## Coverage\nTotal Markdown Files Generated: {len(generated_links)}\n"
    create_markdown("Validation Report", validation_report)


def main():
    try:
        print("Parsing project repository...")
        stats, modules, python_files, dependencies = parse_project()

        print("Generating static pages...")
        generate_static_pages()

        print("Generating dynamic module pages...")
        generate_dynamic_pages(modules, python_files)

        print("Generating reports...")
        generate_reports(stats, dependencies)

        print("Validating Obsidian vault...")
        validate_links()

        print("\n" + "=" * 60)
        print(f"Documentation generation complete!")
        print(f"Markdown files written: {write_count}")
        print(f"Output directory: {OBSIDIAN_DIR}")
        if write_errors:
            print(f"Write errors encountered: {len(write_errors)}")
            for path, err in write_errors:
                print(f"  - {path}: {err}")
        print("=" * 60)

    except Exception:
        print("\n[FATAL] Generation crashed before completing. Full traceback:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()