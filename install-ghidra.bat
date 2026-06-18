@echo off
setlocal
cd /d "%~dp0"

title Ghidra Installer v1.1.1

where powershell >nul 2>&1
if errorlevel 1 (
    echo [FAIL] PowerShell is required but was not found on PATH.
    exit /b 1
)

echo.
echo ===============================================================
echo   Ghidra installer v1.1.1 // Windows 10/11
echo   See GHIDRA.md for Linux install and full usage
echo ===============================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-ghidra.ps1" %*
set "ERR=%ERRORLEVEL%"
if not "%ERR%"=="0" (
    echo.
    echo Install failed with exit code %ERR%.
    pause
)
exit /b %ERR%
