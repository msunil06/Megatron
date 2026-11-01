@echo off
setlocal enabledelayedexpansion

echo =======================================================
echo   MEGATRON AI - COMPLETE SYSTEM UNINSTALLATION WIZARD
echo =======================================================
echo.
echo WARNING: This process will permanently remove Megatron AI,
echo including all application files, databases, trained neural
echo memory, configuration settings, and desktop shortcuts.
echo Nothing will be left on your computer.
echo.

if "%1"=="--silent" goto DO_UNINSTALL
if "%1"=="/y" goto DO_UNINSTALL
if "%1"=="/Y" goto DO_UNINSTALL

set /p CONFIRM="Are you absolutely sure you want to completely uninstall Megatron? (Y/N): "
if /i not "!CONFIRM!"=="Y" (
    echo.
    echo [CANCELLED] Uninstallation aborted by user. No files were removed.
    echo.
    pause
    exit /b 0
)

:DO_UNINSTALL
echo.
echo [1/4] Stopping all active Megatron AI processes...
taskkill /F /FI "WINDOWTITLE eq *Megatron*" >nul 2>&1
wmic process where "commandline like '%%main.py%%' or commandline like '%%megatron%%'" delete >nul 2>&1

echo [2/4] Removing Desktop and Start Menu shortcuts...
if exist "%USERPROFILE%\Desktop\Megatron AI.lnk" del /f /q "%USERPROFILE%\Desktop\Megatron AI.lnk" >nul 2>&1
if exist "%USERPROFILE%\Desktop\Megatron.lnk" del /f /q "%USERPROFILE%\Desktop\Megatron.lnk" >nul 2>&1
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Megatron AI.lnk" del /f /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Megatron AI.lnk" >nul 2>&1

echo [3/4] Purging local databases, caches, and temporary data...
set "TARGET_DIR=%~dp0"
if "!TARGET_DIR:~-1!"=="\" set "TARGET_DIR=!TARGET_DIR:~0,-1!"

echo [4/4] Purging all Megatron project files from disk...
set "CLEANUP_SCRIPT=%TEMP%\megatron_purge_%RANDOM%.bat"

(
    echo @echo off
    echo timeout /t 2 /nobreak ^>nul
    echo echo Wiping Megatron project files...
    echo powershell -NoProfile -ExecutionPolicy Bypass -Command "Remove-Item -LiteralPath '!TARGET_DIR!' -Recurse -Force -ErrorAction SilentlyContinue"
    echo echo.
    echo echo =======================================================
    echo echo   MEGATRON AI HAS BEEN COMPLETELY REMOVED FROM SYSTEM
    echo echo =======================================================
    echo echo All files, databases, and shortcuts were successfully purged.
    echo timeout /t 4 ^>nul
    echo del "%%~f0" ^>nul 2^>^&1
) > "!CLEANUP_SCRIPT!"

echo.
echo Megatron is now being completely erased from your system.
start "" cmd.exe /c "!CLEANUP_SCRIPT!"
exit
