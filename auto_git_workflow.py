#!/usr/bin/env python3
"""
Automated Git Workflow for Legal Ops Platform
Handles common Git operations automatically with smart decision making
"""

import subprocess
import json
import datetime
import os
import sys
import time
from pathlib import Path

class AutoGitWorkflow:
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path).resolve()
        self.log_file = self.repo_path / "auto_git_workflow.log"
        self.config_file = self.repo_path / "git_workflow_config.json"
        self.load_config()
        
    def load_config(self):
        """Load workflow configuration"""
        default_config = {
            "auto_pull_on_start": True,
            "auto_commit_interval": 30,  # minutes
            "auto_push_interval": 60,    # minutes
            "commit_message_template": "Auto-commit: {timestamp}",
            "max_commits_before_push": 3,
            "backup_before_operations": True,
            "notify_on_errors": True
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    self.config = {**default_config, **json.load(f)}
            except:
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save workflow configuration"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)
    
    def log_message(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"[{timestamp}] {message}")
    
    def run_git_command(self, command, capture_output=True):
        """Run git command safely"""
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
        except Exception as e:
            self.log_message(f"Git command failed: {command} - {str(e)}", "ERROR")
            return False, "", str(e)
    
    def check_for_changes(self):
        """Check if there are uncommitted changes"""
        success, stdout, _ = self.run_git_command("git status --porcelain")
        if success:
            changes = [line for line in stdout.split('\n') if line.strip()]
            return len(changes) > 0, changes
        return False, []
    
    def check_remote_updates(self):
        """Check if remote has updates"""
        success, stdout, _ = self.run_git_command("git fetch --dry-run")
        if success:
            return "up to date" not in stdout.lower()
        return False
    
    def auto_pull(self):
        """Automatically pull latest changes"""
        self.log_message("Checking for remote updates...")
        
        if self.check_remote_updates():
            self.log_message("Remote updates found, pulling...")
            success, stdout, stderr = self.run_git_command("git pull")
            if success:
                self.log_message("Successfully pulled latest changes")
                return True
            else:
                self.log_message(f"Pull failed: {stderr}", "ERROR")
                return False
        else:
            self.log_message("Repository is up to date")
            return True
    
    def auto_commit(self, message=None):
        """Automatically commit changes"""
        has_changes, changes = self.check_for_changes()
        
        if not has_changes:
            self.log_message("No changes to commit")
            return True
        
        self.log_message(f"Found {len(changes)} changes, committing...")
        
        # Stage all changes
        success, _, stderr = self.run_git_command("git add .")
        if not success:
            self.log_message(f"Failed to stage changes: {stderr}", "ERROR")
            return False
        
        # Create commit message
        if not message:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = self.config["commit_message_template"].format(timestamp=timestamp)
        
        # Commit changes
        success, _, stderr = self.run_git_command(f'git commit -m "{message}"')
        if success:
            self.log_message(f"Successfully committed: {message}")
            return True
        else:
            self.log_message(f"Commit failed: {stderr}", "ERROR")
            return False
    
    def auto_push(self):
        """Automatically push to remote"""
        self.log_message("Checking if push is needed...")
        
        # Check if we're ahead of remote
        success, stdout, _ = self.run_git_command("git status -uno")
        if success and "Your branch is ahead" in stdout:
            self.log_message("Local branch is ahead, pushing...")
            success, stdout, stderr = self.run_git_command("git push")
            if success:
                self.log_message("Successfully pushed to remote")
                return True
            else:
                self.log_message(f"Push failed: {stderr}", "ERROR")
                return False
        else:
            self.log_message("No push needed")
            return True
    
    def start_work_session(self):
        """Start a new work session"""
        self.log_message("=== Starting Work Session ===")
        
        if self.config["auto_pull_on_start"]:
            self.auto_pull()
        
        self.log_message("Work session started. Auto-commit and auto-push are active.")
    
    def end_work_session(self):
        """End work session with final commit and push"""
        self.log_message("=== Ending Work Session ===")
        
        # Final commit of any remaining changes
        self.auto_commit("End of work session - final commit")
        
        # Push to remote
        self.auto_push()
        
        self.log_message("Work session ended. All changes saved and pushed.")
    
    def run_continuous_monitoring(self):
        """Run continuous monitoring with auto-commit and auto-push"""
        self.log_message("Starting continuous Git monitoring...")
        
        last_commit_time = time.time()
        last_push_time = time.time()
        
        try:
            while True:
                current_time = time.time()
                
                # Auto-commit check
                if (current_time - last_commit_time) >= (self.config["auto_commit_interval"] * 60):
                    if self.auto_commit():
                        last_commit_time = current_time
                
                # Auto-push check
                if (current_time - last_push_time) >= (self.config["auto_push_interval"] * 60):
                    if self.auto_push():
                        last_push_time = current_time
                
                # Sleep for 1 minute before next check
                time.sleep(60)
                
        except KeyboardInterrupt:
            self.log_message("Continuous monitoring stopped by user")
        except Exception as e:
            self.log_message(f"Continuous monitoring error: {str(e)}", "ERROR")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Automated Git Workflow")
    parser.add_argument("--start", action="store_true", help="Start work session")
    parser.add_argument("--end", action="store_true", help="End work session")
    parser.add_argument("--monitor", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--pull", action="store_true", help="Pull latest changes")
    parser.add_argument("--commit", action="store_true", help="Commit current changes")
    parser.add_argument("--push", action="store_true", help="Push to remote")
    parser.add_argument("--config", action="store_true", help="Show current configuration")
    parser.add_argument("--message", type=str, help="Custom commit message")
    
    args = parser.parse_args()
    
    workflow = AutoGitWorkflow()
    
    if args.config:
        print("Current Configuration:")
        print(json.dumps(workflow.config, indent=2))
        return
    
    if args.start:
        workflow.start_work_session()
    elif args.end:
        workflow.end_work_session()
    elif args.monitor:
        workflow.run_continuous_monitoring()
    elif args.pull:
        workflow.auto_pull()
    elif args.commit:
        workflow.auto_commit(args.message)
    elif args.push:
        workflow.auto_push()
    else:
        print("Use --help to see available options")

if __name__ == "__main__":
    main()
