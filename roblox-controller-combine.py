#!/usr/bin/env python
# Child-proof Roblox destroyer by OpenAI's assistant

import os
import sys
import ctypes
import shutil
import subprocess
import string
import signal
import time

# === CONFIGURATION ===
HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
DOMAINS = ["roblox.com", "www.roblox.com"]
ROBLOX_EXE_NAME = "roblox.exe"
APPDATA_FOLDER_NAME = "Roblox"

# === CHECK FOR ADMIN PRIVILEGES ===
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# === UNINSTALL ROBLOX APPLICATION ===
def uninstall_roblox_app():
    found = False
    print("🪛 Uninstalling Roblox...")
    try:
        output = subprocess.check_output('wmic product get name', shell=True, text=True)
        for line in output.splitlines():
            if "Roblox" in line:
                print(f"🛠️ Found via WMIC: {line.strip()}")
                subprocess.run(f'wmic product where name="{line.strip()}" call uninstall /nointeractive', shell=True)
                found = True
                break
    except Exception as e:
        print(f"⚠️ WMIC error: {e}")

    try:
        ps_check = subprocess.run([
            'powershell', '-Command', 'Get-Package -Name *Roblox*'
        ], capture_output=True, text=True)
        if "Roblox" in ps_check.stdout:
            subprocess.run([
                'powershell', '-Command',
                'Get-Package -Name *Roblox* | Uninstall-Package -Force'
            ], capture_output=True, text=True)
            found = True
    except Exception as e:
        print(f"⚠️ PowerShell uninstall failed: {e}")

    if not found:
        print("✅ Roblox app appears already removed.")

# === DELETE ROBLOX.EXE FILES ACROSS ALL FIXED DRIVES ===
def delete_all_roblox_exe():
    print("🧹 Scanning for roblox.exe files...")
    drives = get_fixed_drives()
    deleted = 0

    for drive in drives:
        for root, _, files in os.walk(drive):
            for file in files:
                if file.lower() == ROBLOX_EXE_NAME:
                    path = os.path.join(root, file)
                    try:
                        os.remove(path)
                        print(f"🗑️ Deleted: {path}")
                        deleted += 1
                    except Exception as e:
                        print(f"❌ Failed to delete {path}: {e}")

    if deleted == 0:
        print("ℹ️ No roblox.exe files found.")
    else:
        print(f"✅ Deleted {deleted} roblox.exe files.")

# === DELETE ROBLOX APPDATA FOR ALL USERS ===
def delete_appdata_for_all_users():
    print("🧹 Deleting Roblox AppData for all users...")
    users_dir = r"C:\Users"
    for user in os.listdir(users_dir):
        if user.lower() in ['default', 'public', 'all users', 'defaultuser0']:
            continue
        path = os.path.join(users_dir, user, 'AppData', 'Local', APPDATA_FOLDER_NAME)
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                print(f"🗑️ Deleted AppData for user '{user}'")
            except Exception as e:
                print(f"❌ Could not remove AppData for {user}: {e}")

# === BLOCK ROBLOX DOMAINS IN HOSTS FILE ===
def block_domains_in_hosts():
    print("🔒 Blocking roblox.com domains...")
    try:
        with open(HOSTS_PATH, 'r+') as f:
            content = f.readlines()
            f.seek(0, os.SEEK_END)
            for domain in DOMAINS:
                entry = f"127.0.0.1 {domain}\n"
                if not any(domain in line for line in content):
                    f.write(entry)
                    print(f"🚫 Blocked: {domain}")
                else:
                    print(f"⚠️ Already blocked: {domain}")
    except Exception as e:
        print(f"❌ Could not modify hosts file: {e}")

# === GET FIXED DRIVES ON SYSTEM ===
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

# === CLEANUP FUNCTION CALLED ON INTERRUPT ===
def full_cleanup_and_exit():
    print("\n🚨 Interruption detected! Starting full cleanup...")
    uninstall_roblox_app()
    delete_all_roblox_exe()
    delete_appdata_for_all_users()
    block_domains_in_hosts()
    print("✅ Cleanup complete. Exiting.")
    sys.exit(0)

# === MAIN FUNCTION ===
def main():
    if not is_admin():
        print("❌ Please run this script as Administrator.")
        sys.exit(1)

    # Handle Ctrl+C
    signal.signal(signal.SIGINT, lambda signum, frame: full_cleanup_and_exit())
    signal.signal(signal.SIGTERM, lambda signum, frame: full_cleanup_and_exit())

    # Handle CMD X Close
    try:
        import win32api
        win32api.SetConsoleCtrlHandler(lambda _: full_cleanup_and_exit(), True)
    except ImportError:
        print("⚠️ Please install pywin32 for full CMD protection: pip install pywin32")

    print("✅ Running... waiting for interruption (Ctrl+C or closing CMD window).")
    print("🛡️ If the child tries to stop me, I will uninstall and wipe Roblox from this PC.")

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
