import paramiko
import os
from dotenv import load_dotenv

# Load credentials from .env file (never hardcode secrets!)
load_dotenv()

HOST     = os.getenv("GPU_SERVER_HOST", "")
PORT     = int(os.getenv("GPU_SERVER_PORT", "22"))
USER     = os.getenv("GPU_SERVER_USER", "")
PASSWORD = os.getenv("GPU_SERVER_PASSWORD", "")

if not HOST or not USER or not PASSWORD:
    print("[ERROR] Missing GPU server credentials. Check your .env file.")
    raise SystemExit(1)

def run(client, label, cmd):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    out = stdout.read().decode(errors='replace')
    err = stderr.read().decode(errors='replace')
    if out:
        print(out)
    if err:
        print("[stderr]:", err)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=15)
print("[OK] Connected to", HOST)

# 1. Overall disk usage
run(client, "DISK USAGE OVERVIEW", "df -h")

# 2. Top-level directories eating space
run(client, "TOP-LEVEL DIRECTORY SIZES (root /)", "du -h --max-depth=1 / 2>/dev/null | sort -rh | head -20")

# 3. What's in /var (logs, cache, etc.)
run(client, "WHAT IS INSIDE /var", "du -h --max-depth=2 /var 2>/dev/null | sort -rh | head -20")

# 4. What's in /var/log
run(client, "LOG FILES IN /var/log", "du -h --max-depth=2 /var/log 2>/dev/null | sort -rh | head -20")

# 5. Proxmox specific - VM disk images
run(client, "PROXMOX VM STORAGE (/var/lib/vz)", "du -h --max-depth=2 /var/lib/vz 2>/dev/null | sort -rh | head -20")

# 6. Check /tmp
run(client, "TEMP FILES /tmp", "du -h --max-depth=1 /tmp 2>/dev/null | sort -rh | head -10")

# 7. Largest individual files on the system
run(client, "TOP 20 LARGEST FILES ON SYSTEM", "find / -xdev -type f -size +500M 2>/dev/null | xargs ls -lh 2>/dev/null | sort -k5 -rh | head -20")

# 8. Proxmox logs
run(client, "PROXMOX LOGS (/var/log/pve)", "du -h /var/log/pve* 2>/dev/null | sort -rh | head -10")

# 9. List Proxmox VMs
run(client, "PROXMOX VMs LIST", "qm list 2>/dev/null || echo 'qm not found'")

# 10. List Proxmox containers
run(client, "PROXMOX CONTAINERS LIST", "pct list 2>/dev/null || echo 'pct not found'")

client.close()
print("\n[DONE] Investigation complete. No changes were made.")
