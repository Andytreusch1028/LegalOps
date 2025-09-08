@echo off
title Legal Ops Platform - Flexible Startup
color 0C

echo ========================================
echo    Legal Ops Platform - Flexible Startup
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] Running as Administrator - Good!
) else (
    echo [WARNING] Not running as Administrator
    echo [INFO] Some features may not work properly
    echo.
)

REM Check if WSL is available
echo [1/5] Checking WSL availability...
wsl --status >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] WSL is available
) else (
    echo [ERROR] WSL is not available
    echo [INFO] Please install WSL2 first
    pause
    exit /b 1
)

REM Find Ubuntu distribution (flexible search)
echo [2/5] Finding Ubuntu distribution...
set UBUNTU_DISTRO=""
for /f "tokens=1,*" %%i in ('wsl --list --verbose ^| findstr /i ubuntu') do (
    REM Check if the first token is '*'
    if "%%i"=="*" (
        REM If it's '*', the actual name is the second token
        for /f "tokens=1" %%k in ("%%j") do (
            set UBUNTU_DISTRO=%%k
            echo [OK] Found Ubuntu distribution: %%k
            goto :found_ubuntu
        )
    ) else (
        REM Otherwise, the name is the first token
        set UBUNTU_DISTRO=%%i
        echo [OK] Found Ubuntu distribution: %%i
        goto :found_ubuntu
    )
)

echo [ERROR] No Ubuntu distribution found
echo [INFO] Available distributions:
wsl --list --verbose
echo.
echo [INFO] Please install Ubuntu in WSL2 first
pause
exit /b 1

:found_ubuntu
REM Extract just the distribution name (first word)
for /f "tokens=1" %%a in ("%UBUNTU_DISTRO%") do set UBUNTU_NAME=%%a

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

REM Check for Cursor IDE in multiple locations
echo [4/5] Checking Cursor IDE...
set CURSOR_PATH=""
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\cursor\Cursor.exe" (
    set CURSOR_PATH="C:\Users\%USERNAME%\AppData\Local\Programs\cursor\Cursor.exe"
    echo [OK] Cursor IDE found in default location
) else if exist "C:\Program Files\Cursor\Cursor.exe" (
    set CURSOR_PATH="C:\Program Files\Cursor\Cursor.exe"
    echo [OK] Cursor IDE found in Program Files
) else if exist "C:\Program Files (x86)\Cursor\Cursor.exe" (
    set CURSOR_PATH="C:\Program Files (x86)\Cursor\Cursor.exe"
    echo [OK] Cursor IDE found in Program Files (x86)
) else (
    echo [WARNING] Cursor IDE not found in common locations
    echo [INFO] Will try to start Cursor IDE anyway
    set CURSOR_PATH="cursor"
)

REM Start the complete development environment
echo [5/5] Starting complete development environment...
echo.

REM Start WSL2 Ubuntu and Claude Code
echo Starting WSL2 %UBUNTU_NAME% and Claude Code...
start "Claude Code" wsl -d %UBUNTU_NAME% -e bash -c "cd /mnt/c/LegalOps && echo '========================================' && echo '   Legal Ops Platform - Development' && echo '========================================' && echo '' && echo 'Project Directory: /mnt/c/LegalOps' && echo 'Starting Claude Code...' && echo '' && npx @anthropic-ai/claude-code"

REM Wait a moment for WSL to start
timeout /t 3 >nul

REM Start Cursor IDE
echo Starting Cursor IDE...
if "%CURSOR_PATH%"=="" (
    start "Cursor IDE" cursor "C:\LegalOps"
) else (
    start "Cursor IDE" %CURSOR_PATH% "C:\LegalOps"
)

echo.
echo ========================================
echo    Complete Startup Finished!
echo ========================================
echo.
echo You should now have:
echo   ✓ WSL2 %UBUNTU_NAME% running with Claude Code
echo   ✓ Cursor IDE open with your project
echo   ✓ Complete development environment ready
echo.
echo If something didn't start properly:
echo   1. Check that WSL2 and Ubuntu are installed
echo   2. Check that Cursor IDE is installed
echo   3. Check that the project directory exists
echo   4. Try running this script as Administrator
echo.
echo Press any key to exit...
pause >nul
