import os
import sys
import json
import subprocess
import hashlib
import re
from datetime import datetime
from collections import defaultdict

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DOCS_DIR = os.path.join(BASE_DIR, 'docs', 'graphify')
OBSIDIAN_DIR = os.path.join(DOCS_DIR, 'obsidian')
CHANGELOG_DIR = os.path.join(OBSIDIAN_DIR, 'changelog')
SNAPSHOT_FILE = os.path.join(DOCS_DIR, '.snapshot.json')
INDEX_FILE = os.path.join(OBSIDIAN_DIR, 'Changelog Index.md')

# Ensure directories exist
os.makedirs(CHANGELOG_DIR, exist_ok=True)

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore')
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def is_git_repo():
    return run_cmd(['git', 'rev-parse', '--is-inside-work-tree']) == 'true'

def get_current_git_commit():
    return run_cmd(['git', 'rev-parse', 'HEAD'])

def get_tracked_files_git():
    out = run_cmd(['git', 'ls-files'])
    return out.split('\n') if out else []

def get_file_hashes():
    hashes = {}
    for root, dirs, files in os.walk(BASE_DIR):
        if '.venv' in root or '.git' in root or 'node_modules' in root or 'docs' in root:
            continue
        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, BASE_DIR)
            try:
                with open(filepath, 'rb') as f:
                    hashes[rel_path] = hashlib.sha256(f.read()).hexdigest()
            except Exception:
                pass
    return hashes

def extract_signature_changes(diff_text):
    changes = []
    # Best-effort regex for functions/classes
    func_regex = re.compile(r'^[+-]\s*(def\s+\w+\(.*?\):|class\s+\w+.*?|import\s+.*|from\s+.*?\s+import\s+.*)')
    for line in diff_text.split('\n'):
        if func_regex.match(line):
            changes.append(line)
    return changes

def infer_category(filepath):
    parts = filepath.split('/')
    if len(parts) > 1:
        return parts[0].capitalize()
    return "Root"

def process_git_changes(last_commit):
    print(f"Comparing working tree against commit: {last_commit}")
    # Get added/modified/deleted files
    status_out = run_cmd(['git', 'diff', '--name-status', last_commit])
    if not status_out:
        return []

    changes = []
    for line in status_out.split('\n'):
        if not line.strip(): continue
        parts = line.split('\t')
        status = parts[0]
        filepath = parts[1]
        
        # Get diff for this file
        diff_text = run_cmd(['git', 'diff', last_commit, '--', filepath]) or ""
        
        change_type = "Modified"
        if status.startswith('A'): change_type = "Added"
        elif status.startswith('D'): change_type = "Removed"
        
        changes.append({
            'filepath': filepath,
            'type': change_type,
            'diff': diff_text,
            'category': infer_category(filepath)
        })
    return changes

def process_hash_changes(last_hashes, current_hashes):
    print("Comparing current file hashes against stored snapshot...")
    changes = []
    all_files = set(last_hashes.keys()).union(set(current_hashes.keys()))
    
    for filepath in all_files:
        old_h = last_hashes.get(filepath)
        new_h = current_hashes.get(filepath)
        
        if old_h == new_h:
            continue
            
        change_type = "Modified"
        if not old_h: change_type = "Added"
        elif not new_h: change_type = "Removed"
        
        # Fallback diff generation (limited context if file is removed)
        diff_text = ""
        if change_type in ["Added", "Modified"]:
            abs_path = os.path.join(BASE_DIR, filepath)
            try:
                with open(abs_path, 'r', encoding='utf-8') as f:
                    diff_text = f"--- /dev/null\n+++ b/{filepath}\n@@ Full File Dump @@\n" + f.read()
            except Exception:
                diff_text = "(Unable to read file content)"
        else:
            diff_text = "(File removed, content unavailable without Git)"

        changes.append({
            'filepath': filepath,
            'type': change_type,
            'diff': diff_text,
            'category': infer_category(filepath)
        })
    return changes

def generate_markdown(change, date_str):
    safe_name = change['filepath'].replace('/', '_').replace('\\', '_')
    filename = f"Changelog - {safe_name} - {date_str}.md"
    filepath = os.path.join(CHANGELOG_DIR, filename)
    
    sigs = extract_signature_changes(change['diff'])
    sig_text = "\n".join([f"- `{s.strip()}`" for s in sigs]) if sigs else "- None detected"
    
    content = f"""# Changelog: {change['filepath']}
**Date:** {date_str}
**Type:** {change['type']}

## Summary of Changes
### Structural Changes Detected (Best-Effort)
{sig_text}

## Diff
```diff
{change['diff'][:5000]}  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[{change['category']}]]
- [[Home]]
- [[Changelog Index]]
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Generated: {filename}")
    return filename

def update_index(changes_by_cat, date_str):
    print("Updating Changelog Index...")
    
    # Read existing content if any
    existing_content = ""
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            existing_content = f.read()
            
    # Prepare new entries grouped by date, then category
    new_entries = f"## {date_str}\n"
    for cat, items in changes_by_cat.items():
        new_entries += f"### {cat}\n"
        for item in items:
            # Drop the .md extension for obsidian links
            link_name = item['filename'].replace('.md', '')
            new_entries += f"- [[{link_name}]] ({item['type']}: `{item['filepath']}`)\n"
    new_entries += "\n"
    
    # Prepend new entries below the title
    if existing_content.startswith("# Changelog Index"):
        updated_content = existing_content.replace("# Changelog Index\n", f"# Changelog Index\n\n{new_entries}")
    else:
        updated_content = f"# Changelog Index\n\n{new_entries}{existing_content}"
        
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(updated_content)

def main():
    print("Starting Changelog Knowledge Base Generation...")
    has_git = is_git_repo()
    current_commit = get_current_git_commit() if has_git else None
    current_hashes = get_file_hashes() if not has_git else {}
    
    snapshot_data = {}
    if os.path.exists(SNAPSHOT_FILE):
        try:
            with open(SNAPSHOT_FILE, 'r') as f:
                snapshot_data = json.load(f)
        except Exception as e:
            print(f"Failed to load snapshot: {e}")
            
    # Baseline Check
    if not snapshot_data:
        print("No snapshot found. Establishing initial baseline...")
        new_snapshot = {'type': 'git', 'commit': current_commit} if has_git else {'type': 'hash', 'hashes': current_hashes}
        with open(SNAPSHOT_FILE, 'w') as f:
            json.dump(new_snapshot, f, indent=2)
        print(f"Baseline established. Run this script again after making changes to generate changelogs.")
        
        # Create initial index
        if not os.path.exists(INDEX_FILE):
            with open(INDEX_FILE, 'w', encoding='utf-8') as f:
                f.write("# Changelog Index\n\n_No changes tracked yet._\n")
        return

    # Process changes
    if snapshot_data.get('type') == 'git' and has_git:
        changes = process_git_changes(snapshot_data['commit'])
    else:
        changes = process_hash_changes(snapshot_data.get('hashes', {}), current_hashes)
        
    if not changes:
        print("No changes detected since last snapshot.")
        return
        
    print(f"Detected {len(changes)} changed files.")
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    changes_by_cat = defaultdict(list)
    for c in changes:
        fname = generate_markdown(c, date_str)
        changes_by_cat[c['category']].append({'filename': fname, 'filepath': c['filepath'], 'type': c['type']})
        
    update_index(changes_by_cat, date_str)
    
    # Update snapshot for next run
    print("Updating snapshot.json for future runs...")
    new_snapshot = {'type': 'git', 'commit': current_commit} if has_git else {'type': 'hash', 'hashes': current_hashes}
    with open(SNAPSHOT_FILE, 'w') as f:
        json.dump(new_snapshot, f, indent=2)
        
    print("Changelog generation complete!")

if __name__ == '__main__':
    main()
