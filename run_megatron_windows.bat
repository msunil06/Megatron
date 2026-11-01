@echo off
title Megatron AI — Windows Desktop Suite (Full System Control)
color 0b
echo ========================================================
echo   MEGATRON AI — WINDOWS DESKTOP SUITE
echo   Mode: Full Windows PC System Control Unlocked
echo ========================================================
echo.
set MEGATRON_MODE=windows_app
cd /d "%~dp0"
python windows_app\megatron_desktop.py
if errorlevel 1 (
    echo.
    echo Application exited. Press any key to close...
    pause >nul
)
