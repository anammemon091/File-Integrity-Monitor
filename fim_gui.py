import os
import hashlib
import json
import datetime
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext

# === Configuration ===
BASELINE_FILE = "baseline.json"
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

selected_folder = None  # User-chosen folder

# === Core Functions ===
def get_file_hash(filepath):
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def create_baseline():
    global selected_folder
    if not selected_folder:
        messagebox.showwarning("Warning", "Please select a folder first!")
        return

    baseline = {}
    for root, _, files in os.walk(selected_folder):
        for file in files:
            filepath = os.path.join(root, file)
            baseline[filepath] = get_file_hash(filepath)

    with open(BASELINE_FILE, "w") as f:
        json.dump(baseline, f, indent=4)

    log_event(f"Baseline created with {len(baseline)} files for {selected_folder}")
    messagebox.showinfo("Baseline", f"Baseline created with {len(baseline)} files.")
    update_log_display()

def check_integrity():
    global selected_folder
    if not selected_folder:
        messagebox.showwarning("Warning", "Please select a folder first!")
        return
    if not os.path.exists(BASELINE_FILE):
        messagebox.showwarning("Warning", "No baseline found! Create one first.")
        return

    with open(BASELINE_FILE, "r") as f:
        baseline = json.load(f)

    current = {}
    for root, _, files in os.walk(selected_folder):
        for file in files:
            filepath = os.path.join(root, file)
            current[filepath] = get_file_hash(filepath)

    modified, added, deleted = [], [], []

    for filepath, hash_value in baseline.items():
        if filepath not in current:
            deleted.append(filepath)
        elif current[filepath] != hash_value:
            modified.append(filepath)

    for filepath in current:
        if filepath not in baseline:
            added.append(filepath)

    if not modified and not added and not deleted:
        msg = "[✓] No changes detected."
        log_event(f"No changes detected in {selected_folder}")
    else:
        msg = "[!] Changes detected:\n"
        if modified:
            msg += "\nModified:\n" + "\n".join(modified)
            for f in modified: log_event(f"Modified: {f}")
        if added:
            msg += "\nAdded:\n" + "\n".join(added)
            for f in added: log_event(f"Added: {f}")
        if deleted:
            msg += "\nDeleted:\n" + "\n".join(deleted)
            for f in deleted: log_event(f"Deleted: {f}")
        log_event(f"Changes detected in {selected_folder}")

    messagebox.showinfo("Integrity Check Result", msg)
    update_log_display()

def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logfile = os.path.join(LOG_DIR, f"log_{datetime.date.today()}.txt")
    with open(logfile, "a") as log:
        log.write(f"[{timestamp}] {message}\n")

def update_log_display():
    log_area.delete(1.0, tk.END)
    logfile = os.path.join(LOG_DIR, f"log_{datetime.date.today()}.txt")
    if os.path.exists(logfile):
        with open(logfile, "r") as f:
            log_area.insert(tk.END, f.read())

def browse_folder():
    global selected_folder
    folder = filedialog.askdirectory()
    if folder:
        selected_folder = folder
        folder_label.config(text=f"📂 Selected Folder: {selected_folder}")
        log_event(f"Folder selected: {selected_folder}")
        update_log_display()

# === GUI Setup ===
root = tk.Tk()
root.title("File Integrity Monitor")
root.geometry("700x500")
root.config(bg="#1e1e1e")

# Title
title = tk.Label(root, text="🔒 File Integrity Monitor", font=("Segoe UI", 18, "bold"), bg="#1e1e1e", fg="#00ffcc")
title.pack(pady=10)

# Folder selection
browse_frame = tk.Frame(root, bg="#1e1e1e")
browse_frame.pack(pady=5)

browse_btn = tk.Button(browse_frame, text="📁 Browse Folder", command=browse_folder, width=18, bg="#00ffcc", fg="black", font=("Segoe UI", 10, "bold"))
browse_btn.grid(row=0, column=0, padx=10)

folder_label = tk.Label(root, text="📂 Selected Folder: None", bg="#1e1e1e", fg="white", font=("Segoe UI", 10))
folder_label.pack(pady=5)

# Buttons
button_frame = tk.Frame(root, bg="#1e1e1e")
button_frame.pack(pady=10)

btn_create = tk.Button(button_frame, text="Create Baseline", command=create_baseline, width=18, bg="#00ffcc", fg="black", font=("Segoe UI", 10, "bold"))
btn_create.grid(row=0, column=0, padx=10)

btn_check = tk.Button(button_frame, text="Check Integrity", command=check_integrity, width=18, bg="#00ffcc", fg="black", font=("Segoe UI", 10, "bold"))
btn_check.grid(row=0, column=1, padx=10)

btn_exit = tk.Button(button_frame, text="Exit", command=root.destroy, width=18, bg="#ff4444", fg="white", font=("Segoe UI", 10, "bold"))
btn_exit.grid(row=0, column=2, padx=10)

# Log Display Area
log_label = tk.Label(root, text="📜 Logs", bg="#1e1e1e", fg="#00ffcc", font=("Segoe UI", 12, "bold"))
log_label.pack(pady=5)

log_area = scrolledtext.ScrolledText(root, width=85, height=15, bg="#2d2d2d", fg="white", font=("Consolas", 10))
log_area.pack(padx=10, pady=5)
update_log_display()

root.mainloop()
