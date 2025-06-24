# uninstaller

# 🧼 Roblox Cleaner

This tool **fully resets all Roblox-related restrictions and settings** applied by the [Roblox-Child-Controller](https://github.com/asc3t1c/Roblox-Child-Controller) or similar parental control scripts. It is designed for **parents only** and is **protected by a password** prompt.

---

## 🔐 Purpose

If you or your child no longer need restrictions on Roblox (e.g. domain blocking, firewall rules, executable renaming), this script will **restore the system to its default state**, including optional Roblox app uninstallation.

---

## ✅ Features

- 🔓 Unblocks Roblox domains in the system `hosts` file.
- 🔄 Restores renamed `.exe` files for the Roblox app.
- 🔥 Removes firewall rules blocking Roblox.
- ❌ Kills running Roblox processes.
- 🧹 Attempts full uninstallation via WMIC and PowerShell.
- 🗑️ Deletes leftover Roblox data from local user folders.
- 🔐 **Password-protected** to prevent child access.

---

## ⚠️ Requirements

- Windows 10/11
- Python 3.x installed
- `pywin32` package (`pip install pywin32`)
- Run **as Administrator**
- Know the configured password (default: `parentonly` — change it in the script!)

---

## 🚀 How to Use

1. **Open Terminal or Command Prompt as Administrator**  
   (Right-click and choose “Run as Administrator”)

2. **Run the Script**
   ```bash
   python cleaner.py

