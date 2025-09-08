# Git Monitoring System

## Overview
Comprehensive Git monitoring system for the Legal Ops Platform that ensures repository health and tracks Git operations.

## Features

### 🔍 **Repository Health Monitoring**
- **Git Repository Validation**: Confirms we're in a valid Git repository
- **Working Directory Status**: Tracks uncommitted changes
- **Remote Connection**: Monitors GitHub connectivity
- **Branch Status**: Tracks current branch and tracking information
- **Sync Status**: Monitors if local is up-to-date with remote

### 📊 **Automated Monitoring**
- **Pre-commit Hooks**: Automatic checks before commits
- **Post-commit Hooks**: Verification after commits
- **Manual Monitoring**: On-demand repository health checks
- **Logging**: Comprehensive logging with timestamps

### 📁 **Files Created**
- `git_monitor.py` - Main monitoring script
- `git_monitor.bat` - Windows batch file for easy execution
- `git_monitor.log` - Monitoring activity log
- `git_status.json` - Current repository status (JSON format)

## Usage

### **Manual Monitoring**
```bash
# Run complete monitoring cycle
python git_monitor.py

# Or use the batch file (Windows)
git_monitor.bat
```

### **Set Up Automatic Hooks**
```bash
# Install Git hooks for automatic monitoring
python git_monitor.py --setup-hooks
```

### **Pre-commit Monitoring**
```bash
# Run pre-commit checks
python git_monitor.py --pre-commit
```

### **Post-commit Monitoring**
```bash
# Run post-commit verification
python git_monitor.py --post-commit
```

## Monitoring Checks

### ✅ **Repository Validation**
- Confirms Git repository exists
- Validates Git configuration

### 📝 **Working Directory**
- Tracks uncommitted changes
- Identifies modified, added, or deleted files
- Warns about untracked files

### 🌐 **Remote Connection**
- Verifies GitHub connectivity
- Lists configured remotes
- Checks remote repository access

### 🌿 **Branch Management**
- Shows current branch
- Displays branch tracking information
- Lists all available branches

### 🔄 **Sync Status**
- Compares local vs remote
- Identifies if ahead/behind
- Suggests push/pull actions

## Status Levels

### 🟢 **PASS**
- All checks successful
- Repository is healthy
- No action required

### 🟡 **WARN**
- Minor issues detected
- Repository functional but needs attention
- Recommended actions available

### 🔴 **FAIL**
- Critical issues detected
- Repository may have problems
- Immediate action required

## Log Files

### **git_monitor.log**
```
[2024-01-15 14:30:25] [INFO] Starting Git monitoring cycle
[2024-01-15 14:30:26] [PASS] Repository validation successful
[2024-01-15 14:30:27] [WARN] 3 uncommitted changes detected
[2024-01-15 14:30:28] [INFO] Monitoring complete: 4/5 checks passed, 0 failed, 1 warnings
```

### **git_status.json**
```json
{
  "timestamp": "2024-01-15T14:30:28.123456",
  "repository_path": "C:\\LegalOps",
  "checks": {
    "is_git_repo": {
      "status": "PASS",
      "message": "Valid git repository"
    },
    "working_directory": {
      "status": "WARN",
      "message": "3 uncommitted changes",
      "changes": ["M README.md", "A new_file.txt", "D old_file.txt"]
    }
  }
}
```

## Integration with Development Workflow

### **Automatic Monitoring**
- Hooks run automatically on commit
- Pre-commit prevents problematic commits
- Post-commit verifies successful operations

### **Manual Checks**
- Run before major operations
- Verify repository health
- Troubleshoot Git issues

### **Continuous Monitoring**
- Regular health checks
- Early problem detection
- Proactive maintenance

## Troubleshooting

### **Common Issues**

#### **"Not a git repository"**
- Ensure you're in the project directory
- Run `git init` if needed
- Check `.git` directory exists

#### **"Remote connection failed"**
- Verify GitHub repository exists
- Check internet connectivity
- Validate remote URL configuration

#### **"Branch tracking issues"**
- Run `git branch -M main`
- Set upstream: `git push -u origin main`
- Verify branch names match

### **Recovery Commands**
```bash
# Re-initialize repository
git init
git remote add origin https://github.com/Andytreusch1028/LegalOps.git

# Fix branch tracking
git branch -M main
git push -u origin main

# Reset to clean state
git reset --hard HEAD
git clean -fd
```

## Best Practices

### **Regular Monitoring**
- Run monitoring before major commits
- Check status after pull/push operations
- Monitor during development sessions

### **Hook Management**
- Install hooks after repository setup
- Update hooks when monitoring logic changes
- Test hooks in development environment

### **Log Management**
- Review logs regularly
- Archive old log files
- Monitor log file sizes

## Future Enhancements

### **Planned Features**
- **Email Notifications**: Alert on critical issues
- **Web Dashboard**: Visual monitoring interface
- **Performance Metrics**: Track Git operation speeds
- **Backup Verification**: Ensure repository backups
- **Security Scanning**: Check for sensitive data

### **Integration Opportunities**
- **CI/CD Pipeline**: Integrate with automated builds
- **Slack/Teams**: Send notifications to team channels
- **GitHub Actions**: Trigger on repository events
- **Monitoring Tools**: Integrate with system monitoring

## Support

### **Getting Help**
- Check `git_monitor.log` for detailed information
- Review `git_status.json` for current status
- Run monitoring with verbose output
- Consult Git documentation for specific issues

### **Reporting Issues**
- Include log file contents
- Provide repository status
- Describe expected vs actual behavior
- Include system information (OS, Git version, Python version)
