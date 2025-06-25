#!/usr/bin/python
import os
import sys
import time
import ctypes
import signal
import subprocess
import shutil

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
REDIRECT_IP = "127.0.0.1"
DOMAINS = ["www.roblox.com", "roblox.com"]
BLOCK_ENTRIES = [f"{REDIRECT_IP} {domain}\n" for domain in DOMAINS]
FIREWALL_RULE_NAME = "Block Roblox Player"

ROBLOX_EXE_NAMES = ["RobloxPlayerBeta.exe", "RobloxPlayerLauncher.exe", "RobloxStudioLauncherBeta.exe"]

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def kill_roblox_processes():
    for proc in ROBLOX_EXE_NAMES:
        subprocess.run(['taskkill', '/F', '/IM', proc], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def remove_roblox_appdata():
    user = os.getlogin()
    appdata_path = rf"C:\Users\{user}\AppData\Local\Roblox"
    if os.path.exists(appdata_path):
        try:
            shutil.rmtree(appdata_path)
            print(f"🗑️ Removed Roblox AppData at {appdata_path}")
        except Exception as e:
            print(f"⚠️ Could not remove Roblox AppData: {e}")

def rename_roblox_executables():
    user = os.getlogin()
    base_path = rf"C:\Users\{user}\AppData\Local\Roblox\Versions"
    renamed = 0
    if os.path.exists(base_path):
        for root, _, files in os.walk(base_path):
            for file in files:
                if file in ROBLOX_EXE_NAMES:
                    full_path = os.path.join(root, file)
                    blocked_path = full_path + ".blocked"
                    if not os.path.exists(blocked_path):
                        try:
                            os.rename(full_path, blocked_path)
                            renamed += 1
                            print(f"🔒 Renamed {file} to {os.path.basename(blocked_path)}")
                        except Exception as e:
                            print(f"⚠️ Failed to rename {file}: {e}")
    if renamed == 0:
        print("ℹ️ No Roblox executables renamed.")
    return renamed

def block_domains():
    try:
        with open(HOSTS_PATH, 'r+') as file:
            lines = file.readlines()
            file.seek(0, os.SEEK_END)
            for entry in BLOCK_ENTRIES:
                if entry not in lines:
                    file.write(entry)
                    print(f"🚫 Blocked domain {entry.strip().split()[1]}")
    except Exception as e:
        print(f"⚠️ Could not modify hosts file: {e}")

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
        print(f"⚠️ Could not unblock domains: {e}")

def block_firewall():
    try:
        user = os.getlogin()
        base_path = rf"C:\Users\{user}\AppData\Local\Roblox\Versions"
        executables = []
        if os.path.exists(base_path):
            for root, _, files in os.walk(base_path):
                for file in files:
                    if file in ROBLOX_EXE_NAMES:
                        executables.append(os.path.join(root, file))
        if not executables:
            print("ℹ️ No Roblox executables found for firewall blocking.")
            return
        for exe in executables:
            subprocess.run([
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name={FIREWALL_RULE_NAME}",
                "dir=out", "action=block", f"program={exe}",
                "enable=yes"
            ], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"🔥 Firewall rule added for {os.path.basename(exe)}")
    except Exception as e:
        print(f"⚠️ Could not add firewall rules: {e}")

def remove_roblox_exe_files():
    search_dirs = [
        os.environ.get("USERPROFILE", r"C:\Users"),
        r"C:\Windows\Temp",
        r"C:\ProgramData",
        r"C:\Program Files",
        r"C:\Program Files (x86)"
    ]
    removed = 0
    for root_dir in search_dirs:
        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.lower().startswith("roblox") and file.lower().endswith(".exe"):
                    full_path = os.path.join(root, file)
                    try:
                        os.remove(full_path)
                        removed += 1
                        print(f"🗑️ Removed {full_path}")
                    except Exception as e:
                        print(f"⚠️ Could not remove {full_path}: {e}")
    if removed == 0:
        print("ℹ️ No Roblox executables deleted.")
    else:
        print(f"✅ Removed {removed} Roblox executable(s).")

def uninstall_roblox_app():
    print("\n🪑 Starting Roblox uninstall...")
    kill_roblox_processes()
    remove_roblox_appdata()

    found = False

    # WMIC uninstall
    try:
        output = subprocess.check_output('wmic product get name', shell=True, text=True, errors='ignore')
        for line in output.splitlines():
            if "Roblox" in line:
                print(f"🛠️ Uninstalling Roblox package via WMIC: {line.strip()}")
                subprocess.run(f'wmic product where name="{line.strip()}" call uninstall /nointeractive', shell=True, check=True)
                found = True
                break
    except Exception as e:
        print(f"⚠️ WMIC uninstall error: {e}")

    # PowerShell uninstall
    try:
        ps_check = subprocess.run(['powershell', '-Command', 'Get-Package -Name *Roblox*'], capture_output=True, text=True)
        if "Roblox" in ps_check.stdout:
            print("🛠️ Attempting PowerShell uninstall...")
            subprocess.run(['powershell', '-Command', 'Get-Package -Name *Roblox* | Uninstall-Package -Force'], capture_output=True, text=True)
            found = True
        else:
            print("✅ PowerShell: No Roblox packages found.")
    except Exception as e:
        print(f"⚠️ PowerShell uninstall error: {e}")

    if not found:
        print("🎉 Roblox app not found or already uninstalled.")

def block_everything(admin_mode):
    kill_roblox_processes()
    uninstall_roblox_app()
    rename_roblox_executables()
    if admin_mode:
        block_domains()
        block_firewall()
        remove_roblox_exe_files()
    print("🚪 Blocking and uninstall complete. Exiting now.")
    sys.exit(0)

def handle_exit_signal(signum, frame):
    print("\n🚨 Exit signal caught! Blocking Roblox now...")
    block_everything(is_admin())

def main():
    signal.signal(signal.SIGINT, handle_exit_signal)
    signal.signal(signal.SIGTERM, handle_exit_signal)

    admin = is_admin()
    print(f"Running as admin: {admin}")

    choice = None
    while choice not in ["1", "2"]:
        print("\nChoose mode:")
        print("1) Limited user mode (no admin) - kills Roblox, removes AppData, renames exes")
        print("2) Full admin mode - uninstall Roblox, blocks domains/firewall, deletes executables")
        choice = input("Enter 1 or 2: ").strip()

    if choice == "2" and not admin:
        print("⚠️ You selected full admin mode but script is NOT running as admin.")
        print("Please run the script as Administrator and try again.")
        input("Press Enter to exit...")
        sys.exit(1)

    if choice == "1":
        print("🚀 Running in limited user mode...")
        kill_roblox_processes()
        remove_roblox_appdata()
        rename_roblox_executables()
        print("🚪 Done with limited blocking. Exiting.")
        sys.exit(0)

    if choice == "2":
        print("🚀 Running in full admin mode...")
        unblock_domains()  # allow Roblox temporarily before blocking
        try:
            hours = float(input("⏳ Enter hours to wait before blocking Roblox (e.g., 1.5): "))
            if hours <= 0:
                raise ValueError
        except ValueError:
            print("❌ Invalid input. Exiting.")
            sys.exit(1)

        print(f"⏳ Waiting {hours} hour(s)... Press Ctrl+C to block immediately.")
        try:
            time.sleep(hours * 3600)
        except KeyboardInterrupt:
            print("\n🛑 Interrupted early - blocking Roblox now...")

        block_everything(admin_mode=True)

if __name__ == "__main__":
    main()
