import os
import subprocess
import time
import shutil

# Domains to "block" via fake open method
ROBLOX_DOMAINS = ["www.roblox.com", "roblox.com"]

# Folders to search for Roblox executables
def find_and_delete_roblox_exes():
    userprofile = os.environ.get("USERPROFILE", "")
    search_dirs = [
        os.path.join(userprofile, "AppData", "Local", "Roblox"),
        os.path.join(userprofile, "Downloads"),
        os.path.join(userprofile, "Desktop"),
    ]

    deleted = 0
    for directory in search_dirs:
        if not os.path.exists(directory):
            continue
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().startswith("roblox") and file.lower().endswith(".exe"):
                    full_path = os.path.join(root, file)
                    try:
                        os.remove(full_path)
                        print(f"🗑️ Deleted: {full_path}")
                        deleted += 1
                    except Exception as e:
                        print(f"⚠️ Failed to delete {full_path}: {e}")
    if deleted == 0:
        print("ℹ️ No Roblox .exe files found.")
    else:
        print(f"✅ Deleted {deleted} Roblox executable(s).")

# Tries to block the domain using the default browser
def open_blocked_tab():
    try:
        for domain in ROBLOX_DOMAINS:
            # Open browser with an invalid IP to simulate block
            print(f"🚫 Trying to block: {domain}")
            subprocess.Popen([
                "cmd", "/c", f"start chrome --new-window --host-rules='MAP {domain} 127.0.0.1'"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"⚠️ Browser domain redirection failed: {e}")

# Kills any running Roblox processes
def kill_roblox_processes():
    for proc in ["RobloxPlayerBeta.exe", "RobloxPlayerLauncher.exe"]:
        try:
            subprocess.run(["taskkill", "/f", "/im", proc], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

def main():
    print("🔎 Searching and removing Roblox executables...")
    kill_roblox_processes()
    find_and_delete_roblox_exes()

    print("\n🌐 Attempting to block Roblox domain in browser session...")
    open_blocked_tab()

    print("\n🎉 Done! This works without admin rights.")

if __name__ == "__main__":
    main()
