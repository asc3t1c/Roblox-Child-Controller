import os
import sys
import time
import signal
import ctypes
import subprocess
import shutil
import win32api
import win32con
import atexit

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

cleanup_ran = False

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

def delete_roblox_appdata_for_all_users():
    users_folder = r"C:\Users"
    for user_folder in os.listdir(users_folder):
        if user_folder.lower() in ['default', 'defaultuser0', 'public', 'all users', 'desktop.ini']:
            continue
        appdata_path = os.path.join(users_folder, user_folder, "AppData", "Local", "Roblox")
        if os.path.exists(appdata_path):
            try:
                shutil.rmtree(appdata_path)
                print(f"🗑️ Removed Roblox AppData for user '{user_folder}'")
            except Exception as e:
                print(f"❌ Could not remove AppData for '{user_folder}': {e}")

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
                print(f"🔒 Renamed: {os.path.basename(path)}")
            except Exception as e:
                print(f"❌ Failed to rename {path}: {e}")

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
                    print(f"⚠️ Already blocked: {entry.strip().split()[1]}")
    except PermissionError:
        print("❌ Run as Administrator to block domains.")
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
        print("✅ Unblocked Roblox domains.")
    except Exception as e:
        print(f"❌ Failed to unblock: {e}")

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
            print(f"🔥 Blocked with firewall: {os.path.basename(path)}")
    except Exception as e:
        print(f"⚠️ Firewall error: {e}")

def uninstall_roblox_app():
    print("\n🪑 Uninstalling Roblox...")
    kill_roblox_processes()
    delete_roblox_appdata_for_all_users()

    found = False

    try:
        output = subprocess.check_output('wmic product get name', shell=True, text=True)
        for line in output.splitlines():
            if "Roblox" in line:
                print(f"🛠️ WMIC Uninstall: {line.strip()}")
                subprocess.run(f'wmic product where name="{line.strip()}" call uninstall /nointeractive', shell=True)
                found = True
                break
    except Exception as e:
        print(f"⚠️ WMIC failed: {e}")

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
        print("🎉 Roblox appears to be already uninstalled.")

def remove_roblox_exe_files_all_users():
    print("\n🧹 Scanning system for Roblox .exe files...")
    search_roots = [
        r"C:\Users",
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
        print("ℹ️ No .exe files found.")
    else:
        print(f"✅ Deleted {removed} .exe files.")

def limited_cleanup():
    print("\n🔧 Limited cleanup (process kill, AppData removal, rename .exe)...")
    kill_roblox_processes()
    delete_roblox_appdata_for_all_users()
    rename_roblox_executables_all_users()

def full_block_and_uninstall():
    global cleanup_ran
    if cleanup_ran:
        return
    cleanup_ran = True
    print("\n🔒 Running full cleanup...")
    limited_cleanup()
    block_domains()
    block_roblox_firewall()
    uninstall_roblox_app()
    remove_roblox_exe_files_all_users()
    print("✅ Cleanup complete.")

def on_exit():
    full_block_and_uninstall()

def handle_ctrl_events(ctrl_type):
    if ctrl_type in (win32con.CTRL_CLOSE_EVENT, win32con.CTRL_LOGOFF_EVENT, win32con.CTRL_SHUTDOWN_EVENT):
        print("\n🛑 Windows is closing — cleaning up...")
        full_block_and_uninstall()
        time.sleep(2)  # Give time to see the message
    return True

def get_wait_time_hours():
    while True:
        try:
            hours = float(input("⏳ Enter wait time in hours before blocking Roblox (e.g., 2.5): "))
            if hours <= 0:
                print("Please enter a valid positive number.")
                continue
            return hours
        except ValueError:
            print("❌ Invalid input.")

def main():
    if not is_admin():
        print("🛡️ Requesting Administrator rights...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit(0)

    atexit.register(on_exit)
    win32api.SetConsoleCtrlHandler(handle_ctrl_events, True)
    signal.signal(signal.SIGINT, lambda s, f: on_exit())
    signal.signal(signal.SIGTERM, lambda s, f: on_exit())

    print("✅ Running with Administrator privileges.")
    unblock_domains()
    limited_cleanup()

    wait_hours = get_wait_time_hours()
    print(f"⏳ Roblox access allowed for {wait_hours} hour(s). Close this window or press Ctrl+C to trigger cleanup.")
    try:
        time.sleep(wait_hours * 3600)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user.")

    full_block_and_uninstall()
    input("✅ Press Enter to exit...")

if __name__ == "__main__":
    main()
