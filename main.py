import os
import subprocess
import threading
import webbrowser
import eel

from engine.features import *
from engine.command import *
from engine.auth import recoganize
from engine.config import ASSISTANT_NAME

import socket

def get_local_ip():
    """Get the active local network IPv4 address of this machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def run_device_setup():
    """Run device.bat in background to avoid freezing application launch."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        bat_file = os.path.join(base_dir, 'device.bat')
        if os.path.exists(bat_file):
            subprocess.Popen([bat_file], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"[Device Setup Error] {e}")


def start():
    """Initializes and runs the Megatron Eel desktop application for all devices."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    www_dir = os.path.join(base_dir, "www")
    eel.init(www_dir)

    # Register Android APK and ZIP MIME types so phones never download as HTML
    import mimetypes
    mimetypes.add_type('application/vnd.android.package-archive', '.apk')
    mimetypes.add_type('application/zip', '.zip')

    # Custom route to serve downloads with exact binary MIME headers and attachment disposition
    @eel.btl.route('/downloads/<filename:path>')
    def serve_downloads(filename):
        download_dir = os.path.join(www_dir, 'downloads')
        file_path = os.path.join(download_dir, filename)
        if not os.path.exists(file_path):
            return eel.btl.HTTPError(404, "File not found")
        if filename.lower().endswith('.apk'):
            mimetype = 'application/vnd.android.package-archive'
        elif filename.lower().endswith('.zip'):
            mimetype = 'application/zip'
        else:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        return eel.btl.static_file(filename, root=download_dir, mimetype=mimetype, download=filename)

    local_ip = get_local_ip()
    port = 8000

    # Start optional background ADB connection
    threading.Thread(target=run_device_setup, daemon=True).start()

    # Play startup chime
    playAssistantSound()

    @eel.expose
    def getNetworkAccessInfo():
        """Returns local and network access URLs for multi-device connectivity."""
        return {
            "local_ip": local_ip,
            "port": port,
            "local_url": f"http://localhost:{port}/index.html",
            "network_url": f"http://{local_ip}:{port}/index.html",
            "apk_url": f"http://{local_ip}:{port}/downloads/Megatron_Android_App.apk",
            "win_url": f"http://{local_ip}:{port}/downloads/Megatron_Windows_Software_Suite.zip"
        }

    @eel.expose
    def skipAuth():
        """Bypass face authentication directly from UI button."""
        print("[Megatron Auth] Face authentication manually bypassed.")
        try:
            eel.hideLoader()
            eel.hideFaceAuth()
            eel.hideFaceAuthSuccess()
            eel.hideStart()
            speak("Welcome Commander. Megatron is online and ready for your commands.")
            playAssistantSound()
        except Exception as e:
            print(f"[skipAuth Error] {e}")

    @eel.expose
    def init():
        """
        Triggered upon web UI load.
        In browser mode, bypasses face recognition completely and loads
        straight into Megatron AI Agent HUD for instant, frictionless data access.
        """
        try:
            eel.hideStart()
            eel.ShowHood()
            print(f"[Megatron Agent] Loaded directly into Web Agent HUD on {local_ip}:{port}. No face authentication required.")
        except Exception as e:
            print(f"[init Exception] {e}")

    @eel.expose
    def triggerBiometricScan():
        """Optional on-demand face authentication for Windows Desktop software."""
        try:
            speak("Ready for Face Authentication. Look at the camera.")
            flag = recoganize.AuthenticateFace()
            if flag == 1:
                speak("Biometric verification confirmed.")
                return 1
            else:
                speak("Biometric verification cancelled.")
                return 0
        except Exception as e:
            print(f"[Biometric Error] {e}")
            return 0

    # Launch browser in app mode (Edge or default browser fallback)
    def open_browser():
        import time
        time.sleep(1.2)
        target_url = f"http://localhost:{port}/index.html"
        ret = os.system(f'start msedge.exe --app="{target_url}"')
        if ret != 0:
            webbrowser.open(target_url)

    threading.Thread(target=open_browser, daemon=True).start()

    # Prevent Eel server from auto-exiting when browser tab reloads, closes, or disconnects
    def prevent_shutdown(page, sockets):
        pass

    eel._detect_shutdown = lambda: None

    print("\n" + "=" * 65)
    print("  MEGATRON AI — MULTI-DEVICE LOCAL NETWORK SERVER ACTIVE")
    print("=" * 65)
    print(f"  [>] Local Host (This PC)  : http://localhost:{port}/index.html")
    print(f"  [>] ALL DEVICES ON WI-FI  : http://{local_ip}:{port}/index.html")
    print(f"  [>] Windows Software Suite: http://{local_ip}:{port}/downloads/Megatron_Windows_Software_Suite.zip")
    print(f"  [>] Android Mobile APK    : http://{local_ip}:{port}/downloads/Megatron_Android_App.apk")
    print("=" * 65)
    print(f"  Connect phones, tablets, or laptops on the same Wi-Fi")
    print(f"  and open: http://{local_ip}:{port}/index.html")
    print("=" * 65 + "\n")

    # Start Eel Server listening on 0.0.0.0 to enable access from all devices
    eel.start('index.html', mode=None, host='0.0.0.0', port=port, block=True, close_callback=prevent_shutdown)


if __name__ == "__main__":
    start()