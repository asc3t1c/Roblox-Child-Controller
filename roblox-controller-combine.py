#!/usr/bin/env python
# Author: nu11secur1ty - final safe cleanup for roblox.exe

import os
import sys
import time
import signal
import ctypes
import shutil
import subprocess
import string

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_fixed_drives():
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            path = f"{letter}:/"
            if ctypes.windll.kernel32.GetDriveTypeW(path) == 3:
                drives.append(path)
        bitmask >>= 1
    return drives

def kill_roblox_processes():
    for proc in ["roblox.exe"]:
        subprocess.run(['taskkill', '/F', '/IM', proc], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def delete_roblox_appdata_for_all_users():
    users_dir = r"C:\Users"
    for user in os.listdir(users_dir):
        if user.lower() in ['default', 'public', 'all users', 'defaultuser0']:
            continue
        roblox_path = os.path.join(users_dir, user, 'AppData', 'Local', 'Roblox')
        if os.path.exists(roblox_path):
            try:
                shutil.rmtree(roblox_path)
                print(f"🗑️ Deleted AppData for user: {user}")
            except Exception as e:
                print(f"⚠️ Could not delete {roblox_path}: {e}")

def remove_all_roblox_exe_files():
    print("🔍 Searching for roblox.exe across all drives...")
    count = 0
    for drive in get_fixed_drives():
        for root, _, files in os.walk(drive):
            for f in files:
                if f.lower() == "roblox.exe":
                    path = os.path.join(root, f)
                    try:
                        os.remove(path)
                        print(f"🗑️ Deleted: {path}")
                        count += 1
                    except Exception as e:
                        print(f"⚠️ Cannot delete {path}: {e}")
    if count == 0:
        print("✅ No roblox.exe found.")
    else:
        print(f"✅ Deleted {count} roblox.exe files.")

def full_cleanup():
    print("\n🧹 Final cleanup triggered!")
    kill_roblox_processes()
    delete_roblox_appdata_for_all_users()
    remove_all_roblox_exe_files()
    print("✅ Cleanup complete. Goodbye!")
    sys.exit(0)

def handle_exit(signum, frame):
    print("\n🚨 Exit attempt caught (Ctrl+C or X).")
    full_cleanup()

def get_wait_time_hours():
    print("\n⏳ Choose Roblox allowed access time:")
    print("  1) 1 hour")
    print("  2) 2 hours")
    print("  3) 3 hours")
    print("  4) Custom hours")
    while True:
        choice = input("Select option (1-4): ").strip()
        if choice == '1': return 1
        if choice == '2': return 2
        if choice == '3': return 3
        if choice == '4':
            try:
                hours = float(input("Enter number of hours: ").strip())
                if hours > 0:
                    return hours
            except:
                pass
        print("❌ Invalid input. Try again.")

def main():
    if not is_admin():
        print("❌ Please run this script as Administrator.")
        sys.exit(1)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    print("✅ Running with Admin rights.")
    hours = get_wait_time_hours()
    print(f"\n🔓 Roblox is allowed for {hours} hour(s). Press Ctrl+C or close window to stop early.")

    try:
        time.sleep(hours * 3600)
    except:
        print("\n🛑 Interrupted...")

    full_cleanup()

if __name__ == "__main__":
    main()
