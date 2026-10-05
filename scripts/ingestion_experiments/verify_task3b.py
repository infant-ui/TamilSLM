import subprocess
import time
import requests
import json
import os

print("--- Starting verify_task3b ---")

def kill_port(port):
    subprocess.run(f"for /f \"tokens=5\" %a in ('netstat -aon ^| findstr :{port} ^| findstr LISTENING') do taskkill /f /pid %a", shell=True, stderr=subprocess.DEVNULL)

kill_port(8002)
kill_port(8000)

env = os.environ.copy()
env["PATH"] = os.path.abspath(r".venv\Scripts") + os.pathsep + env["PATH"]
python_path = os.path.abspath(r".venv\Scripts\python.exe")

print("\n1. Starting correction-service...")
corr_process = subprocess.Popen(
    [python_path, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8002"],
    cwd=r"backend\correction-service",
    env=env,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
time.sleep(3)

print("2. Starting retrieval-service...")
retrieval_process = subprocess.Popen(
    [python_path, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
    cwd=r"backend\retrieval-service",
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

print("Waiting for retrieval-service to start (checking logs)...")
import threading

def stream_reader(pipe, prefix):
    for line in iter(pipe.readline, b''):
        decoded = line.decode('utf-8', errors='ignore').strip()
        try:
            print(f"[{prefix}] {decoded}".encode('utf-8', errors='replace').decode('utf-8'))
        except:
            pass
        
t_out = threading.Thread(target=stream_reader, args=(retrieval_process.stdout, "RETRIEVAL STDOUT"))
t_err = threading.Thread(target=stream_reader, args=(retrieval_process.stderr, "RETRIEVAL STDERR"))
t_out.daemon = True
t_err.daemon = True
t_out.start()
t_err.start()

# Wait loop
for _ in range(60):
    try:
        r = requests.get("http://127.0.0.1:8000/docs", timeout=1)
        if r.status_code == 200:
            print("Retrieval service is UP!")
            break
    except:
        pass
    time.sleep(1)

try:
    print("\n3. Testing when correction-service is UP")
    resp = requests.post("http://127.0.0.1:8000/retrieve", json={
        "question": "what is the mass of the earth?",
        "preferred_medium": "english",
        "allowed_content_types": ["textbook"],
        "class_id": 6,
        "term": 1
    }, timeout=20)
    data = resp.json()
    sys_prompt = data.get("diagnostics", {}).get("system_prompt", "")
    scanned = data.get("diagnostics", {}).get("scanned_nodes_count", 0)
    print(f"System Prompt Snippet: {sys_prompt[:100]}")
    print(f"Scanned Nodes: {scanned}")

    print("\n4. Killing correction-service...")
    corr_process.terminate()
    time.sleep(2)
    
    print("5. Testing when correction-service is DOWN")
    resp2 = requests.post("http://127.0.0.1:8000/retrieve", json={
        "question": "what is the mass of the earth?",
        "preferred_medium": "english",
        "allowed_content_types": ["textbook"],
        "class_id": 6,
        "term": 1
    }, timeout=20)
    data2 = resp2.json()
    sys_prompt2 = data2.get("diagnostics", {}).get("system_prompt", "")
    scanned2 = data2.get("diagnostics", {}).get("scanned_nodes_count", 0)
    print(f"System Prompt Snippet: {sys_prompt2[:100]}")
    print(f"Scanned Nodes: {scanned2}")
    
finally:
    retrieval_process.terminate()
    try:
        corr_process.terminate()
    except:
        pass
    print("\nCleaning up...")
