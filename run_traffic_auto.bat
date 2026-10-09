@echo off
REM Traffic Pipeline AUTO Runner - Batch wrapper for run_traffic_auto.ps1
REM Run this by double-clicking or from command prompt

echo ############################################################
echo # TRAFFIC PIPELINE AUTO - Zero Touch (Batch Wrapper)
echo ############################################################
echo.
echo Started: %date% %time%
echo.

REM Check if PowerShell is available
where powershell >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: PowerShell not found in PATH
    pause
    exit /b 1
)

REM Run the PowerShell script
powershell -ExecutionPolicy Bypass -File "%~dp0run_traffic_auto.ps1" %*

echo.
echo ############################################################
echo # Pipeline finished. Press any key to exit...
echo ############################################################
pause >nul