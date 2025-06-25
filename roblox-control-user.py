#!/usr/bin/python
import os
import time
import shutil
import subprocess
import signal
import sys

ROBLOX_EXE_NAMES = [
    "RobloxPlayerBeta.exe",
    "RobloxPlayerLauncher.exe",
    "RobloxStudioBeta.exe"
]

USER = os.getlogin()
LOCAL_ROBLOX_PATH = os.path.join("C:\\Users", USER, "AppData", "Local", "Roblox")
STUDIO_PATH = os.path.join("C:\\Users", USER, "AppData", "Local", "Roblox Studio")
DOWNLOADS_PATH = os.path.join("C:\\Users", USER, "Downloads")

ROBLOX_DOMAINS = [
    "roblox.com",
    "www.roblox.com",
    "api.roblox.com",
    "setup.roblox.com",
    "assetgame.roblox.com",
    "friends.roblox.com",
    "games.roblox.com",
    "presence.roblox.com"
]

def kill_roblox_processes():
    for exe in ROBLOX_EXE_NAMES:
        subprocess.run(["taskkill", "/F", "/IM", exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def delete_local_roblox_folder():
    for path in [LOCAL_ROBLOX_PATH, STUDIO_PATH]:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                print(f"🗑️ Deleted folder: {path}")
            except Exception as e:
                print(f"❌ Could not delete {path}: {e}")

def delete_roblox_exe_files():
    print("🧹 Searching for Roblox .exe files...")
    search_dirs = [LOCAL_ROBLOX_PATH, STUDIO_PATH, os.environ.get("TEMP", ""), DOWNLOADS_PATH]
    count = 0

    for root_dir in search_dirs:
        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.lower().startswith("roblox") and file.lower().endswith(".exe"):
                    try:
                        os.remove(os.path.join(root, file))
                        print(f"🗑️ Deleted: {os.path.join(root, file)}")
                        count += 1
                    except Exception as e:
                        print(f"⚠️ Could not delete {file}: {e}")
    if count == 0:
        print("ℹ️ No Roblox .exe files found or deleted.")
    else:
        print(f"✅ Removed {count} Roblox .exe file(s).")

def block_roblox_domains_firewall():
    print("🔥 Adding firewall rules to block Roblox domains...")
    for domain in ROBLOX_DOMAINS:
        rule_name = f"Block_{domain.replace('.', '_')}"
        try:
            subprocess.run([
                "netsh", "advfirewall", "firewall", "add", "rule",
                "name=" + rule_name,
                "dir=out", "action=block",
                f"remoteip={domain}",
                "enable=yes"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"❌ Failed to add firewall rule for {domain}: {e}")
    print("✅ Firewall rules added to block Roblox.")

def block_roblox_user_level():
    kill_roblox_processes()
    delete_local_roblox_folder()
    delete_roblox_exe_files()
    block_roblox_domains_firewall()
    print("✅ Roblox & Studio blocked (via firewall).")

def handle_exit(signum, frame):
    print("\n⚠️ Exit signal detected. Blocking Roblox now...")
    block_roblox_user_level()
    sys.exit(0)

def wait_then_block(hours):
    seconds = hours * 3600
    print(f"⏳ Waiting {hours} hour(s)... Press Ctrl+C to block immediately.")
    try:
        time.sleep(seconds)
    except KeyboardInterrupt:
        handle_exit(None, None)
    print("\n⏲️ Time's up! Roblox will now be blocked.")
    block_roblox_user_level()

def main():
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    try:
        wait_hours = float(input("⏳ Enter wait time in hours before blocking Roblox: "))
        if wait_hours <= 0:
            print("Please enter a number greater than 0.")
            return
    except ValueError:
        print("❌ Invalid number.")
        return

    wait_then_block(wait_hours)

if __name__ == "__main__":
    main()
