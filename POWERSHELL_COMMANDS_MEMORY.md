# PowerShell Command Workarounds

## Commands that STALL in PowerShell:
- `mkdir` - stalls terminal
- `cd ..` - stalls terminal  
- `git status` - stalls terminal
- `git add .` - stalls terminal
- `git add -A` - stalls terminal
- `git add "filename"` - stalls terminal
- `git log` - stalls terminal (pager issues)
- `git diff` - stalls terminal (pager issues)
- Most Git commands with interactive/pager output

## Working Alternatives:
- Instead of `mkdir`: Use `write` tool to create files directly (creates parent directories automatically)
- Instead of `cd ..`: Use `Set-Location ..` or `Set-Location -Path ..`
- Instead of `git status`: Use `git status --porcelain` or `git diff --name-only`
- Instead of ALL git add commands: Use VS Code's integrated Git or Git GUI tools
- Instead of `git log`: Use `git log --oneline --no-pager` or `git log --oneline | cat`
- Instead of `git diff`: Use `git diff --no-pager` or `git diff | cat`

## Git Configuration Fixes (Run these once):
```bash
git config --global core.pager ""
git config --global --unset core.pager
git config --global init.defaultBranch main
git config --global core.autocrlf true
git config --global core.safecrlf false
```

## CRITICAL WORKAROUND - Git Operations:
**PowerShell is fundamentally incompatible with Git commands that modify the repository.**

### Recommended Solutions:
1. **Use VS Code's Integrated Git**: 
   - Open VS Code in the project directory
   - Use the Source Control panel (Ctrl+Shift+G)
   - Stage, commit, and push from the GUI

2. **Use Git Bash or WSL**:
   - Switch to Git Bash terminal in VS Code
   - Or use WSL terminal for Git operations

3. **Use Git GUI Tools**:
   - GitKraken, SourceTree, or GitHub Desktop

4. **Batch File Workaround**:
   - Create .bat files for common Git operations
   - Run Git commands through batch files

## Memory Rule:
**PowerShell cannot handle Git operations reliably. Always use VS Code's integrated Git, Git Bash, WSL, or Git GUI tools for repository operations. Use PowerShell only for file operations and non-Git commands.**