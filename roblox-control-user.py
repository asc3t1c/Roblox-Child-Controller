#!/usr/bin/python
import os
import time
import shutil
import subprocess
import signal
import sys

USER = os.getlogin()
LOCAL_ROBLOX_PATH = os.path.join("C:\\Users", USER, "AppData", "Local", "Roblox")

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
DOMAINS = ["www.roblox.com", "roblox.com"]
REDIRECT_IP = "127.0.0.1"
BLOCK_ENTRIES = [f"{REDIRECT_IP} {domain}\n" for domain in DOMAINS]

def kill_roblox_processes():
    try:
        tasks = subprocess.check_output("tasklist", shell=True, text=True).splitlines()
        for task in tasks:
            name = task.split()[0]
            if name.lower().startswith("robloxplayer") and name.lower().endswith(".exe"):
                subprocess.run(["taskkill", "/F", "/IM", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"🔪 Killed process: {name}")
    except Exception as e:
        print(f"⚠️ Error killing Roblox processes: {e}")

def delete_roblox_exe_files():
    print("🧹 Searching for RobloxPlayer*.exe files...")
    search_dirs = [
        LOCAL_ROBLOX_PATH,
        os.environ.get("TEMP", r"C:\Windows\Temp"),
        os.path.join("C:\\Users", USER, "Downloads")
    ]

    deleted = 0
    for root_dir in search_dirs:
        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.lower().startswith("robloxplayer") and file.lower().endswith(".exe"):
                    try:
                        os.remove(os.path.join(root, file))
                        print(f"🗑️ Deleted: {os.path.join(root, file)}")
                        deleted += 1
                    except Exception as e:
                        print(f"⚠️ Could not delete {file}: {e}")
    if deleted == 0:
        print("ℹ️ No RobloxPlayer .exe files were deleted.")
    else:
        print(f"✅ Deleted {deleted} RobloxPlayer .exe files.")

def delete_local_roblox_folder():
    if os.path.exists(LOCAL_ROBLOX_PATH):
        try:
            shutil.rmtree(LOCAL_ROBLOX_PATH)
            print(f"🗑️ Deleted Roblox folder: {LOCAL_ROBLOX_PATH}")
        except Exception as e:
            print(f"❌ Could not delete Roblox folder: {e}")
    else:
        print("ℹ️ Roblox folder not found.")

def block_domains():
    try:
        with open(HOSTS_PATH, 'r+', encoding="utf-8") as f:
            lines = f.readlines()
            f.seek(0, os.SEEK_END)
            for entry in BLOCK_ENTRIES:
                if entry not in lines:
                    f.write(entry)
                    print(f"🚫 Blocked domain: {entry.strip().split()[1]}")
        print("✅ Roblox domains blocked.")
    except PermissionError:
        print("⚠️ Cannot block domains — run as administrator.")
    except Exception as e:
        print(f"❌ Failed to modify hosts file: {e}")

def block_roblox():
    kill_roblox_processes()
    delete_roblox_exe_files()
    delete_local_roblox_folder()
    block_domains()
    print("✅ Roblox blocked successfully.")

def handle_exit(signum, frame):
    print("\n⚠️ Exit signal detected. Blocking Roblox now...")
    block_roblox()
    sys.exit(0)

def wait_then_block(hours):
    seconds = int(hours * 3600)
    print(f"⏳ Waiting for {hours} hour(s)... Press Ctrl+C to block immediately.")
    try:
        time.sleep(seconds)
    except KeyboardInterrupt:
        handle_exit(None, None)
    print("\n⏲️ Time's up! Blocking Roblox now...")
    block_roblox()

def main():
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    try:
        wait_hours = float(input("⏳ Enter wait time (in hours) before blocking Roblox: "))
        if wait_hours <= 0:
            print("⚠️ Please enter a number greater than 0.")
            return
    except ValueError:
        print("❌ Invalid input.")
        return

    wait_then_block(wait_hours)

if __name__ == "__main__":
    main()
