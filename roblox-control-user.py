#!/usr/bin/python
import time
import os
import sys
import subprocess
import shutil
import signal

def kill_roblox_processes():
    procs = ["RobloxPlayerBeta.exe", "RobloxPlayerLauncher.exe"]
    for proc in procs:
        try:
            subprocess.run(['taskkill', '/F', '/IM', proc], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"❌ Killed process: {proc}")
        except Exception as e:
            print(f"⚠️ Failed to kill {proc}: {e}")

def find_roblox_executables():
    user = os.getlogin()
    base_path = rf"C:\Users\{user}\AppData\Local\Roblox\Versions"
    executables = []
    if os.path.exists(base_path):
        for root, _, files in os.walk(base_path):
            for file in files:
                if file.lower() == "robloxplayerbeta.exe":
                    executables.append(os.path.join(root, file))
    return executables

def rename_roblox_executables():
    count = 0
    paths = find_roblox_executables()
    for path in paths:
        new_path = path + ".blocked"
        try:
            os.rename(path, new_path)
            print(f"🔒 Renamed: {os.path.basename(path)} -> {os.path.basename(new_path)}")
            count += 1
        except Exception as e:
            print(f"⚠️ Could not rename {path}: {e}")
    if count == 0:
        print("ℹ️ No Roblox executables found to rename.")
    return count

def remove_roblox_appdata():
    user = os.getlogin()
    appdata_path = rf"C:\Users\{user}\AppData\Local\Roblox"
    if os.path.exists(appdata_path):
        try:
            shutil.rmtree(appdata_path)
            print(f"🗑️ Deleted Roblox AppData: {appdata_path}")
            return True
        except Exception as e:
            print(f"⚠️ Failed to delete AppData: {e}")
            return False
    else:
        print("ℹ️ Roblox AppData folder not found.")
        return True

def remove_local_exe_files():
    user_profile = os.environ.get("USERPROFILE", r"C:\Users")
    removed = 0
    for root, _, files in os.walk(user_profile):
        for file in files:
            if file.lower().startswith("roblox") and file.lower().endswith(".exe"):
                full_path = os.path.join(root, file)
                try:
                    os.remove(full_path)
                    print(f"🗑️ Deleted local .exe: {full_path}")
                    removed += 1
                except Exception as e:
                    print(f"⚠️ Could not delete {full_path}: {e}")
    if removed == 0:
        print("ℹ️ No local Roblox .exe files found.")
    else:
        print(f"✅ Deleted {removed} local .exe file(s).")

def handle_ctrl_c(signum, frame):
    print("\n🚫 Ctrl+C detected. Blocking Roblox now...")
    block_everything()

def block_everything():
    kill_roblox_processes()
    rename_roblox_executables()
    remove_roblox_appdata()
    remove_local_exe_files()
    print("\n✅ Roblox access has been blocked for this user.")
    sys.exit(0)

def get_wait_time_hours():
    while True:
        try:
            hours = float(input("⏳ Enter number of hours before blocking Roblox (e.g., 2.5): "))
            if hours <= 0:
                print("⚠️ Please enter a positive number.")
                continue
            return hours
        except ValueError:
            print("❌ Invalid input. Please enter a number.")

def main():
    signal.signal(signal.SIGINT, handle_ctrl_c)
    print("🎮 Roblox blocker for current user (no admin required).")
    wait_hours = get_wait_time_hours()
    wait_seconds = wait_hours * 3600

    print(f"⏳ Waiting {wait_hours} hour(s)... Roblox will be blocked after that.")
    try:
        time.sleep(wait_seconds)
    except KeyboardInterrupt:
        handle_ctrl_c(None, None)

    print("\n⏲️ Time's up!")
    try:
        input("👤 Press Enter to block Roblox now (or Ctrl+C to block immediately): ")
    except KeyboardInterrupt:
        handle_ctrl_c(None, None)

    block_everything()

if __name__ == "__main__":
    main()
