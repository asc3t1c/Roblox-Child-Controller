#!/usr/bin/python
# by nu11secur1ty

import os
import sys
import time
import signal
import ctypes
import subprocess
import shutil
import string

import win32api
import win32con

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
REDIRECT_IP = "127.0.0.1"
DOMAINS = ["www.roblox.com", "roblox.com"]
BLOCK_ENTRIES = [f"{REDIRECT_IP} {domain}\n" for domain in DOMAINS]
FIREWALL_RULE_NAME = "Block Roblox Player"

ROBLOX_EXE_NAMES = [
    "RobloxPlayerBeta.exe",
    "RobloxPlayerLauncher.exe",
    "RobloxStudioLauncherBeta.exe",
    "RobloxStudioBeta.exe"
]

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def kill_roblox_processes():
    for proc in ROBLOX_EXE_NAMES:
        try:
            subprocess.run(['taskkill', '/F', '/IM', proc], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"🔪 Killed process: {proc}", flush=True)
        except Exception as e:
            print(f"⚠️ Could not kill {proc}: {e}", flush=True)

def delete_roblox_appdata_for_all_users():
    users_folder = r"C:\Users"
    for user_folder in os.listdir(users_folder):
        if user_folder.lower() in ['default', 'defaultuser0', 'public', 'all users', 'desktop.ini']:
            continue
        appdata_path = os.path.join(users_folder, user_folder, "AppData", "Local", "Roblox")
        if os.path.exists(appdata_path):
            try:
                shutil.rmtree(appdata_path)
                print(f"🗑️ Removed Roblox AppData for user '{user_folder}'", flush=True)
            except Exception as e:
                print(f"❌ Could not remove AppData for '{user_folder}': {e}", flush=True)

def find_roblox_executables_all_users():
    users_folder = r"C:\Users"
    executables = []
    for user_folder in os.listdir(users_folder):
        if user_folder.lower() in ['default', 'defaultuser0', 'public', 'all users', 'desktop.ini']:
            continue
        base_path = os.path.join(users_folder, user_folder, "AppData", "Local", "Roblox", "Versions")
        if os.path.exists(base_path):
            for root, _, files in os.walk(base_path):
                for file in files:
                    if file.lower() in (name.lower() for name in ROBLOX_EXE_NAMES):
                        executables.append(os.path.join(root, file))
    return executables

def rename_roblox_executables_all_users():
    paths = find_roblox_executables_all_users()
    for path in paths:
        new_path = path + ".blocked"
        if not os.path.exists(new_path):
            try:
                os.rename(path, new_path)
                print(f"🔒 Renamed: {os.path.basename(path)}", flush=True)
            except Exception as e:
                print(f"❌ Failed to rename {path}: {e}", flush=True)

def block_domains():
    try:
        with open(HOSTS_PATH, 'r+') as file:
            lines = file.readlines()
            file.seek(0, os.SEEK_END)
            for entry in BLOCK_ENTRIES:
                if entry not in lines:
                    file.write(entry)
                    print(f"🚫 Blocked domain: {entry.strip().split()[1]}", flush=True)
                else:
                    print(f"⚠️ Already blocked: {entry.strip().split()[1]}", flush=True)
    except PermissionError:
        print("❌ Run as Administrator to block domains.", flush=True)
    except Exception as e:
        print(f"❌ Failed to block domains: {e}", flush=True)

def unblock_domains():
    try:
        with open(HOSTS_PATH, 'r') as file:
            lines = file.readlines()
        with open(HOSTS_PATH, 'w') as file:
            for line in lines:
                if not any(domain in line for domain in DOMAINS):
                    file.write(line)
        print("✅ Unblocked Roblox domains.", flush=True)
    except Exception as e:
        print(f"❌ Failed to unblock: {e}", flush=True)

def block_roblox_firewall():
    try:
        roblox_paths = find_roblox_executables_all_users()
        for path in roblox_paths:
            subprocess.run([
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name={FIREWALL_RULE_NAME}",
                "dir=out", "action=block", f"program={path}",
                "enable=yes"
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"🔥 Blocked with firewall: {os.path.basename(path)}", flush=True)
    except Exception as e:
        print(f"⚠️ Firewall error: {e}", flush=True)

def uninstall_roblox_app():
    print("\n🪑 Uninstalling Roblox...", flush=True)
    kill_roblox_processes()
    delete_roblox_appdata_for_all_users()

    found = False

    try:
        output = subprocess.check_output('wmic product get name', shell=True, text=True)
        for line in output.splitlines():
            if "Roblox" in line:
                print(f"🛠️ WMIC Uninstall: {line.strip()}", flush=True)
                subprocess.run(f'wmic product where name="{line.strip()}" call uninstall /nointeractive', shell=True)
                found = True
                break
    except Exception as e:
        print(f"⚠️ WMIC failed: {e}", flush=True)

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
        print(f"⚠️ PowerShell uninstall failed: {e}", flush=True)

    if not found:
        print("🎉 Roblox appears to be already uninstalled.", flush=True)

def get_fixed_drives():
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drive_path = f"{letter}:\\"
            if ctypes.windll.kernel32.GetDriveTypeW(drive_path) == 3:  # DRIVE_FIXED = 3
                drives.append(drive_path)
        bitmask >>= 1
    return drives

def remove_all_roblox_exe_files():
    print("\n🧹 Scanning all fixed drives for Roblox .exe files...", flush=True)
    drives = get_fixed_drives()
    removed = 0
    found_files = []

    for drive in drives:
        for root, _, files in os.walk(drive):
            for file in files:
                if "roblox" in file.lower() and file.lower().endswith(".exe"):
                    full_path = os.path.join(root, file)
                    found_files.append(full_path)
                    try:
                        os.remove(full_path)
                        print(f"🗑️ Deleted: {full_path}", flush=True)
                        removed += 1
                    except Exception as e:
                        print(f"⚠️ Could not delete {full_path}: {e}", flush=True)

    if removed == 0:
        if found_files:
            print("⚠️ Found Roblox .exe files but couldn't delete them (permission issues?).", flush=True)
            for f in found_files:
                print(f"  -> {f}", flush=True)
        else:
            print("ℹ️ No Roblox .exe files found.", flush=True)
    else:
        print(f"✅ Deleted {removed} Roblox .exe files.", flush=True)

def limited_cleanup():
    print("\n🔧 Limited cleanup (process kill, AppData removal, rename .exe)...", flush=True)
    kill_roblox_processes()
    delete_roblox_appdata_for_all_users()
    rename_roblox_executables_all_users()

def full_block_and_uninstall():
    limited_cleanup()
    print("\n🔒 Admin-level cleanup...", flush=True)
    block_domains()
    block_roblox_firewall()
    uninstall_roblox_app()
    remove_all_roblox_exe_files()
    print("\n✅ All cleanup completed. Exiting.", flush=True)
    sys.exit(0)

def handle_exit_signal(signum, frame):
    print("\n🚨 Exit signal caught! Performing cleanup now...", flush=True)
    full_block_and_uninstall()

def get_wait_time_hours():
    print("\n⏳ Choose Roblox allowed access time:", flush=True)
    print("  1) 1 hour", flush=True)
    print("  2) 2 hours", flush=True)
    print("  3) 3 hours", flush=True)
    print("  4) Custom time in hours", flush=True)
    while True:
        try:
            choice = input("Select option (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n🛑 Input interrupted, starting cleanup...", flush=True)
            full_block_and_uninstall()

        if choice == '1':
            return 1.0
        elif choice == '2':
            return 2.0
        elif choice == '3':
            return 3.0
        elif choice == '4':
            while True:
                try:
                    hours = input("Enter custom hours (positive number): ").strip()
                    if hours.lower() in ['exit', 'quit']:
                        print("\n🛑 Exit requested, starting cleanup...", flush=True)
                        full_block_and_uninstall()
                    hours = float(hours)
                    if hours > 0:
                        return hours
                    else:
                        print("Please enter a positive number.", flush=True)
                except ValueError:
                    print("Invalid input. Please enter a numeric value.", flush=True)
                except (EOFError, KeyboardInterrupt):
                    print("\n🛑 Input interrupted, starting cleanup...", flush=True)
                    full_block_and_uninstall()
        else:
            print("Invalid option. Please choose 1, 2, 3, or 4.", flush=True)

def main():
    if not is_admin():
        print("❌ You must run this script as Administrator!", flush=True)
        sys.exit(1)

    signal.signal(signal.SIGINT, handle_exit_signal)
    signal.signal(signal.SIGTERM, handle_exit_signal)

    print("✅ Running with Administrator privileges.", flush=True)
    unblock_domains()
    limited_cleanup()

    wait_hours = get_wait_time_hours()
    print(f"\n⏳ Roblox access allowed for {wait_hours} hour(s). Press Ctrl+C or close terminal to stop early.", flush=True)

    try:
        time.sleep(wait_hours * 3600)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted — starting cleanup.", flush=True)

    full_block_and_uninstall()

if __name__ == "__main__":
    main()
