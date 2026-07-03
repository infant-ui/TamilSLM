import subprocess
import sys

def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    return result.stdout.strip()

print("Fetching all commits...")
commits = run_cmd(["git", "rev-list", "--all"]).split()

print(f"Scanning {len(commits)} commits...")

exclusions = [
    ":!graphify-out",
    ":!docs/graphify",
    ":!node_modules",
    ":!.venv",
    ":!*package-lock.json",
    ":!*.svg",
    ":!*.png"
]

search_pattern = "api_key.?=|password.?=|secret.?=|token.?=|sk-|bearer"

# We run git grep -iE pattern <commit> -- . exclusions
findings = []

for i, commit in enumerate(commits):
    if i % 100 == 0:
        print(f"Scanned {i}/{len(commits)} commits...")
    
    cmd = ["git", "grep", "-iE", search_pattern, commit, "--", "."] + exclusions
    out = run_cmd(cmd)
    if out:
        for line in out.splitlines():
            # Skip if it's just import statements or obvious false positives
            if "import " not in line.lower() and "from " not in line.lower():
                findings.append(line)

print("--- SCAN COMPLETE ---")
for f in set(findings):  # deduplicate
    print(f)
