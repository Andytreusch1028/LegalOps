@echo off
title Legal Ops Platform - Auto Startup
color 0A

echo ========================================
echo    Legal Ops Platform - Auto Startup
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] Running as Administrator - Good!
) else (
    echo [WARNING] Not running as Administrator
    echo [INFO] Some features may not work properly
    echo [INFO] Consider running this script as Administrator
    echo.
)

REM Check if WSL is available
echo [1/4] Checking WSL availability...
wsl --status >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] WSL is available
) else (
    echo [ERROR] WSL is not available
    echo [INFO] Please install WSL2 first
    pause
    exit /b 1
)

REM Check if Ubuntu is available
echo [2/4] Checking Ubuntu distribution...
wsl -l -v | findstr Ubuntu >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Ubuntu distribution found
) else (
    echo [ERROR] Ubuntu distribution not found
    echo [INFO] Please install Ubuntu in WSL2 first
    pause
    exit /b 1
)

REM Check if project directory exists
echo [3/5] Checking project directory...
if exist "C:\LegalOps" (
    echo [OK] Project directory found: C:\LegalOps
) else (
    echo [ERROR] Project directory not found: C:\LegalOps
    echo [INFO] Please ensure the project directory exists
    pause
    exit /b 1
)

REM Check if Cursor IDE is available
echo [4/5] Checking Cursor IDE...
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\cursor\Cursor.exe" (
    echo [OK] Cursor IDE found
) else (
    echo [WARNING] Cursor IDE not found in default location
    echo [INFO] Will try to start Cursor IDE anyway
)

REM Start the development environment
echo [5/5] Starting development environment...
echo.
echo Starting WSL2 Ubuntu and Claude Code...
echo.

REM Start WSL2 Ubuntu and navigate to project directory
wsl -d Ubuntu -e bash -c "cd /mnt/c/LegalOps && echo '========================================' && echo '   Legal Ops Platform - Development' && echo '========================================' && echo '' && echo 'Project Directory: /mnt/c/LegalOps' && echo 'Starting Claude Code...' && echo '' && npx @anthropic-ai/claude-code"

echo.
echo Starting Cursor IDE...
start "" "C:\Users\%USERNAME%\AppData\Local\Programs\cursor\Cursor.exe" "C:\LegalOps"

echo.
echo ========================================
echo    Startup Complete!
echo ========================================
echo.
echo If Claude Code didn't start automatically, run these commands manually:
echo   1. Open Windows Terminal
echo   2. Select Ubuntu tab
echo   3. Run: cd /mnt/c/LegalOps
echo   4. Run: npx @anthropic-ai/claude-code
echo.
echo Press any key to exit...
pause >nul
