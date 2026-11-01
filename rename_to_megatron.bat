@echo off
echo ==============================================
echo   Megatron Project Folder Renaming Utility
echo ==============================================
echo.
echo Please close the IDE or any open terminals in this folder before continuing.
echo.
pause
echo Renaming D:\J-238\Jarvis to D:\J-238\megatron...
powershell -NoProfile -Command "[System.IO.Directory]::SetCurrentDirectory('C:\'); Set-Location 'C:\'; Rename-Item -Path 'D:\J-238\Jarvis' -NewName 'megatron'"
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Folder successfully renamed to: D:\J-238\megatron
    echo You can now open D:\J-238\megatron in your IDE!
) else (
    echo.
    echo [ERROR] Folder is currently locked by your IDE or terminal.
    echo Please close the IDE window and run this file again.
)
echo.
pause
