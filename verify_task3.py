import subprocess
import time
import requests
import json
import os

# Kill existing port 8002
subprocess.run("for /f \"tokens=5\" %a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do taskkill /f /pid %a", shell=True, stderr=subprocess.DEVNULL)

print("Starting correction-service...")
env = os.environ.copy()
env["PATH"] = os.path.abspath(r".venv\Scripts") + os.pathsep + env["PATH"]
python_path = os.path.abspath(r".venv\Scripts\python.exe")

corr_process = subprocess.Popen(
    [python_path, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8002"],
    cwd=r"backend\correction-service",
    env=env,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
time.sleep(3) # Wait for it to start

BASE_URL = "http://127.0.0.1:8002"

# 2. Submit a test report
print("\n--- Submitting Report ---")
resp = requests.post(f"{BASE_URL}/corrections/report", json={
    "reported_issue_text": "The mass of the earth is wrong, it should be 5.972 x 10^24 kg",
    "reported_by": "eval_pipeline"
})
print(resp.json())
report_id = resp.json()["report_id"]

# 3. Approve it
print("\n--- Approving Report ---")
resp = requests.post(f"{BASE_URL}/corrections/review/{report_id}", json={
    "status": "approved",
    "reviewed_by": "admin_jane",
    "reviewer_notes": "Verified against textbook page 42.",
    "approved_correction_text": "The mass of the Earth is 5.972 x 10^24 kg."
})
print(resp.json())

# 4. Standalone Lookup Test
print("\n--- Standalone Lookup Test ---")
resp = requests.get(f"{BASE_URL}/corrections/lookup?query=what is the mass of the earth?")
print("Lookup Response:", resp.json())

# 5. Integrated Retrieval-Service Test
print("\n--- Integrated Retrieval Service Test ---")
print("Restarting Retrieval Service to pick up changes...")
# Kill existing port 8000
subprocess.run("for /f \"tokens=5\" %a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /f /pid %a", shell=True, stderr=subprocess.DEVNULL)

env = os.environ.copy()
env["PATH"] = os.path.abspath(r".venv\Scripts") + os.pathsep + env["PATH"]

python_path = os.path.abspath(r".venv\Scripts\python.exe")
# Start retrieval service
retrieval_process = subprocess.Popen(
    [python_path, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
    cwd=r"backend\retrieval-service",
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

print("Waiting for retrieval service to start...")
time.sleep(10) # Give it 10 seconds to load models

if retrieval_process.poll() is not None:
    print("Retrieval service crashed!")
    out, err = retrieval_process.communicate()
    print("STDOUT:", out.decode('utf-8', errors='ignore'))
    print("STDERR:", err.decode('utf-8', errors='ignore'))

try:
    resp = requests.post("http://127.0.0.1:8000/retrieve", json={
        "question": "what is the mass of the earth?",
        "preferred_medium": "english",
        "allowed_content_types": ["textbook"],
        "class_id": 6,
        "term": 1
    }, timeout=20)
    
    if resp.status_code == 200:
        data = resp.json()
        sys_prompt = data.get("diagnostics", {}).get("system_prompt", "")
        if "[Verified Correction: The mass of the Earth is 5.972 x 10^24 kg.]" in sys_prompt:
            print("SUCCESS: Verified Correction found in system prompt!")
        else:
            print("FAILED: Verified correction not found in system prompt.")
            print(sys_prompt[:200])
    else:
        print(f"Retrieval Service returned {resp.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Retrieval service not reachable or failed: {e}")
finally:
    retrieval_process.terminate()
    print("\nCleaning up...")
    corr_process.terminate()
