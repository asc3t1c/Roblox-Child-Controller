#!/usr/bin/python
import os
import sys
import ctypes
import subprocess
import shutil
import time
import win32api
import win32con

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
DOMAINS = ["www.roblox.com", "roblox.com"]
REDIRECT_IP = "127.0.0.1"
BLOCK_ENTRIES = [f"{REDIRECT_IP} {domain}\n" for domain in DOMAINS]
FIREWALL_RULE_NAME = "Block Roblox Player"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def unblock_domains(domains):
    print("🧹 Unblocking Roblox domains in hosts file...")
    try:
        with open(HOSTS_PATH, 'r') as file:
            lines = file.readlines()
        with open(HOSTS_PATH, 'w') as file:
            for line in lines:
                if not any(domain in line for domain in domains):
                    file.write(line)
        print("✅ Domains unblocked.")
    except Exception as e:
        print(f"❌ Failed to unblock hosts: {e}")

def restore_renamed_executables():
    print("🧹 Restoring renamed Roblox executables...")
    user = os.getlogin()
    base_path = rf"C:\\Users\\{user}\\AppData\\Local\\Roblox\\Versions"
    restored_count = 0
    if os.path.exists(base_path):
        for root, _, files in os.walk(base_path):
            for file in files:
                if file.endswith(".blocked"):
                    orig_file = file[:-8]  # remove ".blocked"
                    orig_path = os.path.join(root, orig_file)
                    blocked_path = os.path.join(root, file)
                    try:
                        if not os.path.exists(orig_path):
                            os.rename(blocked_path, orig_path)
                            print(f"🔄 Restored: {file} -> {orig_file}")
                            restored_count += 1
                        else:
                            print(f"⚠️ Original file exists, skipping restore: {orig_file}")
                    except Exception as e:
                        print(f"❌ Failed to restore {file}: {e}")
    if restored_count == 0:
        print("ℹ️ No renamed executables found to restore.")

def remove_firewall_rule():
    print("🧹 Removing Roblox firewall block rule...")
    try:
        subprocess.run([
            "netsh", "advfirewall", "firewall", "delete", "rule",
            f"name={FIREWALL_RULE_NAME}"
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Firewall rule removed.")
    except Exception as e:
        print(f"❌ Failed to remove firewall rule: {e}")

def kill_roblox_processes():
    print("🧹 Killing Roblox processes if running...")
    try:
        subprocess.run('taskkill /f /im RobloxPlayerBeta.exe', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run('taskkill /f /im RobloxPlayerLauncher.exe', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Roblox processes killed.")
    except Exception as e:
        print(f"❌ Failed to kill Roblox processes: {e}")

def uninstall_roblox():
    print("🧹 Uninstalling Roblox via WMIC and PowerShell...")
    try:
        # WMIC uninstall
        output = subprocess.check_output('wmic product get name', shell=True, text=True)
        for line in output.splitlines():
            if "Roblox" in line:
                name = line.strip()
                print(f"🛠️ Uninstalling: {name}")
                subprocess.run(f'wmic product where name="{name}" call uninstall /nointeractive', shell=True)
                time.sleep(3)  # wait a little for uninstall
                break
        else:
            print("ℹ️ Roblox not found via WMIC.")
    except Exception as e:
        print(f"❌ WMIC uninstall failed: {e}")

    try:
        # PowerShell uninstall fallback
        ps_check = subprocess.run([
            'powershell', '-Command', 'Get-Package -Name *Roblox*'
        ], capture_output=True, text=True)
        if "Roblox" in ps_check.stdout:
            print("🛠️ Attempting PowerShell uninstall...")
            subprocess.run([
                'powershell', '-Command',
                'Get-Package -Name *Roblox* | Uninstall-Package -Force'
            ], capture_output=True, text=True)
            print("✅ PowerShell uninstall attempted.")
        else:
            print("ℹ️ No Roblox packages found in PowerShell.")
    except Exception as e:
        print(f"❌ PowerShell uninstall failed: {e}")

def remove_roblox_data():
    print("🧹 Removing Roblox user data folders...")
    user = os.getlogin()
    appdata_path = rf"C:\Users\{user}\AppData\Local\Roblox"
    try:
        if os.path.exists(appdata_path):
            shutil.rmtree(appdata_path, ignore_errors=True)
            print(f"✅ Removed Roblox data at: {appdata_path}")
        else:
            print("ℹ️ Roblox data folder not found.")
    except Exception as e:
        print(f"❌ Failed to remove Roblox data: {e}")

def main():
    if not is_admin():
        print("⚠️ Please run this script as Administrator.")
        input("Press Enter to exit...")
        sys.exit(1)

    print("=== Roblox Cleaning & Reset Script ===")

    unblock_domains(DOMAINS)
    restore_renamed_executables()
    remove_firewall_rule()
    kill_roblox_processes()
    uninstall_roblox()
    remove_roblox_data()

    print("\n✅ All done! Roblox settings reset to default.")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
