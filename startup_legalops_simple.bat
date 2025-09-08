@echo off
title Legal Ops Platform - Simple Startup
color 0A

echo ========================================
echo    Legal Ops Platform - Simple Startup
echo ========================================
echo.

echo [1/4] Starting WSL2 Ubuntu...
echo [2/4] Starting Claude Code...
echo [3/4] Starting Cursor IDE...
echo [4/4] Complete development environment ready!
echo.

REM Start WSL2 Ubuntu and Claude Code
echo Starting WSL2 Ubuntu and Claude Code...
start "Claude Code" wsl -d Ubuntu -e bash -c "cd /mnt/c/LegalOps && echo '========================================' && echo '   Legal Ops Platform - Development' && echo '========================================' && echo '' && echo 'Project Directory: /mnt/c/LegalOps' && echo 'Starting Claude Code...' && echo '' && npx @anthropic-ai/claude-code"

REM Wait a moment for WSL to start
timeout /t 3 >nul

REM Start Cursor IDE
echo Starting Cursor IDE...
start "Cursor IDE" "C:\Users\%USERNAME%\AppData\Local\Programs\cursor\Cursor.exe" "C:\LegalOps"

echo.
echo ========================================
echo    Startup Complete!
echo ========================================
echo.
echo You should now have:
echo   ✓ WSL2 Ubuntu running with Claude Code
echo   ✓ Cursor IDE open with your project
echo   ✓ Complete development environment ready
echo.
echo Press any key to exit...
pause >nul

