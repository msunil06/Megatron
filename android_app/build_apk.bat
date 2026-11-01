@echo off
title Build Megatron Android APK
color 0a
echo ========================================================
echo   MEGATRON AI — ANDROID APK BUILDER
echo ========================================================
echo.

cd /d "%~dp0"

if exist gradlew.bat (
    echo [*] Building Android APK with Gradle...
    call gradlew.bat assembleDebug
    if errorlevel 0 (
        echo.
        echo [OK] APK Built Successfully!
        echo Location: app\build\outputs\apk\debug\app-debug.apk
    ) else (
        echo [!] Gradle build encountered an error. Ensure Android SDK is installed.
    )
) else (
    echo [*] You can open the 'android_app' folder directly in Android Studio
    echo     or use the Gradle command to compile the APK.
    echo.
    echo [*] Alternatively, on your Android device, open:
    echo     http://<YOUR_PC_IP>:8000/index.html
    echo     and tap 'Install App' or 'Add to Home Screen' for instant mobile installation!
)

echo.
pause
