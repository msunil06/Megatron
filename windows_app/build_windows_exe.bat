@echo off
title Build Megatron Windows Executable (PyInstaller)
color 0b
echo ========================================================
echo   BUILDING STANDALONE MEGATRON.EXE FOR WINDOWS
echo ========================================================
echo.

cd /d "%~dp0\.."

echo [*] Compiling Megatron with PyInstaller...
python -m PyInstaller --noconfirm --onedir --windowed ^
    --name "Megatron" ^
    --icon "www/assets/img/logo.ico" ^
    --add-data "www;www" ^
    --add-data "megatron.db;." ^
    windows_app/megatron_desktop.py

if errorlevel 0 (
    echo.
    echo ========================================================
    echo   BUILD SUCCESSFUL!
    echo   Standalone executable created in: dist\Megatron\Megatron.exe
    echo ========================================================
) else (
    echo.
    echo [ERROR] Build failed. Check the error log above.
)
pause
