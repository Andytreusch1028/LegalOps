#!/usr/bin/env python3
"""
Git Monitoring System for Legal Ops Platform
Monitors Git operations and repository health at regular intervals
"""

import subprocess
import json
import datetime
import os
import sys
from pathlib import Path

class GitMonitor:
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path).resolve()
        self.log_file = self.repo_path / "git_monitor.log"
        self.status_file = self.repo_path / "git_status.json"
        
    def log_message(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"[{timestamp}] {message}")
    
    def run_git_command(self, command, capture_output=True):
        """Run git command safely with error handling"""
        try:
            if capture_output:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    cwd=self.repo_path,
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
            else:
                result = subprocess.run(command, shell=True, cwd=self.repo_path, timeout=30)
                return result.returncode == 0, "", ""
        except subprocess.TimeoutExpired:
            self.log_message(f"Git command timed out: {command}", "ERROR")
            return False, "", "Command timed out"
        except Exception as e:
            self.log_message(f"Git command failed: {command} - {str(e)}", "ERROR")
            return False, "", str(e)
    
    def check_repository_status(self):
        """Check overall repository health"""
        status = {
            "timestamp": datetime.datetime.now().isoformat(),
            "repository_path": str(self.repo_path),
            "checks": {}
        }
        
        # Check if we're in a git repository
        success, _, _ = self.run_git_command("git rev-parse --git-dir")
        if not success:
            status["checks"]["is_git_repo"] = {"status": "FAIL", "message": "Not a git repository"}
            return status
        else:
            status["checks"]["is_git_repo"] = {"status": "PASS", "message": "Valid git repository"}
        
        # Check git status
        success, stdout, stderr = self.run_git_command("git status --porcelain")
        if success:
            changes = stdout.split('\n') if stdout else []
            status["checks"]["working_directory"] = {
                "status": "PASS" if not changes else "WARN",
                "message": f"{len(changes)} uncommitted changes" if changes else "Clean working directory",
                "changes": changes
            }
        else:
            status["checks"]["working_directory"] = {"status": "FAIL", "message": stderr}
        
        # Check remote connection
        success, stdout, stderr = self.run_git_command("git remote -v")
        if success and stdout:
            remotes = [line.split() for line in stdout.split('\n') if line.strip()]
            status["checks"]["remote_connection"] = {
                "status": "PASS",
                "message": f"Connected to {len(remotes)} remote(s)",
                "remotes": remotes
            }
        else:
            status["checks"]["remote_connection"] = {"status": "WARN", "message": "No remotes configured"}
        
        # Check branch status
        success, stdout, stderr = self.run_git_command("git branch -vv")
        if success:
            branches = [line.strip() for line in stdout.split('\n') if line.strip()]
            current_branch = next((b for b in branches if b.startswith('*')), None)
            status["checks"]["branch_status"] = {
                "status": "PASS",
                "message": f"On branch: {current_branch[2:] if current_branch else 'unknown'}",
                "branches": branches
            }
        else:
            status["checks"]["branch_status"] = {"status": "FAIL", "message": stderr}
        
        # Check if up to date with remote
        success, stdout, stderr = self.run_git_command("git status -uno")
        if success:
            if "Your branch is up to date" in stdout:
                status["checks"]["sync_status"] = {"status": "PASS", "message": "Up to date with remote"}
            elif "Your branch is ahead" in stdout:
                status["checks"]["sync_status"] = {"status": "WARN", "message": "Ahead of remote - needs push"}
            elif "Your branch is behind" in stdout:
                status["checks"]["sync_status"] = {"status": "WARN", "message": "Behind remote - needs pull"}
            else:
                status["checks"]["sync_status"] = {"status": "INFO", "message": "Sync status unclear"}
        else:
            status["checks"]["sync_status"] = {"status": "FAIL", "message": stderr}
        
        return status
    
    def run_monitoring_cycle(self):
        """Run a complete monitoring cycle"""
        self.log_message("Starting Git monitoring cycle")
        
        status = self.check_repository_status()
        
        # Save status to JSON file
        with open(self.status_file, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2)
        
        # Log summary
        total_checks = len(status["checks"])
        passed_checks = sum(1 for check in status["checks"].values() if check["status"] == "PASS")
        failed_checks = sum(1 for check in status["checks"].values() if check["status"] == "FAIL")
        warning_checks = sum(1 for check in status["checks"].values() if check["status"] == "WARN")
        
        self.log_message(f"Monitoring complete: {passed_checks}/{total_checks} checks passed, {failed_checks} failed, {warning_checks} warnings")
        
        # Log any issues
        for check_name, check_result in status["checks"].items():
            if check_result["status"] in ["FAIL", "WARN"]:
                self.log_message(f"{check_name}: {check_result['message']}", check_result["status"])
        
        return status
    
    def setup_git_hooks(self):
        """Set up git hooks for automatic monitoring"""
        hooks_dir = self.repo_path / ".git" / "hooks"
        
        # Pre-commit hook
        pre_commit_hook = hooks_dir / "pre-commit"
        pre_commit_content = """#!/bin/sh
# Git Monitor Pre-commit Hook
echo "Running Git Monitor pre-commit check..."
python3 git_monitor.py --pre-commit
"""
        
        with open(pre_commit_hook, "w") as f:
            f.write(pre_commit_content)
        os.chmod(pre_commit_hook, 0o755)
        
        # Post-commit hook
        post_commit_hook = hooks_dir / "post-commit"
        post_commit_content = """#!/bin/sh
# Git Monitor Post-commit Hook
echo "Running Git Monitor post-commit check..."
python3 git_monitor.py --post-commit
"""
        
        with open(post_commit_hook, "w") as f:
            f.write(post_commit_content)
        os.chmod(post_commit_hook, 0o755)
        
        self.log_message("Git hooks installed successfully")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Git Monitoring System")
    parser.add_argument("--pre-commit", action="store_true", help="Run pre-commit monitoring")
    parser.add_argument("--post-commit", action="store_true", help="Run post-commit monitoring")
    parser.add_argument("--setup-hooks", action="store_true", help="Set up git hooks")
    parser.add_argument("--repo-path", default=".", help="Repository path")
    
    args = parser.parse_args()
    
    monitor = GitMonitor(args.repo_path)
    
    if args.setup_hooks:
        monitor.setup_git_hooks()
        return
    
    if args.pre_commit:
        monitor.log_message("Pre-commit monitoring check")
        status = monitor.run_monitoring_cycle()
        # Don't fail the commit unless there are critical issues
        failed_checks = [name for name, check in status["checks"].items() if check["status"] == "FAIL"]
        if failed_checks:
            monitor.log_message(f"Pre-commit check failed: {failed_checks}", "ERROR")
            sys.exit(1)
    
    elif args.post_commit:
        monitor.log_message("Post-commit monitoring check")
        monitor.run_monitoring_cycle()
    
    else:
        # Regular monitoring cycle
        monitor.run_monitoring_cycle()

if __name__ == "__main__":
    main()
