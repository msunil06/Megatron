@echo off
title Megatron AI — Windows Software Installer
color 0b
echo ========================================================
echo   MEGATRON AI — WINDOWS SOFTWARE INSTALLER
echo   Configuring Desktop Suite with Full System Control...
echo ========================================================
echo.

set SCRIPT_DIR=%~dp0
set TARGET_BAT=%SCRIPT_DIR%run_megatron_windows.bat
set ICON_PATH=%SCRIPT_DIR%www\assets\img\logo.ico
set VBS_SCRIPT=%TEMP%\create_megatron_shortcut.vbs

echo [*] Creating Desktop Shortcut for Megatron AI...

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\Megatron AI.lnk" >> "%VBS_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_SCRIPT%"
echo oLink.TargetPath = "%TARGET_BAT%" >> "%VBS_SCRIPT%"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> "%VBS_SCRIPT%"
echo oLink.Description = "Megatron AI Desktop Suite (Full System Control)" >> "%VBS_SCRIPT%"
if exist "%ICON_PATH%" (
    echo oLink.IconLocation = "%ICON_PATH%" >> "%VBS_SCRIPT%"
)
echo oLink.Save >> "%VBS_SCRIPT%"

cscript /nologo "%VBS_SCRIPT%"
del "%VBS_SCRIPT%" 2>nul

echo [OK] Shortcut 'Megatron AI.lnk' has been placed on your Desktop!
echo.
echo [*] Optional: You can also compile a standalone .exe by running:
echo     windows_app\build_windows_exe.bat
echo.
echo ========================================================
echo   INSTALLATION COMPLETE!
echo   Double-click the 'Megatron AI' icon on your Desktop
echo   to run with FULL PC SYSTEM CONTROLS.
echo ========================================================
echo.
pause
