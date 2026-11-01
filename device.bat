@echo off
echo [Megatron] Checking ADB Bridge...
where adb >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [Megatron] ADB executable not found in PATH. Skipping mobile bridge.
    exit /b 0
)

echo [Megatron] Probing connected Android devices...
adb devices | find "device" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [Megatron] Connected device detected. Initializing TCPIP port 5555...
    adb tcpip 5555
    FOR /F "tokens=2" %%G IN ('adb shell ip addr show wlan0 2^>nul ^| find "inet "') DO set ipfull=%%G
    if defined ipfull (
        FOR /F "tokens=1 delims=/" %%G in ("%ipfull%") DO set ip=%%G
        if defined ip (
            echo [Megatron] Connecting over Wi-Fi to %ip%:5555...
            adb connect %ip%:5555
        )
    )
) else (
    echo [Megatron] No Android devices currently connected via USB. Skipping.
)
exit /b 0
