@echo off
echo ===================================================
echo   Megatron Windows Suite - Uninstaller Launcher
echo ===================================================
cd /d "%~dp0\.."
if exist "uninstall_megatron.bat" (
    call "uninstall_megatron.bat" %*
) else (
    echo Error: Root uninstaller script not found.
    pause
)
