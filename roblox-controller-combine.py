#!/usr/bin/python
# by nu11secur1ty - Roblox timer & enforced cleanup

import os
import sys
import time
import signal
import ctypes
import subprocess
import shutil
import string
from ctypes import wintypes

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
    except:
        return False

def kill_roblox_processes():
    for proc in ROBLOX_EXE_NAMES:
        subprocess.run(['taskkill', '/F', '/IM', proc], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def delete_roblox_appdata_for_all_users():
    users_folder = r"C:\Users"
    for user in os.listdir(users_folder):
        path = os.path.join(users_folder, user, "AppData", "Local", "Roblox")
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
            except: pass

def find_roblox_executables():
    paths = []
    for drive in get_fixed_drives():
        for root, _, files in os.walk(drive):
            for file in files:
                if file.lower().endswith("roblox.exe") or "roblox" in file.lower() and file.lower().endswith(".exe"):
                    paths.append(os.path.join(root, file))
    return paths

def delete_all_roblox_exes():
    files = find_roblox_executables()
    for path in files:
        try:
            os.remove(path)
        except: pass

def block_domains():
    try:
        with open(HOSTS_PATH, 'r+') as f:
            lines = f.readlines()
            f.seek(0, os.SEEK_END)
            for entry in BLOCK_ENTRIES:
                if entry not in lines:
                    f.write(entry)
    except: pass

def unblock_domains():
    try:
        with open(HOSTS_PATH, 'r') as f:
            lines = f.readlines()
        with open(HOSTS_PATH, 'w') as f:
            for line in lines:
                if not any(domain in line for domain in DOMAINS):
                    f.write(line)
    except: pass

def block_roblox_firewall():
    try:
        for path in find_roblox_executables():
            subprocess.run([
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name={FIREWALL_RULE_NAME}",
                "dir=out", "action=block", f"program={path}",
                "enable=yes"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass

def uninstall_roblox_app():
    kill_roblox_processes()
    delete_roblox_appdata_for_all_users()

def get_fixed_drives():
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for i, letter in enumerate(string.ascii_uppercase):
        if bitmask & (1 << i):
            drive = f"{letter}:\\"
            if ctypes.windll.kernel32.GetDriveTypeW(drive) == 3:
                drives.append(drive)
    return drives

def final_cleanup_and_exit():
    try:
        block_domains()
        block_roblox_firewall()
        uninstall_roblox_app()
        delete_all_roblox_exes()
    except: pass
    sys.exit(0)

def wait_choice():
    print("⏳ Select Roblox usage time:")
    print("1) 1 hour\n2) 2 hours\n3) 3 hours\n4) Custom")
    while True:
        opt = input("Choose (1-4): ").strip()
        if opt in ['1', '2', '3']:
            return int(opt)
        elif opt == '4':
            try:
                h = float(input("Enter hours: ").strip())
                if h > 0: return h
            except: pass
        print("❌ Invalid choice. Try again.")

# ========== HANDLE CMD X-BUTTON CLOSE ==========

CTRL_C_EVENT = 0
CTRL_CLOSE_EVENT = 2
PHANDLER_ROUTINE = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)

@PHANDLER_ROUTINE
def console_ctrl_handler(ctrl_type):
    if ctrl_type in (CTRL_C_EVENT, CTRL_CLOSE_EVENT):
        print("\n⚠️ CTRL+C or Close detected! Cleaning up...")
        final_cleanup_and_exit()
    return False

# Register handler
ctypes.windll.kernel32.SetConsoleCtrlHandler(console_ctrl_handler, True)

# ========== END ==========

def main():
    if not is_admin():
        print("❌ Please run as Administrator.")
        time.sleep(2)
        sys.exit(1)

    signal.signal(signal.SIGINT, lambda s, f: final_cleanup_and_exit())
    signal.signal(signal.SIGTERM, lambda s, f: final_cleanup_and_exit())

    unblock_domains()
    kill_roblox_processes()
    delete_roblox_appdata_for_all_users()

    hours = wait_choice()
    print(f"\n✅ Roblox allowed for {hours} hour(s). Press Ctrl+C or close window to stop early.\n")
    try:
        time.sleep(hours * 3600)
    except:
        pass

    final_cleanup_and_exit()

if __name__ == "__main__":
    main()
