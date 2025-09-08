@echo off
echo ========================================
echo    Legal Ops Platform - Auto Startup
echo ========================================
echo.

echo Starting WSL2 Ubuntu and Claude Code...
echo.

REM Start WSL2 Ubuntu and navigate to project directory
echo [1/4] Starting WSL2 Ubuntu...
wsl -d Ubuntu -e bash -c "cd /mnt/c/LegalOps && echo 'Navigated to LegalOps project directory' && echo '[2/4] Starting Claude Code...' && npx @anthropic-ai/claude-code"

echo.
echo [3/4] Starting Cursor IDE...
start "" "C:\Users\%USERNAME%\AppData\Local\Programs\cursor\Cursor.exe" "C:\LegalOps"

echo.
echo [4/4] Claude Code and Cursor IDE should now be running!
echo.
echo If Claude Code didn't start automatically, run these commands manually:
echo   1. Open Windows Terminal
echo   2. Select Ubuntu tab
echo   3. Run: cd /mnt/c/LegalOps
echo   4. Run: npx @anthropic-ai/claude-code
echo.
pause
