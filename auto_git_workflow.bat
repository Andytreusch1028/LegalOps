@echo off
REM Automated Git Workflow Batch Script for Windows
REM Provides easy access to automated Git operations

echo Automated Git Workflow for Legal Ops Platform
echo =============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Show menu
:menu
echo.
echo Choose an option:
echo 1. Start Work Session (auto-pull latest changes)
echo 2. End Work Session (commit and push all changes)
echo 3. Run Continuous Monitoring (auto-commit every 30 min, auto-push every 60 min)
echo 4. Pull Latest Changes
echo 5. Commit Current Changes
echo 6. Push to GitHub
echo 7. Show Configuration
echo 8. Exit
echo.

set /p choice="Enter your choice (1-8): "

if "%choice%"=="1" (
    echo Starting work session...
    python auto_git_workflow.py --start
    goto menu
) else if "%choice%"=="2" (
    echo Ending work session...
    python auto_git_workflow.py --end
    goto menu
) else if "%choice%"=="3" (
    echo Starting continuous monitoring...
    echo Press Ctrl+C to stop monitoring
    python auto_git_workflow.py --monitor
    goto menu
) else if "%choice%"=="4" (
    echo Pulling latest changes...
    python auto_git_workflow.py --pull
    goto menu
) else if "%choice%"=="5" (
    set /p message="Enter commit message (or press Enter for auto-message): "
    if "%message%"=="" (
        python auto_git_workflow.py --commit
    ) else (
        python auto_git_workflow.py --commit --message "%message%"
    )
    goto menu
) else if "%choice%"=="6" (
    echo Pushing to GitHub...
    python auto_git_workflow.py --push
    goto menu
) else if "%choice%"=="7" (
    python auto_git_workflow.py --config
    goto menu
) else if "%choice%"=="8" (
    echo Goodbye!
    exit /b 0
) else (
    echo Invalid choice. Please try again.
    goto menu
)
