@echo off
REM Git Monitor Batch Script for Windows
REM Runs Git monitoring system for Legal Ops Platform

echo Starting Git Monitor for Legal Ops Platform...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Run the Git monitor
python git_monitor.py

echo.
echo Git monitoring complete. Check git_monitor.log for details.
pause
