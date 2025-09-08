@echo off
title Legal Ops Platform - Windows Terminal Startup
color 0B

echo ========================================
echo    Legal Ops Platform - Auto Startup
echo ========================================
echo.

REM Check if Windows Terminal is available
echo [1/3] Checking Windows Terminal...
where wt >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Windows Terminal found
) else (
    echo [ERROR] Windows Terminal not found
    echo [INFO] Please install Windows Terminal first
    pause
    exit /b 1
)

REM Check if project directory exists
echo [2/4] Checking project directory...
if exist "C:\LegalOps" (
    echo [OK] Project directory found: C:\LegalOps
) else (
    echo [ERROR] Project directory not found: C:\LegalOps
    echo [INFO] Please ensure the project directory exists
    pause
    exit /b 1
)

REM Check if Cursor IDE is available
echo [3/4] Checking Cursor IDE...
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\cursor\Cursor.exe" (
    echo [OK] Cursor IDE found
) else (
    echo [WARNING] Cursor IDE not found in default location
    echo [INFO] Will try to start Cursor IDE anyway
)

REM Start Windows Terminal with Ubuntu tab and auto-run commands
echo [4/4] Starting Windows Terminal with Ubuntu...
echo.

REM Create a temporary script to run in Ubuntu
echo #!/bin/bash > temp_startup.sh
echo echo "=========================================" >> temp_startup.sh
echo echo "   Legal Ops Platform - Development" >> temp_startup.sh
echo echo "=========================================" >> temp_startup.sh
echo echo "" >> temp_startup.sh
echo echo "Navigating to project directory..." >> temp_startup.sh
echo cd /mnt/c/LegalOps >> temp_startup.sh
echo echo "Project Directory: $(pwd)" >> temp_startup.sh
echo echo "" >> temp_startup.sh
echo echo "Starting Claude Code..." >> temp_startup.sh
echo npx @anthropic-ai/claude-code >> temp_startup.sh

REM Start Windows Terminal with Ubuntu tab and run the script
wt -p "Ubuntu" -d "C:\LegalOps" --title "Legal Ops Platform" -e bash -c "chmod +x /mnt/c/LegalOps/temp_startup.sh && /mnt/c/LegalOps/temp_startup.sh"

REM Start Cursor IDE
echo.
echo Starting Cursor IDE...
start "" "C:\Users\%USERNAME%\AppData\Local\Programs\cursor\Cursor.exe" "C:\LegalOps"

REM Clean up temporary script
timeout /t 2 >nul
del temp_startup.sh >nul 2>&1

echo.
echo ========================================
echo    Startup Complete!
echo ========================================
echo.
echo Windows Terminal should now be open with Ubuntu tab
echo Claude Code should be starting automatically
echo.
echo If it didn't work, run these commands manually:
echo   1. Open Windows Terminal
echo   2. Select Ubuntu tab
echo   3. Run: cd /mnt/c/LegalOps
echo   4. Run: npx @anthropic-ai/claude-code
echo.
echo Press any key to exit...
pause >nul
