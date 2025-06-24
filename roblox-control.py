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
FIREWALL_RULE_NAME = "Block Roblox Player"
ROBLOX_APPDATA_REL = r"AppData\Local\Roblox"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def unblock_domains(domains):
    try:
        with open(HOSTS_PATH, 'r') as file:
            lines = file.readlines()
        with open(HOSTS_PATH, 'w') as file:
            for line in lines:
                if not any(domain in line for domain in domains):
                    file.write(line)
        print(f"✅ Domains unblocked: {', '.join(domains)}")
    except Exception as e:
        print(f"❌ Failed to unblock domains: {e}")

def block_domains(domains, block_entries):
    try:
        with open(HOSTS_PATH, 'r+') as file:
            lines = file.readlines()
            for entry in block_entries:
                if entry not in lines:
                    file.write(entry)
                    print(f"🚫 Blocked domain: {entry.strip().split()[1]}")
                else:
                    print(f"⚠️ Domain already blocked: {entry.strip().split()[1]}")
        print(f"🔒 Roblox domains blocked.")
    except Exception as e:
        print(f"❌ Failed to block domains: {e}")

def find_roblox_executables():
    user = os.getlogin()
    base_path = rf"C:\Users\{user}\AppData\Local\Roblox\Versions"
    executables = []
    if os.path.exists(base_path):
        for root, _, files in os.walk(base_path):
            for file in files:
                if file == "RobloxPlayerBeta.exe":
                    executables.append(os.path.join(root, file))
    return executables

def rename_roblox_executables():
    count = 0
    try:
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
    except Exception as e:
        print(f"❌ Rename failed: {e}")
    return count

def restore_roblox_executables():
    restored_count = 0
    try:
        paths = find_roblox_executables()
        # Check for .blocked files instead
        user = os.getlogin()
        base_path = rf"C:\Users\{user}\AppData\Local\Roblox\Versions"
        for root, _, files in os.walk(base_path):
            for file in files:
                if file.endswith(".blocked"):
                    old_path = os.path.join(root, file)
                    new_path = old_path[:-8]  # remove ".blocked"
                    if not os.path.exists(new_path):
                        os.rename(old_path, new_path)
                        print(f"✅ Restored executable: {file} -> {os.path.basename(new_path)}")
                        restored_count += 1
                    else:
                        print(f"⚠️ Target file exists, skipping restore: {new_path}")
        if restored_count == 0:
            print("ℹ️ No renamed executables found to restore.")
    except Exception as e:
        print(f"❌ Restore failed: {e}")
    return restored_count

def block_roblox_firewall():
    try:
        paths = find_roblox_executables()
        if not paths:
            print("ℹ️ No Roblox executables found for firewall blocking.")
            return
        for path in paths:
            subprocess.run([
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name={FIREWALL_RULE_NAME}",
                "dir=out", "action=block", f"program={path}",
                "enable=yes"
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"🔥 Firewall blocked: {os.path.basename(path)}")
    except Exception as e:
        print(f"⚠️ Firewall blocking failed: {e}")

def unblock_roblox_firewall():
    try:
        subprocess.run([
            "netsh", "advfirewall", "firewall", "delete", "rule",
            f"name={FIREWALL_RULE_NAME}"
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Firewall rules removed.")
    except Exception as e:
        print(f"❌ Failed to remove firewall rules: {e}")

def kill_roblox_processes():
    try:
        subprocess.run('taskkill /f /im RobloxPlayerBeta.exe', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run('taskkill /f /im RobloxPlayerLauncher.exe', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("🛑 Killed Roblox processes.")
    except Exception as e:
        print(f"⚠️ Failed to kill Roblox processes: {e}")

def remove_roblox_appdata():
    user = os.getlogin()
    appdata_path = rf"C:\Users\{user}\{ROBLOX_APPDATA_REL}"
    if os.path.exists(appdata_path):
        try:
            shutil.rmtree(appdata_path, onerror=on_rm_error)
            print(f"🗑️ Removed Roblox AppData: {appdata_path}")
        except Exception as e:
            print(f"❌ Failed to remove AppData folder: {e}")
    else:
        print("ℹ️ Roblox AppData not found.")

def on_rm_error(func, path, exc_info):
    import stat
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def uninstall_roblox_app():
    print("\n🪑 Starting Roblox Player uninstall...")

    kill_roblox_processes()
    remove_roblox_appdata()

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

    # PowerShell uninstall fallback
    try:
        ps_check = subprocess.run([
            'powershell', '-Command', 'Get-AppxPackage *Roblox* | Select Name, PackageFullName'
        ], capture_output=True, text=True)
        if "Roblox" in ps_check.stdout:
            print("🛠️ Attempting PowerShell uninstall...")
            uninstall_ps = subprocess.run([
                'powershell', '-Command',
                'Get-AppxPackage *Roblox* | Remove-AppxPackage'
            ], capture_output=True, text=True)
            if uninstall_ps.returncode == 0:
                print("✅ Roblox app uninstalled via PowerShell.")
            else:
                print(f"❌ PowerShell uninstall returned code {uninstall_ps.returncode}")
        else:
            print("ℹ️ No Roblox packages found in PowerShell.")
    except Exception as e:
        print(f"⚠️ PowerShell uninstall failed: {e}")

def block_everything():
    block_domains(DOMAINS, BLOCK_ENTRIES)
    rename_roblox_executables()
    block_roblox_firewall()

def uninstall_everything():
    unblock_domains(DOMAINS)
    unblock_roblox_firewall()
    restore_roblox_executables()
    uninstall_roblox_app()

def handle_ctrl_c(signum, frame):
    print("\n🚫 Ctrl+C detected! Running uninstall before exit...")
    uninstall_everything()
    print("✅ Uninstall and cleanup done. Exiting.")
    sys.exit(0)

def console_event_handler(event):
    if event in (
        win32con.CTRL_C_EVENT,
        win32con.CTRL_CLOSE_EVENT,
        win32con.CTRL_BREAK_EVENT,
        win32con.CTRL_LOGOFF_EVENT,
        win32con.CTRL_SHUTDOWN_EVENT,
    ):
        print("\n⚠️ Termination detected! Running uninstall before exit...")
        uninstall_everything()
        print("✅ Uninstall and cleanup done. Exiting.")
        sys.exit(0)
    return False

def get_wait_time_hours():
    while True:
        try:
            hours = float(input("⏳ Enter hours to wait before blocking Roblox (e.g., 3 or 1.5): "))
            if hours <= 0:
                print("❌ Please enter a positive number.")
                continue
            return hours
        except ValueError:
            print("❌ Invalid input. Enter a number like 3 or 1.5.")

def main_block():
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

    print("Blocking Roblox now...")
    block_everything()
    print("✅ Roblox blocked. Exiting.")
    sys.exit(0)

def main_uninstall():
    print("🧹 Running uninstall and cleanup...")
    uninstall_everything()
    print("✅ Uninstall and cleanup done. Exiting.")
    sys.exit(0)

if __name__ == "__main__":
    if not is_admin():
        print("⚠️ Please run this script as Administrator.")
        input("Press Enter to exit...")
        sys.exit(1)

    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        mode = "block"

    if mode == "block":
        main_block()
    elif mode == "uninstall":
        main_uninstall()
    else:
        print("❌ Unknown mode. Use 'block' or 'uninstall'.")
        sys.exit(1)
