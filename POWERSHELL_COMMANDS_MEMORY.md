# PowerShell Command Workarounds

## Commands that STALL in PowerShell:
- `mkdir` - stalls terminal
- `cd ..` - stalls terminal  
- `Set-Location ..` - stalls terminal
- `cd C:\LegalOps` - stalls terminal
- `cd` commands in general - stalls terminal
- `git status` - stalls terminal
- `git add .` - stalls terminal
- `git add -A` - stalls terminal
- `git add "filename"` - stalls terminal
- `git log` - stalls terminal (pager issues)
- `git diff` - stalls terminal (pager issues)
- `docker-compose --version` - stalls terminal
- Most Git commands with interactive/pager output
- Most Docker Compose commands with output
- Most directory navigation commands

## Working Alternatives:
- Instead of `mkdir`: Use `write` tool to create files directly (creates parent directories automatically)
- Instead of ALL cd commands: Use batch files or VS Code integrated terminal
- Instead of `git status`: Use `git status --porcelain` or `git diff --name-only`
- Instead of ALL git add commands: Use VS Code's integrated Git or Git GUI tools
- Instead of `git log`: Use `git log --oneline --no-pager` or `git log --oneline | cat`
- Instead of `git diff`: Use `git diff --no-pager` or `git diff | cat`
- Instead of `docker-compose --version`: Use `docker compose version` (newer syntax)
- Instead of `docker-compose`: Use `docker compose` (newer syntax)

## Git Configuration Fixes (Run these once):
```bash
git config --global core.pager ""
git config --global --unset core.pager
git config --global init.defaultBranch main
git config --global core.autocrlf true
git config --global core.safecrlf false
```

## CRITICAL WORKAROUND - PowerShell Terminal Issues:
**PowerShell has fundamental compatibility issues with most commands.**

### Recommended Solutions:
1. **Use VS Code's Integrated Terminal with Different Shell**:
   - Switch to Git Bash terminal in VS Code
   - Or use WSL terminal for all operations
   - Or use Command Prompt instead of PowerShell

2. **Use Batch Files for Everything**:
   - Create .bat files for all operations
   - Run commands through batch files
   - This bypasses PowerShell issues

3. **Use VS Code's Integrated Git**: 
   - Open VS Code in the project directory
   - Use the Source Control panel (Ctrl+Shift+G)
   - Stage, commit, and push from the GUI

4. **Use Git GUI Tools**:
   - GitKraken, SourceTree, or GitHub Desktop

## Docker Workarounds:
- Use `docker compose` instead of `docker-compose` (newer syntax)
- Use batch files for Docker operations
- Use VS Code's integrated terminal with different shell types

## Navigation Workarounds:
- Use batch files for all directory operations
- Use VS Code's integrated terminal with different shell types
- Use `write` tool to create files in any directory

## Memory Rule:
**PowerShell is fundamentally broken for most operations. Always use VS Code's integrated terminal with Git Bash/WSL, batch files, or VS Code's integrated Git. Avoid PowerShell entirely for development work.**