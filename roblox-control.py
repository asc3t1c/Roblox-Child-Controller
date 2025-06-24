#!/usr/bin/python
import time
import ctypes
import signal
import sys
import os
import subprocess
import shutil
import win32api
import win32con

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
REDIRECT_IP = "127.0.0.1"
DOMAINS = ["www.roblox.com", "roblox.com"]
BLOCK_ENTRIES = [f"{REDIRECT_IP} {domain}\n" for domain in DOMAINS]
ROBLOX_URL = "https://www.roblox.com/"
FIREWALL_RULE_NAME = "Block Roblox Player"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def unblock_domains(domains):
    with open(HOSTS_PATH, 'r') as file:
        lines = file.readlines()
    with open(HOSTS_PATH, 'w') as file:
        for line in lines:
            if not any(domain in line for domain in domains):
                file.write(line)
    print(f"✅ Domains unblocked: {', '.join(domains)}")
    print(f"🌐 Roblox accessible: {ROBLOX_URL}")

def block_domains(domains, block_entries):
    with open(HOSTS_PATH, 'r+') as file:
        lines = file.readlines()
        for entry in block_entries:
            if entry not in lines:
                file.write(entry)
                print(f"🚫 Blocked domain: {entry.strip().split()[1]}")
            else:
                print(f"⚠️ Domain already blocked: {entry.strip().split()[1]}")
    print(f"🔒 Roblox blocked: {ROBLOX_URL}")

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

def rename_roblox_executables():
    try:
        count = 0
        paths = find_roblox_executables()
        if not paths:
            print("ℹ️ No Roblox executables found to rename.")
            return 0
        for path in paths:
            new_path = path + ".blocked"
            if not os.path.exists(new_path):
                os.rename(path, new_path)
                print(f"🔒 Renamed: {os.path.basename(path)} -> {os.path.basename(new_path)}")
                count += 1
            else:
                print(f"⚠️ Already renamed: {os.path.basename(new_path)}")
        if count == 0:
            print("ℹ️ No executables were renamed (already blocked).")
        return count
    except Exception as e:
        print(f"❌ Rename failed: {e}")
    return 0

def find_roblox_executables():
    user = os.getlogin()
    base_path = rf"C:\\Users\\{user}\\AppData\\Local\\Roblox\\Versions"
    executables = []
    if os.path.exists(base_path):
        for root, _, files in os.walk(base_path):
            for file in files:
                if file == "RobloxPlayerBeta.exe":
                    executables.append(os.path.join(root, file))
    return executables

def uninstall_roblox_app():
    print("\n🪑 Starting Roblox Player uninstall...")

    # Kill Roblox processes first
    try:
        subprocess.run('taskkill /f /im RobloxPlayerBeta.exe', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run('taskkill /f /im RobloxPlayerLauncher.exe', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("🛑 Killed Roblox processes.")
    except Exception as e:
        print(f"⚠️ Failed to kill Roblox processes: {e}")

    # Remove AppData Roblox directory
    user = os.getlogin()
    appdata_path = rf"C:\\Users\\{user}\\AppData\\Local\\Roblox"
    if os.path.exists(appdata_path):
        try:
            shutil.rmtree(appdata_path)
            print(f"🗑️ Removed Roblox AppData: {appdata_path}")
        except Exception as e:
            print(f"❌ Failed to remove AppData folder: {e}")
    else:
        print("ℹ️ Roblox AppData not found.")

    # Try uninstall via WMIC
    try:
        output = subprocess.check_output('wmic product get name', shell=True, text=True)
        for line in output.splitlines():
            if "Roblox" in line:
                name = line.strip()
                print(f"🛠️ Uninstalling with WMIC: {name}")
                subprocess.run(f'wmic product where name="{name}" call uninstall /nointeractive', shell=True)
                break
        else:
            print("ℹ️ Roblox not found in WMIC list.")
    except Exception as e:
        print(f"⚠️ WMIC uninstall failed: {e}")

    # Fallback: PowerShell uninstall
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
        else:
            print("ℹ️ No Roblox packages found in PowerShell.")
    except Exception as e:
        print(f"⚠️ PowerShell uninstall failed: {e}")

def block_everything_and_exit():
    block_domains(DOMAINS, BLOCK_ENTRIES)
    renamed_count = rename_roblox_executables()
    block_roblox_firewall()
    uninstall_roblox_app()
    if renamed_count == 0:
        print("ℹ️ No executables renamed (maybe already blocked). Exiting now.")
        try:
            sys.exit(0)  # Normal exit
        except SystemExit:
            os._exit(0)  # Force immediate exit if sys.exit is caught

def handle_ctrl_c(signum, frame):
    print("\n🚫 Ctrl+C detected! Blocking Roblox and uninstalling before exit...")
    block_everything_and_exit()

def console_event_handler(event):
    if event in (
        win32con.CTRL_C_EVENT,
        win32con.CTRL_CLOSE_EVENT,
        win32con.CTRL_BREAK_EVENT,
        win32con.CTRL_LOGOFF_EVENT,
        win32con.CTRL_SHUTDOWN_EVENT,
    ):
        print("\n⚠️ Termination detected! Blocking Roblox and uninstalling before exit...")
        block_everything_and_exit()
        return True
    return False

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
    signal.signal(signal.SIGINT, handle_ctrl_c)
    win32api.SetConsoleCtrlHandler(console_event_handler, True)

    print("Step 1: Unblocking Roblox domains if needed...")
    unblock_domains(DOMAINS)

    wait_hours = get_wait_time_hours()
    wait_seconds = wait_hours * 3600

    print(f"⏳ Waiting {wait_hours} hour(s)... Roblox is accessible until then.")
    try:
        time.sleep(wait_seconds)
    except KeyboardInterrupt:
        handle_ctrl_c(None, None)

    print("\n⏲️ Time's up!")
    try:
        input("👤 Press Enter to block Roblox (or Ctrl+C — it will still be blocked): ")
    except KeyboardInterrupt:
        handle_ctrl_c(None, None)

    block_everything_and_exit()

if __name__ == "__main__":
    if not is_admin():
        print("⚠️ Please run this script as Administrator.")
        input("Press Enter to exit...")
        sys.exit(1)
    main()
