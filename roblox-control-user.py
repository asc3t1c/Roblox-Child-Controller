#!/usr/bin/python
import time
import signal
import sys
import os
import subprocess
import shutil

ROBLOX_EXECUTABLES = [
    "RobloxPlayerBeta.exe",
    "RobloxPlayerLauncher.exe",
    "RobloxStudioBeta.exe"
]

def kill_roblox_processes():
    for proc in ROBLOX_EXECUTABLES:
        try:
            subprocess.run(['taskkill', '/F', '/IM', proc], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass  # Ignore if not running

def find_roblox_executables():
    user = os.getlogin()
    base_path = rf"C:\Users\{user}\AppData\Local\Roblox\Versions"
    executables = []
    if os.path.exists(base_path):
        for root, _, files in os.walk(base_path):
            for file in files:
                if file.lower() in [e.lower() for e in ROBLOX_EXECUTABLES]:
                    executables.append(os.path.join(root, file))
    return executables

def rename_roblox_executables():
    count = 0
    paths = find_roblox_executables()
    for path in paths:
        new_path = path + ".blocked"
        if not os.path.exists(new_path):
            try:
                os.rename(path, new_path)
                print(f"🔒 Renamed: {os.path.basename(path)} -> {os.path.basename(new_path)}")
                count += 1
            except Exception as e:
                print(f"⚠️ Could not rename {path}: {e}")
    return count

def remove_roblox_appdata():
    user = os.getlogin()
    appdata_path = rf"C:\Users\{user}\AppData\Local\Roblox"
    if os.path.exists(appdata_path):
        try:
            shutil.rmtree(appdata_path)
            print(f"🗑️ Removed Roblox AppData: {appdata_path}")
        except Exception as e:
            print(f"⚠️ Could not remove AppData folder: {e}")
    else:
        print("ℹ️ Roblox AppData not found.")

def remove_roblox_exe_files():
    user_dir = os.path.expanduser("~")
    search_dirs = [
        os.path.join(user_dir, "Downloads"),
        os.environ.get("TEMP", r"C:\Windows\Temp"),
        rf"C:\Users\{os.getlogin()}\AppData\Local\Roblox"
    ]

    count = 0
    for search_root in search_dirs:
        for root, _, files in os.walk(search_root):
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
        print("ℹ️ No .exe files deleted.")
    else:
        print(f"✅ Removed {count} Roblox .exe file(s).")

def block_roblox_user_level():
    kill_roblox_processes()
    remove_roblox_appdata()
    rename_roblox_executables()
    remove_roblox_exe_files()
    print("✅ Roblox blocked (user-level).")

def handle_exit(signum, frame):
    print("\n🚫 Ctrl+C detected. Blocking Roblox now...")
    block_roblox_user_level()
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    try:
        wait_hours = float(input("⏳ Enter hours to wait before blocking Roblox: "))
        if wait_hours <= 0:
            print("⚠️ Please enter a number greater than 0.")
            return
    except ValueError:
        print("❌ Invalid input.")
        return

    try:
        print(f"⏳ Waiting {wait_hours} hour(s)... Press Ctrl+C to block early.")
        time.sleep(wait_hours * 3600)
    except KeyboardInterrupt:
        handle_exit(None, None)

    print("\n⏲️ Time's up! Blocking Roblox now...")
    block_roblox_user_level()

if __name__ == "__main__":
    main()
