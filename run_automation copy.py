import os
import time
import subprocess
import threading

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

KB_DEBOUNCE_SECONDS = 5
CHANGELOG_MAX_INTERVAL = 15 * 60  # 15 minutes

def get_current_git_commit():
    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=BASE_DIR, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception:
        return None

def scan_for_latest_mtime():
    """Returns the latest modification time of any tracked source file."""
    latest_mtime = 0
    for root, dirs, files in os.walk(BASE_DIR):
        path_parts = set(os.path.normpath(root).split(os.sep))
        if path_parts & {'.venv', 'venv', '.git', 'node_modules', 'docs', '__pycache__'}:
            dirs[:] = []
            continue
            
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in ['.py', '.js', '.ts', '.json', '.html', '.css', '.md']:
                filepath = os.path.join(root, file)
                try:
                    mtime = os.stat(filepath).st_mtime
                    if mtime > latest_mtime:
                        latest_mtime = mtime
                except Exception:
                    pass
    return latest_mtime

def run_kb_generator():
    print("\n[kb] File change detected, regenerating KB...")
    try:
        subprocess.run(['python', 'generate_obsidian_kb.py'], cwd=BASE_DIR)
    except Exception as e:
        print(f"[kb] ERROR running generate_obsidian_kb.py: {e}")

def run_changelog_generator(reason):
    print(f"\n[changelog] {reason}, generating changelog...")
    try:
        subprocess.run(['python', 'generate_changelog_kb.py'], cwd=BASE_DIR)
    except Exception as e:
        print(f"[changelog] ERROR running generate_changelog_kb.py: {e}")

def watcher_loop():
    print("============================================")
    print("   Antigravity Docs Automation Pipeline     ")
    print("============================================")
    print(f"- Watching {BASE_DIR}")
    print(f"- KB Regen Debounce: {KB_DEBOUNCE_SECONDS}s")
    print(f"- Changelog Triggers: Git Commits or {CHANGELOG_MAX_INTERVAL // 60}m rolling interval")
    print("============================================\n")

    last_known_mtime = scan_for_latest_mtime()
    last_event_time = 0
    kb_trigger_pending = False
    
    last_known_commit = get_current_git_commit()
    last_changelog_run = time.time()
    untracked_activity = False

    while True:
        time.sleep(1)
        
        # 1. Check for file changes
        current_mtime = scan_for_latest_mtime()
        if current_mtime > last_known_mtime:
            last_known_mtime = current_mtime
            last_event_time = time.time()
            kb_trigger_pending = True
            untracked_activity = True
            
        # 2. Trigger A: KB Debounce Execution
        if kb_trigger_pending and (time.time() - last_event_time) >= KB_DEBOUNCE_SECONDS:
            run_kb_generator()
            kb_trigger_pending = False

        # 3. Trigger B: Changelog Generation (Git Commit)
        current_commit = get_current_git_commit()
        if current_commit and current_commit != last_known_commit:
            last_known_commit = current_commit
            run_changelog_generator("New commit detected")
            last_changelog_run = time.time()
            untracked_activity = False
            
        # 4. Trigger B: Changelog Generation (Time Interval)
        elif untracked_activity and (time.time() - last_changelog_run) >= CHANGELOG_MAX_INTERVAL:
            run_changelog_generator(f"{CHANGELOG_MAX_INTERVAL // 60} minutes passed with tracked activity")
            last_changelog_run = time.time()
            untracked_activity = False

if __name__ == "__main__":
    watcher_loop()
