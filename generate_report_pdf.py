from fpdf import FPDF
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
GPU_HOST = os.getenv("GPU_SERVER_HOST", "GPU Server")

class ServerReportPDF(FPDF):
    def header(self):
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 28, 'F')
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 7)
        self.cell(0, 8, "GPU Server Investigation Report", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(180, 200, 230)
        self.set_xy(10, 17)
        self.cell(0, 6, f"Server: {GPU_HOST}  |  Host: auistgpu  |  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        self.ln(15)

    def footer(self):
        self.set_y(-13)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()} | GPU Server Report - Confidential", align="C")

    def section_title(self, title):
        self.ln(4)
        self.set_fill_color(30, 58, 138)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, f"  {title}", new_x="LMARGIN", new_y="NEXT", fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def alert_box(self, text, color=(220, 38, 38)):
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 7, f"  {text}", new_x="LMARGIN", new_y="NEXT", fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def kv_row(self, key, value, highlight=False):
        self.set_font("Helvetica", "B", 9)
        if highlight:
            self.set_fill_color(254, 240, 138)
        else:
            self.set_fill_color(245, 247, 250)
        self.cell(52, 6, f"  {key}", fill=True)
        self.set_font("Helvetica", "", 9)
        self.cell(0, 6, value, fill=True, new_x="LMARGIN", new_y="NEXT")

    def table_header(self, cols, widths):
        self.set_fill_color(30, 58, 138)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 8)
        for i, (col, w) in enumerate(zip(cols, widths)):
            nx = "LMARGIN" if i == len(cols)-1 else "RIGHT"
            ny = "NEXT" if i == len(cols)-1 else "TOP"
            self.cell(w, 7, col, fill=True, align="C", new_x=nx, new_y=ny)
        self.set_text_color(0, 0, 0)


pdf = ServerReportPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# SECTION 1: Server Overview
pdf.section_title("1. SERVER OVERVIEW")
pdf.alert_box("CRITICAL: Root Disk is 100% FULL -- No VMs can start!", color=(185, 28, 28))
pdf.ln(2)

fields = [
    ("Hostname",        "auistgpu"),
    ("Operating System","Linux - Proxmox VE 6.8.12-17"),
    ("Total RAM",       "251 GB"),
    ("Used RAM",        "13 GB"),
    ("Free RAM",        "238 GB"),
    ("Root Disk Total", "94 GB"),
    ("Root Disk Used",  "92 GB  (100% FULL)"),
    ("Root Disk Free",  "0 GB -- DISK IS FULL"),
    ("SSH Port",        "22"),
    ("Web UI Port",     "8006 (Proxmox Web Interface)"),
]
for k, v in fields:
    pdf.kv_row(k, v, highlight=("FULL" in v or "100%" in v))

# SECTION 2: GPU Hardware
pdf.section_title("2. GPU HARDWARE DETECTED")
pdf.ln(1)
gpu_fields = [
    ("GPU Model",       "NVIDIA AD102GL [L40S]"),
    ("GPU Type",        "Data Center / AI / Professional GPU"),
    ("VRAM",            "48 GB"),
    ("PCI Slot",        "26:00.0  (address: 0000:26:00)"),
    ("IOMMU Group",     "21"),
    ("Kernel Modules",  "nvidiafb, nouveau (host side)"),
    ("Management GPU",  "Matrox MGA G200eH3 - HPE iLO5 (NOT for compute)"),
]
for k, v in gpu_fields:
    pdf.kv_row(k, v, highlight=("L40S" in v or "48 GB" in v))

# SECTION 3: Disk Usage
pdf.section_title("3. DISK USAGE BREAKDOWN")
pdf.ln(1)
pdf.set_font("Helvetica", "B", 9)
pdf.set_fill_color(220, 230, 255)
pdf.cell(0, 6, "  Top-Level Directory Sizes", new_x="LMARGIN", new_y="NEXT", fill=True)
pdf.ln(1)

dirs = [
    ("/home",  "71 GB",  "VM disk image files (.qcow2) -- MAIN CULPRIT"),
    ("/var",   "16 GB",  "Proxmox ISO templates + system logs"),
    ("/usr",   " 5 GB",  "System binaries"),
    ("/root",  "294 MB", "Root user home folder"),
    ("/tmp",   " 36 KB", "Temp files (clean)"),
]
pdf.table_header(["Directory", "Size", "Contents"], [35, 25, 130])
for i, (d, s, c) in enumerate(dirs):
    if i == 0:
        pdf.set_fill_color(255, 220, 220)
    else:
        pdf.set_fill_color(248, 250, 255)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(35, 6, d, fill=True)
    pdf.cell(25, 6, s, fill=True, align="C")
    pdf.cell(0, 6, c, fill=True, new_x="LMARGIN", new_y="NEXT")

pdf.ln(4)
pdf.set_font("Helvetica", "B", 9)
pdf.set_fill_color(220, 230, 255)
pdf.cell(0, 6, "  VM Disk Image Files  (/home/OS/images/)", new_x="LMARGIN", new_y="NEXT", fill=True)
pdf.ln(1)

vm_files = [
    ("vm-110-disk-0.qcow2",  "513 GB*", "VM 110 - oslab-desktop"),
    ("vm-109-disk-1.qcow2",  "257 GB*", "VM 109 - currently running (no GPU)"),
    ("vm-111-disk-0.qcow2",  " 61 GB",  "VM 111"),
    ("vm-108-disk-0.qcow2",  " 61 GB",  "VM 108"),
    ("vm-102-disk-0.qcow2",  " 33 GB",  "VM 102"),
    ("vm-107-disk-0.qcow2",  " 33 GB",  "VM 107"),
    ("vm-109-disk-0.qcow2",  " 33 GB",  "VM 109 base disk"),
    ("base-101-disk-0.qcow2"," 33 GB",  "VM 101 template"),
    ("vm-105-disk-0.qcow2",  "  2 GB",  "VM 105"),
    ("vm-106-disk-0.qcow2",  "1.8 GB",  "VM 106"),
]
pdf.table_header(["Filename", "Alloc. Size", "VM / Notes"], [70, 30, 90])
for i, row in enumerate(vm_files):
    pdf.set_fill_color(255, 235, 235) if i < 2 else pdf.set_fill_color(248, 250, 255)
    pdf.set_font("Helvetica", "", 8)
    for val, w in zip(row, [70, 30, 90]):
        pdf.cell(w, 6, val, fill=True)
    pdf.ln()

pdf.ln(2)
pdf.set_font("Helvetica", "I", 8)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 5, "  * Allocated size shown. Actual disk footprint is 92 GB total (sparse/thin-provisioned).", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0,0,0)

pdf.ln(3)
pdf.set_font("Helvetica", "B", 9)
pdf.set_fill_color(220, 230, 255)
pdf.cell(0, 6, "  ISO Files Taking Space", new_x="LMARGIN", new_y="NEXT", fill=True)
pdf.ln(1)

isos = [
    ("/home/OS/",                 "ubuntu-24.04.3-desktop-amd64.iso", "6.0 GB", "DUPLICATE!"),
    ("/var/lib/vz/template/iso/", "ubuntu-24.04.3-desktop-amd64.iso", "6.0 GB", "DUPLICATE copy"),
    ("/var/lib/vz/template/iso/", "ubuntu-25.10-desktop-amd64.iso",   "5.4 GB", "Old version"),
    ("/var/lib/vz/template/iso/", "ubuntu-20.04.6-desktop-amd64.iso", "4.1 GB", "Old version"),
    ("/home/OS/template/iso/",    "ubuntu-26.04-live-server-amd64.iso","2.8 GB","Used by VM 114"),
]
pdf.table_header(["Location", "Filename", "Size", "Note"], [50, 75, 18, 47])
for row in isos:
    pdf.set_fill_color(255, 240, 200) if "DUPLICATE" in row[3] else pdf.set_fill_color(248, 250, 255)
    pdf.set_font("Helvetica", "", 7)
    for val, w in zip(row, [50, 75, 18, 47]):
        pdf.cell(w, 6, val, fill=True)
    pdf.ln()

# SECTION 4: All VMs
pdf.add_page()
pdf.section_title("4. ALL VMs ON THIS SERVER")
pdf.ln(1)

vms = [
    ("100", "oslab",              "stopped", "8 GB",   "50 GB",  "YES - 0000:26:00"),
    ("101", "oslab-template",     "stopped", "2 GB",   "32 GB",  "No"),
    ("102", "Copy-of-VM-student", "stopped", "2 GB",   "32 GB",  "No"),
    ("103", "oslab02",            "stopped", "2 GB",   "32 GB",  "No (iLO VGA)"),
    ("104", "oslab03",            "stopped", "2 GB",   "32 GB",  "No"),
    ("105", "student",            "stopped", "2 GB",   "32 GB",  "No"),
    ("106", "oslab05",            "stopped", "2 GB",   "32 GB",  "No"),
    ("107", "Test",               "stopped", "2 GB",   "32 GB",  "No"),
    ("108", "VM 108",             "stopped", "32 GB",  "60 GB",  "No"),
    ("109", "VM 109",             "RUNNING", "32 GB",  "256 GB", "NO GPU"),
    ("110", "oslab-desktop",      "stopped", "15.5 GB","512 GB", "YES - x-vga=1"),
    ("111", "VM 111",             "stopped", "34 GB",  "60 GB",  "YES - 0000:26:00"),
    ("112", "VM 112",             "stopped", "35 GB",  "1 TB",   "No"),
    ("113", "VM 113",             "stopped", "35 GB",  "1 TB",   "YES - pcie=1"),
    ("114", "DIST",               "stopped", "158 GB", "512 GB", "YES - pcie=1 (BEST)"),
]
pdf.table_header(["VMID","Name","Status","RAM","Disk","GPU Passthrough"], [15, 42, 22, 18, 18, 75])
for row in vms:
    is_best = "BEST" in row[5]
    has_gpu = "YES" in row[5]
    is_running = row[2] == "RUNNING"
    if is_best:
        pdf.set_fill_color(220, 255, 220)
    elif has_gpu:
        pdf.set_fill_color(240, 255, 240)
    elif is_running:
        pdf.set_fill_color(255, 250, 220)
    else:
        pdf.set_fill_color(248, 250, 255)
    pdf.set_font("Helvetica", "B" if is_best else "", 8)
    for val, w in zip(row, [15, 42, 22, 18, 18, 75]):
        pdf.cell(w, 6, val, fill=True)
    pdf.ln()

pdf.ln(3)
pdf.set_font("Helvetica", "I", 8)
pdf.set_text_color(30, 100, 30)
pdf.cell(0, 5, "  Green = GPU passthrough  |  Bold green = Recommended  |  Yellow = Currently running", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0,0,0)

# SECTION 5: Best GPU VMs
pdf.section_title("5. RECOMMENDED GPU VMs (RANKED)")
pdf.ln(2)

ranks = [
    ("RANK 1", "VM 114 - DIST", [
        ("CPU",      "16 cores, 2 sockets, cpu=host (full native speed)"),
        ("RAM",      "158 GB"),
        ("Disk",     "512 GB SSD (local-lvm, discard=on)"),
        ("GPU",      "hostpci0: 0000:26:00, pcie=1  (PCIe passthrough)"),
        ("OS",       "Ubuntu 26.04 server"),
        ("Status",   "STOPPED -- ready to start once disk is freed"),
        ("Why Best", "Most RAM, most CPU cores, PCIe passthrough, native CPU mode"),
    ], (22, 120, 20)),
    ("RANK 2", "VM 113", [
        ("CPU",    "8 cores"),
        ("RAM",    "35 GB"),
        ("Disk",   "1 TB (local-lvm)"),
        ("GPU",    "hostpci0: 26:00, pcie=1  (PCIe passthrough)"),
        ("Status", "STOPPED"),
    ], (30, 100, 30)),
    ("RANK 3", "VM 111", [
        ("CPU",    "6 cores"),
        ("RAM",    "34 GB"),
        ("Disk",   "60 GB"),
        ("GPU",    "hostpci0: 0000:26:00"),
        ("Status", "STOPPED"),
    ], (60, 130, 60)),
]
for rank, name, details, color in ranks:
    pdf.set_fill_color(*color)
    pdf.set_text_color(255,255,255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 7, f"  {rank}: {name}", new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.set_text_color(0,0,0)
    pdf.ln(1)
    for k, v in details:
        pdf.kv_row(k, v, highlight=(k == "Why Best"))
    pdf.ln(3)

# SECTION 6: Why Can't Train
pdf.section_title("6. WHY YOU CANNOT TRAIN MODELS RIGHT NOW")
pdf.ln(1)

blockers = [
    ("Blocker 1: Root disk is 100% FULL",
     "No VM can start while disk has 0 bytes free. Proxmox needs free space to write VM state files, logs, and runtime data.", (185, 28, 28)),
    ("Blocker 2: All GPU VMs are STOPPED",
     "VM 114, 113, and 111 all have GPU passthrough but are stopped. VM 109 is the only running VM and it has NO GPU assigned -- running training on it will use CPU only.", (194, 65, 12)),
    ("Blocker 3: NVIDIA Drivers not installed in GPU VMs",
     "Even after starting a GPU VM, NVIDIA drivers + CUDA must be installed inside it. Without them, nvidia-smi fails and PyTorch/TensorFlow cannot detect the GPU.", (161, 98, 7)),
]
for title, detail, color in blockers:
    pdf.set_fill_color(*color)
    pdf.set_text_color(255,255,255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, f"  {title}", new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.set_text_color(50,50,50)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_fill_color(255,248,245)
    pdf.multi_cell(0, 5, f"  {detail}", fill=True)
    pdf.ln(2)

# SECTION 7: Cleanup Plan
pdf.section_title("7. DISK CLEANUP PLAN (Recommended Order)")
pdf.ln(1)

steps = [
    ("Step 1", "Remove duplicate Ubuntu 24.04 ISO from /home/OS/",    "~6 GB",        "LOW",    "Safe -- exact copy already in /var/lib/vz/template/iso/"),
    ("Step 2", "Remove old Ubuntu 20.04 + 25.10 ISOs",                "~10 GB",       "MEDIUM", "Verify no VM uses these as boot media"),
    ("Step 3", "Delete unused stopped VMs (107, 102, 103, 104, 106)", "30-60 GB each","HIGH",   "Cannot be undone -- confirm each VM is truly unused"),
    ("Step 4", "Move VM images to dedicated storage volume",           "Frees root",   "HIGH",   "Long-term fix -- needs additional storage hardware"),
]
pdf.table_header(["Step","Action","Space Saved","Risk","Notes"], [14, 65, 22, 15, 74])
risk_colors = {"LOW":(220,255,220), "MEDIUM":(255,250,200), "HIGH":(255,220,220)}
for step, action, saved, risk, note in steps:
    pdf.set_fill_color(*risk_colors[risk])
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(14, 6, step,   fill=True)
    pdf.cell(65, 6, action, fill=True)
    pdf.cell(22, 6, saved,  fill=True, align="C")
    pdf.cell(15, 6, risk,   fill=True, align="C")
    pdf.cell(0,  6, note,   fill=True, new_x="LMARGIN", new_y="NEXT")

# SECTION 8: Steps to Train
pdf.ln(4)
pdf.section_title("8. STEPS TO GET GPU TRAINING WORKING (~20 Minutes)")
pdf.ln(1)

action_steps = [
    ("Step 1", "Free disk space",               "Remove duplicate ISO -- 6 GB freed in ~2 min"),
    ("Step 2", "Start VM 114 (DIST)",            "Boot the best GPU VM via Proxmox"),
    ("Step 3", "Find VM 114 IP address",         "Check VM's assigned IP to SSH into it"),
    ("Step 4", "SSH into VM 114",                "Connect as root or ubuntu user"),
    ("Step 5", "Install NVIDIA drivers",         "sudo apt install nvidia-driver-550 + reboot"),
    ("Step 6", "Install CUDA + cuDNN",           "Follow NVIDIA CUDA toolkit installation guide"),
    ("Step 7", "Install PyTorch / HuggingFace",  "pip install torch transformers datasets"),
    ("Step 8", "Upload dataset + model files",   "Use scp or rsync to transfer files"),
    ("Step 9", "Run training / fine-tuning",     "python train.py -- GPU active and ready!"),
]
pdf.table_header(["#", "Action", "Details"], [14, 55, 121])
for step, action, detail in action_steps:
    pdf.set_fill_color(235, 245, 255)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(14,  6, step,   fill=True)
    pdf.cell(55,  6, action, fill=True)
    pdf.cell(0,   6, detail, fill=True, new_x="LMARGIN", new_y="NEXT")

pdf.ln(3)
pdf.set_fill_color(220, 255, 220)
pdf.set_font("Helvetica", "B", 9)
pdf.set_text_color(22, 101, 52)
pdf.cell(0, 7, "  Estimated time to training-ready: ~20 minutes after disk cleanup", new_x="LMARGIN", new_y="NEXT", fill=True)
pdf.set_text_color(0,0,0)

out_path = r"d:\Project Assistan\GPU_Server_Report.pdf"
pdf.output(out_path)
print(f"[OK] PDF saved: {out_path}")
