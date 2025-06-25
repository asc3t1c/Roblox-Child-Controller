#!/usr/bin/python
import os
import sys
import time
import signal
import ctypes
import subprocess
import shutil
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
            print(f"🔪 Killed process: {proc}")
        except Exception as e:
            print(f"⚠️ Could not kill {proc}: {e}")

def remove_roblox_appdata():
    user = os.getlogin()
    appdata_path = rf"C:\Users\{user}\AppData\Local\Roblox"
    max_attempts = 5
    for attempt in range(max_attempts):
        if os.path.exists(appdata_path):
            try:
                shutil.rmtree(appdata_path)
                print(f"🗑️ Removed Roblox AppData: {appdata_path}")
                return True
            except Exception as e:
                print(f"❌ Attempt {attempt+1}: Failed to remove AppData folder: {e}")
                time.sleep(2)
        else:
            print("ℹ️ Roblox AppData folder not found.")
            return True
    print("⚠️ Failed to remove Roblox AppData after multiple attempts.")
    return False

def find_roblox_executables():
    user = os.getlogin()
    base_path = rf"C:\Users\{user}\AppData\Local\Roblox\Versions"
    executables = []
    if os.path.exists(base_path):
        for root, _, files in os.walk(base_path):
            for file in files:
                if file.lower() in (name.lower() for name in ROBLOX_EXE_NAMES):
                    executables.append(os.path.join(root, file))
    return executables

def rename_roblox_executables():
    count = 0
    paths = find_roblox_executables()
    if not paths:
        print("ℹ️ No Roblox executables found to rename.")
        return 0
    for path in paths:
        new_path = path + ".blocked"
        if not os.path.exists(new_path):
            try:
                os.rename(path, new_path)
                print(f"🔒 Renamed: {os.path.basename(path)} -> {os.path.basename(new_path)}")
                count += 1
            except Exception as e:
                print(f"❌ Failed to rename {path}: {e}")
        else:
            print(f"⚠️ Already renamed: {os.path.basename(new_path)}")
    return count

def block_domains():
    try:
        with open(HOSTS_PATH, 'r+') as file:
            lines = file.readlines()
            file.seek(0, os.SEEK_END)
            for entry in BLOCK_ENTRIES:
                if entry not in lines:
                    file.write(entry)
                    print(f"🚫 Blocked domain: {entry.strip().split()[1]}")
                else:
                    print(f"⚠️ Domain already blocked: {entry.strip().split()[1]}")
        print("🔒 Roblox domains blocked.")
    except PermissionError:
        print("❌ Permission denied: Run as Administrator to block domains.")
    except Exception as e:
        print(f"❌ Failed to block domains: {e}")

def unblock_domains():
    try:
        with open(HOSTS_PATH, 'r') as file:
            lines = file.readlines()
        with open(HOSTS_PATH, 'w') as file:
            for line in lines:
                if not any(domain in line for domain in DOMAINS):
                    file.write(line)
        print(f"✅ Domains unblocked: {', '.join(DOMAINS)}")
    except Exception as e:
        print(f"❌ Failed to unblock domains: {e}")

def block_roblox_firewall():
    try:
        roblox_paths = find_roblox_executables()
        if not roblox_paths:
            print("ℹ️ No Roblox executables found for firewall blocking.")
            return
        for path in roblox_paths:
            subprocess.run([
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name={FIREWALL_RULE_NAME}",
                "dir=out", "action=block", f"program={path}",
                "enable=yes"
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"🔥 Firewall blocked: {os.path.basename(path)}")
    except Exception as e:
        print(f"⚠️ Firewall blocking failed: {e}")

def uninstall_roblox_app():
    print("\n🪑 Starting Roblox Player uninstall...")
    kill_roblox_processes()

    if not remove_roblox_appdata():
        print("⚠️ Proceeding even though AppData folder removal failed.")

    found = False

    # Try uninstall via WMIC
    try:
        output = subprocess.check_output('wmic product get name', shell=True, text=True)
        for line in output.splitlines():
            name = line.strip()
            if not name:
                continue
            if "Roblox" in name:
                print(f"🛠️ Uninstalling with WMIC: {name}")
                subprocess.run(f'wmic product where name="{name}" call uninstall /nointeractive', shell=True, check=True)
                found = True
                break
    except Exception as e:
        print(f"⚠️ WMIC uninstall failed: {e}")

    # Try PowerShell uninstall
    try:
        ps_check = subprocess.run([
            'powershell', '-Command', 'Get-Package -Name *Roblox*'
        ], capture_output=True, text=True)
        if "Roblox" in ps_check.stdout:
            print("🛠️ Attempting PowerShell uninstall...")
            subprocess.run([
                'powershell', '-Command',
                'Get-Package -Name *Roblox* | Uninstall-Package -Force'
            ], capture_output=True, text=True)
            found = True
        else:
            print("✅ PowerShell: No Roblox packages found (likely already removed).")
    except Exception as e:
        print(f"⚠️ PowerShell uninstall failed: {e}")

    if not found:
        print("🎉 Roblox appears to already be uninstalled.")

def remove_roblox_exe_files():
    print("\n🧹 Searching for Roblox .exe files...")

    search_roots = [
        os.environ.get("USERPROFILE", r"C:\Users"),
        r"C:\Windows\Temp",
        r"C:\ProgramData",
        r"C:\Program Files",
        r"C:\Program Files (x86)"
    ]

    removed = 0
    for root_dir in search_roots:
        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.lower().startswith("roblox") and file.lower().endswith(".exe"):
                    full_path = os.path.join(root, file)
                    try:
                        os.remove(full_path)
                        print(f"🗑️ Deleted: {full_path}")
                        removed += 1
                    except Exception as e:
                        print(f"⚠️ Could not delete {full_path}: {e}")
    if removed == 0:
        print("ℹ️ No Roblox .exe files found.")
    else:
        print(f"✅ Removed {removed} Roblox .exe file(s).")

def limited_cleanup():
    print("\n🔧 Running limited cleanup (kill processes, remove AppData, rename exe)...")
    kill_roblox_processes()
    remove_roblox_appdata()
    rename_roblox_executables()

def full_block_and_uninstall(admin_mode):
    # Run limited cleanup first
    limited_cleanup()

    # Then if admin, run full blocking
    if admin_mode:
        print("\n🔒 Running admin-level blocking and uninstall...")
        block_domains()
        block_roblox_firewall()
        uninstall_roblox_app()
        remove_roblox_exe_files()
    else:
        print("\n⚠️ Not running as admin — skipping domain blocking and uninstall.")

    print("🚪 Cleanup and blocking done. Exiting.")
    sys.exit(0)

def handle_exit_signal(signum, frame):
    print("\n🚨 Exit signal caught! Running cleanup and blocking now...")
    full_block_and_uninstall(is_admin())

def get_wait_time_hours():
    while True:
        try:
            hours = float(input("⏳ Enter hours to wait before blocking Roblox (e.g., 3 or 1.5): "))
            if hours <= 0:
                print("Please enter a positive number.")
                continue
            return hours
        except ValueError:
            print("❌ Invalid input. Enter a number like 3 or 1.5.")

def main():
    signal.signal(signal.SIGINT, handle_exit_signal)
    signal.signal(signal.SIGTERM, handle_exit_signal)

    admin = is_admin()
    print(f"🛡️ Running as admin: {admin}")

    print("Step 1: Unblocking Roblox domains if needed...")
    unblock_domains()

    print("\nStep 2: Initial limited cleanup...")
    limited_cleanup()

    if admin:
        wait_hours = get_wait_time_hours()
        print(f"⏳ Waiting {wait_hours} hour(s)... Roblox is accessible until then. Press Ctrl+C to block now.")
        try:
            time.sleep(wait_hours * 3600)
        except KeyboardInterrupt:
            print("\n🛑 Interrupted early - proceeding with cleanup...")

        full_block_and_uninstall(admin_mode=True)
    else:
        print("\n⚠️ Not admin — limited cleanup done, exiting now.")
        sys.exit(0)

if __name__ == "__main__":
    main()
