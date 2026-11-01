"""
Megatron AI — Windows Desktop Software Suite
Provides 100% full Windows PC system control (volume, screenshots, lock screen,
desktop applications, CMD, Notepad, Calculator, WhatsApp, and global hotkeys).
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser

# Set Execution Mode to Windows Desktop App with full system permissions
os.environ["MEGATRON_MODE"] = "windows_app"

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import eel
from engine.features import *
from engine.command import *
from engine.config import ASSISTANT_NAME

def launch_desktop_window():
    """Launch native frameless application window."""
    time.sleep(1.2)
    url = "http://localhost:8000/index.html"
    # Launch in native app mode (Edge or Chrome without browser toolbars)
    edge_cmd = f'start msedge.exe --app="{url}" --window-size=1200,820'
    ret = os.system(edge_cmd)
    if ret != 0:
        chrome_cmd = f'start chrome.exe --app="{url}" --window-size=1200,820'
        ret_chrome = os.system(chrome_cmd)
        if ret_chrome != 0:
            webbrowser.open(url)

def main():
    print("=" * 60)
    print("  MEGATRON AI — WINDOWS DESKTOP SUITE (FULL CONTROL)")
    print("  All Windows hardware & system controls are ACTIVE.")
    print("=" * 60)

    www_dir = os.path.join(BASE_DIR, "www")
    eel.init(www_dir)

    # Launch desktop app window
    threading.Thread(target=launch_desktop_window, daemon=True).start()

    # Start hotkey listener thread (Win+J)
    try:
        threading.Thread(target=hotword, daemon=True).start()
    except Exception as e:
        print(f"[Hotkey Warning] {e}")

    # Start Eel Server on port 8000
    try:
        eel._detect_shutdown = lambda: None
        eel.start('index.html', mode=None, host='0.0.0.0', port=8000, block=True)
    except OSError:
        # If port is already in use by background server, just open the app window
        launch_desktop_window()

if __name__ == "__main__":
    main()
