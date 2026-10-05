import paramiko
import sys
import os
from dotenv import load_dotenv

# Load credentials from .env file (never hardcode secrets!)
load_dotenv()

HOST     = os.getenv("GPU_SERVER_HOST", "")
PORT     = int(os.getenv("GPU_SERVER_PORT", "22"))
USER     = os.getenv("GPU_SERVER_USER", "")
PASSWORD = os.getenv("GPU_SERVER_PASSWORD", "")

if not HOST or not USER or not PASSWORD:
    print("[ERROR] Missing GPU server credentials. Please set GPU_SERVER_HOST, GPU_SERVER_USER, GPU_SERVER_PASSWORD in your .env file.")
    sys.exit(1)

def run_command(client, cmd):
    print(f"\n>>> {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out:
        print(out)
    if err:
        print("[stderr]:", err)
    return out

try:
    print(f"Connecting to {HOST}:{PORT} as {USER}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=15)
    print("[OK] Connected successfully!\n")

    run_command(client, "hostname")
    run_command(client, "uname -a")
    run_command(client, "nvidia-smi")
    run_command(client, "df -h /")
    run_command(client, "free -h")

    client.close()

except paramiko.AuthenticationException:
    print("[ERROR] Authentication failed - wrong username or password.")
except paramiko.ssh_exception.NoValidConnectionsError:
    print(f"[ERROR] Could not connect to {HOST}:{PORT} - port may be closed or wrong.")
    print("Trying port 2222...")
    try:
        client.connect(HOST, port=2222, username=USER, password=PASSWORD, timeout=15)
        print("[OK] Connected on port 2222!")
        run_command(client, "hostname")
        run_command(client, "nvidia-smi")
        client.close()
    except Exception as e2:
        print(f"[ERROR] Also failed on port 2222: {e2}")
except Exception as e:
    print(f"[ERROR] Error: {e}")
