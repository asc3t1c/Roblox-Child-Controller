#!/usr/bin/python
import os
import time
import shutil
import subprocess
import signal
import sys

ROBLOX_EXE_NAMES = ["RobloxPlayerBeta.exe", "RobloxPlayerLauncher.exe"]
USER = os.getlogin()
LOCAL_ROBLOX_PATH = os.path.join("C:\\Users", USER, "AppData", "Local", "Roblox")

def kill_roblox_processes():
    for exe in ROBLOX_EXE_NAMES:
        try:
            subprocess.run(["taskkill", "/F", "/IM", exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"🔪 Killed process: {exe}")
        except Exception as e:
            print(f"⚠️ Failed to kill {exe}: {e}")

def delete_local_roblox_folder():
    if os.path.exists(LOCAL_ROBLOX_PATH):
        try:
            shutil.rmtree(LOCAL_ROBLOX_PATH)
            print(f"🗑️ Deleted local Roblox folder: {LOCAL_ROBLOX_PATH}")
        except Exception as e:
            print(f"❌ Failed to delete Roblox folder: {e}")
    else:
        print("ℹ️ Roblox folder not found.")

def delete_roblox_exe_files():
    print("🧹 Searching for Roblox .exe files in user-accessible locations...")

    search_dirs = [
        LOCAL_ROBLOX_PATH,
        os.environ.get("TEMP", r"C:\Windows\Temp"),
        os.path.join("C:\\Users", USER, "Downloads")
    ]

    count = 0
    for root_dir in search_dirs:
        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.lower().startswith("roblox") and file.lower().endswith(".exe"):
                    full_path = os.path.join(root, file)
                    try:
                        os.remove(full_path)
                        print(f"🗑️ Deleted: {full_path}")
                        count += 1
                    except Exception as e:
                        print(f"⚠️ Could not delete {full_path}: {e}")
    if count == 0:
        print("ℹ️ No .exe files deleted (none found or access denied).")
    else:
        print(f"✅ Removed {count} Roblox .exe file(s).")

def block_roblox_user_level():
    kill_roblox_processes()
    delete_local_roblox_folder()
    delete_roblox_exe_files()
    print("✅ Roblox blocked (user-level).")

def handle_exit(signum, frame):
    print("\n⚠️ Exit signal detected. Blocking Roblox now...")
    block_roblox_user_level()
    sys.exit(0)

def wait_then_block(hours):
    seconds = hours * 3600
    print(f"⏳ Waiting {hours} hour(s)...")
    try:
        time.sleep(seconds)
    except KeyboardInterrupt:
        handle_exit(None, None)
    print("\n⏲️ Time's up! Roblox will now be removed.")
    block_roblox_user_level()

def main():
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    try:
        wait_hours = float(input("⏳ Enter wait time in hours before blocking Roblox: "))
        if wait_hours <= 0:
            print("Please enter a number greater than 0.")
            return
    except ValueError:
        print("❌ Invalid number.")
        return

    wait_then_block(wait_hours)

if __name__ == "__main__":
    main()
