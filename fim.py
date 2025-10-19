import os
import hashlib
import json
import datetime

# === Configuration ===
MONITOR_DIR = "test"        # Folder to monitor
BASELINE_FILE = "baseline.json"
LOG_DIR = "logs"             # Folder for log files

# === Ensure log folder exists ===
os.makedirs(LOG_DIR, exist_ok=True)

def get_file_hash(filepath):
    """Generate SHA256 hash for a file."""
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def create_baseline():
    baseline = {}
    for root, _, files in os.walk(MONITOR_DIR):
        for file in files:
            filepath = os.path.join(root, file)
            baseline[filepath] = get_file_hash(filepath)

    with open(BASELINE_FILE, "w") as f:
        json.dump(baseline, f, indent=4)

    log_event(f"Baseline created with {len(baseline)} files.")
    print(f"[+] Baseline created with {len(baseline)} files.")

def check_integrity():
    if not os.path.exists(BASELINE_FILE):
        print("[!] No baseline found. Please create one first.")
        return

    with open(BASELINE_FILE, "r") as f:
        baseline = json.load(f)

    current = {}
    for root, _, files in os.walk(MONITOR_DIR):
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
        print("[✓] No changes detected.")
        log_event("Integrity check: No changes detected.")
    else:
        print("[!] Changes detected:")
        log_event("Integrity check: Changes detected.")
        if modified:
            for f in modified:
                print(f"    Modified: {f}")
                log_event(f"Modified: {f}")
        if added:
            for f in added:
                print(f"    Added: {f}")
                log_event(f"Added: {f}")
        if deleted:
            for f in deleted:
                print(f"    Deleted: {f}")
                log_event(f"Deleted: {f}")

def log_event(message):
    """Save events with timestamp into logs folder."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logfile = os.path.join(LOG_DIR, f"log_{datetime.date.today()}.txt")
    with open(logfile, "a") as log:
        log.write(f"[{timestamp}] {message}\n")

def main():
    while True:
        print("\n=== File Integrity Monitor ===")
        print("1. Create Baseline")
        print("2. Check Integrity")
        print("3. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            create_baseline()
        elif choice == "2":
            check_integrity()
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("[!] Invalid option.")

if __name__ == "__main__":
    main()
