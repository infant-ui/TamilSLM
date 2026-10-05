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
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode(errors='replace')
    err = stderr.read().decode(errors='replace')
    if out:
        print(out)
    if err and 'Permission denied' not in err:
        print("[stderr]:", err)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=15)
print("[OK] Connected to", HOST)

# ============================================================
# PART 1: DETAILED du - find exactly what's big
# ============================================================

run(client, "FULL BREAKDOWN: /home (VM disks)", 
    "du -h --max-depth=3 /home 2>/dev/null | sort -rh | head -40")

run(client, "FULL BREAKDOWN: /var/lib/vz (ISO templates)",
    "du -h --max-depth=3 /var/lib/vz 2>/dev/null | sort -rh | head -20")

run(client, "ALL FILES > 1GB (sorted by size)",
    "find / -xdev -type f -size +1G 2>/dev/null | xargs ls -lh 2>/dev/null | awk '{print $5, $9}' | sort -rh")

run(client, "/root directory contents",
    "du -h --max-depth=2 /root 2>/dev/null | sort -rh | head -20")

# ============================================================
# PART 2: FIND GPU VM - check each VM config
# ============================================================

run(client, "ALL VM CONFIGS (look for GPU/PCI passthrough)",
    "for vmid in $(qm list | awk 'NR>1 {print $1}'); do echo \"--- VM $vmid ---\"; cat /etc/pve/qemu-server/$vmid.conf 2>/dev/null; echo; done")

run(client, "SPECIFICALLY: hostpci / GPU lines in all VM configs",
    "grep -l 'hostpci\\|nvidia\\|gpu\\|GPU\\|vga\\|NVIDIA' /etc/pve/qemu-server/*.conf 2>/dev/null && grep -h 'hostpci\\|vga\\|name\\|memory' /etc/pve/qemu-server/*.conf 2>/dev/null")

run(client, "PCI DEVICES ON HOST (GPUs)",
    "lspci | grep -iE 'vga|nvidia|amd|radeon|display|3d|gpu'")

run(client, "NVIDIA GPU DETAILS",
    "lspci -v | grep -A5 -iE 'nvidia|vga|3d controller'")

run(client, "CURRENTLY RUNNING VM (109) CONFIG",
    "cat /etc/pve/qemu-server/109.conf")

run(client, "VM 108 CONFIG (large RAM, likely GPU VM)",
    "cat /etc/pve/qemu-server/108.conf")

run(client, "VM 111 CONFIG",
    "cat /etc/pve/qemu-server/111.conf")

run(client, "VM 114 CONFIG (DIST - large disk)",
    "cat /etc/pve/qemu-server/114.conf")

client.close()
print("\n[DONE] Read-only investigation complete.")
