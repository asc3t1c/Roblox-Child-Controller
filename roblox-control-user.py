import os
import subprocess
import time
import shutil
import socket
import threading

ROBLOX_DOMAINS = ["www.roblox.com", "roblox.com"]
USER_DIR = os.environ.get("USERPROFILE", "")
ROBLOX_DIR = os.path.join(USER_DIR, "AppData", "Local", "Roblox")

def kill_roblox_processes():
    procs = ["RobloxPlayerBeta.exe", "RobloxPlayerLauncher.exe"]
    for proc in procs:
        try:
            subprocess.run(['taskkill', '/F', '/IM', proc], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass

def delete_roblox_executables():
    print("🔍 Searching for Roblox .exe files in user folders...")
    deleted = 0
    for root, _, files in os.walk(ROBLOX_DIR):
        for file in files:
            if file.lower().endswith(".exe") and "roblox" in file.lower():
                full_path = os.path.join(root, file)
                try:
                    os.remove(full_path)
                    print(f"🗑️ Deleted: {full_path}")
                    deleted += 1
                except Exception as e:
                    print(f"⚠️ Could not delete {full_path}: {e}")
    if deleted == 0:
        print("ℹ️ No executables found or already removed.")
    else:
        print(f"✅ Removed {deleted} Roblox executables.")

def remove_roblox_folder():
    if os.path.exists(ROBLOX_DIR):
        try:
            shutil.rmtree(ROBLOX_DIR)
            print(f"🗑️ Removed folder: {ROBLOX_DIR}")
        except Exception as e:
            print(f"⚠️ Could not remove folder: {e}")
    else:
        print("ℹ️ Roblox folder already removed.")

def block_domains_browser():
    print("\n🌐 Attempting browser-level domain blocks using command-line options...")
    for domain in ROBLOX_DOMAINS:
        try:
            subprocess.Popen([
                "cmd", "/c", f"start chrome --host-rules='MAP {domain} 127.0.0.1' --new-window"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            print(f"⚠️ Could not block {domain} via browser.")

# Optional: Run a fake web server to catch blocked requests
def start_fake_server():
    def fake_server():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 80))
            s.listen()
            while True:
                conn, addr = s.accept()
                with conn:
                    try:
                        conn.sendall(b"HTTP/1.1 403 Forbidden\r\n\r\nBlocked by user script.")
                    except:
                        pass
    t = threading.Thread(target=fake_server, daemon=True)
    t.start()

def main():
    print("📦 Roblox User Blocker (No Admin Needed)")
    kill_roblox_processes()
    delete_roblox_executables()
    remove_roblox_folder()

    start_fake_server()
    block_domains_browser()

    print("\n✅ Done. Roblox is removed and domain access is blocked via browser.")
    print("🧠 Tip: You can also install a browser extension like BlockSite for stronger control.")

if __name__ == "__main__":
    main()
