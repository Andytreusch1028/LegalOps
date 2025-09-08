# Terminal Execution Rules - Memory

## 🚨 **CRITICAL RULE: NEVER GET STUCK IN TERMINAL COMMANDS**

### **Problem Identified:**
- Terminal commands are getting stuck in pager views (less, more)
- Commands are waiting for user input instead of completing automatically
- This creates a poor user experience requiring manual intervention

### **SOLUTION RULES:**

#### **1. Always Use Non-Interactive Commands:**
- **NEVER use**: `git log`, `git status` without flags
- **ALWAYS use**: `git log --oneline`, `git status --porcelain`
- **ALWAYS append**: `| cat` to commands that might use pagers
- **ALWAYS use**: `--porcelain` flags when available

#### **2. Automatic Continuation:**
- **NEVER wait** for user input to continue
- **ALWAYS proceed** automatically with the next logical step
- **NEVER ask** "continue?" - just continue
- **ALWAYS complete** the full task without stopping

#### **3. Command Alternatives:**
- **Instead of**: `git log` → **Use**: `git log --oneline | cat`
- **Instead of**: `git status` → **Use**: `git status --porcelain`
- **Instead of**: `git diff` → **Use**: `git diff --name-only`
- **Instead of**: `ls -la` → **Use**: `dir` (Windows) or `ls -1`

#### **4. Error Handling:**
- **If stuck**: Immediately start new shell
- **If pager opens**: Use Ctrl+C equivalent
- **If waiting**: Use timeout commands
- **If interactive**: Use non-interactive alternatives

#### **5. Windows-Specific:**
- **Use**: `dir` instead of `ls`
- **Use**: `type` instead of `cat`
- **Use**: `findstr` instead of `grep`
- **Use**: PowerShell commands when needed

### **IMPLEMENTATION:**
- **Apply immediately** to all terminal commands
- **Test commands** before using in production
- **Use alternatives** that don't require user interaction
- **Complete tasks** without stopping for user input

### **EXAMPLES OF CORRECT USAGE:**
```bash
# CORRECT - Non-interactive
git status --porcelain
git log --oneline | cat
git config --list | findstr user

# INCORRECT - Interactive
git status
git log
git config --list
```

### **MEMORY RULE:**
**ALWAYS use non-interactive terminal commands and never wait for user input. Complete all tasks automatically without stopping.**