@echo off
echo Committing changes to Git...
git add -A
git commit -m "Fix CSS backdrop-filter Safari compatibility and update PowerShell workarounds"
git push
echo Git operations completed!
pause
