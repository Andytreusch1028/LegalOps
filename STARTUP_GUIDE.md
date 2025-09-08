# Legal Ops Platform - Startup Guide

## 🚀 **After Restart: What You Need to Do**

### **Quick Start (2 minutes):**
1. **Open Windows Terminal**
2. **Select Ubuntu tab**
3. **Navigate to project**
4. **Start Claude Code**

---

## 📋 **Step-by-Step Startup Process**

### **Step 1: Open Windows Terminal**
- **Click Start Menu** → Search "Windows Terminal" → Click to open
- **Or press** `Windows + R` → Type `wt` → Press Enter

### **Step 2: Select Ubuntu Tab**
- **Click the dropdown arrow** next to the + tab
- **Select "Ubuntu"** (this opens WSL2 Ubuntu environment)
- **You should see**: `imali@GT1Mega:~$`

### **Step 3: Navigate to Your Project**
```bash
cd /mnt/c/LegalOps
```

### **Step 4: Start Claude Code**
```bash
npx @anthropic-ai/claude-code
```

**That's it! You're ready to continue development.**

---

## 🔧 **What Gets Preserved vs What Needs Setup**

### **✅ Automatically Preserved (No Setup Needed):**
- **WSL2 installation** - stays installed
- **Ubuntu distribution** - stays configured
- **Windows Terminal** - stays installed
- **Project files** - all your code and documents
- **Claude Code installation** - stays available
- **Development rules** - stored in files
- **Professional development plan** - ready to reference

### **❌ Needs to be Restarted (Quick Setup):**
- **WSL2 Ubuntu session** - needs to be opened
- **Claude Code interactive session** - needs to be started
- **Terminal environment** - needs to be opened

---

## 🎯 **Alternative Startup Methods**

### **Method 1: Direct Ubuntu Launch**
```bash
# Open PowerShell as Administrator
wsl -d Ubuntu

# Navigate to project
cd /mnt/c/LegalOps

# Start Claude Code
npx @anthropic-ai/claude-code
```

### **Method 2: Windows Terminal Shortcut**
1. **Right-click Windows Terminal** in Start Menu
2. **Select "Run as administrator"**
3. **Click Ubuntu tab**
4. **Run startup commands**

### **Method 3: Batch Script (Optional)**
Create a startup script for even faster startup:

**Create `startup.bat`:**
```batch
@echo off
start wt -p "Ubuntu" -d "C:\LegalOps"
```

**Double-click to start everything at once.**

---

## 🔍 **Troubleshooting Common Issues**

### **Issue 1: Ubuntu Tab Not Available**
**Solution:**
```powershell
# Open PowerShell as Administrator
wsl --set-default Ubuntu
wsl -d Ubuntu
```

### **Issue 2: Claude Code Not Found**
**Solution:**
```bash
# In Ubuntu tab
npm install -g @anthropic-ai/claude-code
```

### **Issue 3: Permission Denied**
**Solution:**
```bash
# In Ubuntu tab
sudo chown -R $USER:$USER /mnt/c/LegalOps
```

### **Issue 4: WSL Not Starting**
**Solution:**
```powershell
# Open PowerShell as Administrator
wsl --shutdown
wsl --start
```

---

## 📊 **Startup Time Expectations**

### **Fast Startup (30 seconds):**
- **Windows Terminal** → **Ubuntu tab** → **Navigate** → **Claude Code**

### **Medium Startup (1-2 minutes):**
- **WSL needs to start** → **Ubuntu initialization** → **Claude Code**

### **Slow Startup (3+ minutes):**
- **WSL needs restart** → **Ubuntu reconfiguration** → **Claude Code**

---

## 🎯 **Optimal Startup Workflow**

### **Daily Development Routine:**
1. **Open Windows Terminal** (5 seconds)
2. **Click Ubuntu tab** (2 seconds)
3. **Run**: `cd /mnt/c/LegalOps` (3 seconds)
4. **Run**: `npx @anthropic-ai/claude-code` (10-30 seconds)
5. **Start coding!** (immediate)

### **Weekly Maintenance:**
- **Update packages**: `sudo apt update && sudo apt upgrade`
- **Check Claude Code**: `npx @anthropic-ai/claude-code --version`
- **Verify project files**: `ls -la /mnt/c/LegalOps`

---

## 🔒 **Security & Best Practices**

### **Always Run as Administrator:**
- **Windows Terminal** should be run as Administrator
- **WSL commands** may need elevated privileges
- **File permissions** should be properly set

### **Backup Important Files:**
- **Development rules** are in `DEVELOPMENT_RULES.md`
- **Professional plan** is in `PROFESSIONAL_DEVELOPMENT_PLAN.md`
- **Project files** are in `/mnt/c/LegalOps`

---

## 📱 **Quick Reference Commands**

### **Essential Commands:**
```bash
# Navigate to project
cd /mnt/c/LegalOps

# Start Claude Code
npx @anthropic-ai/claude-code

# Check WSL status
wsl --status

# List WSL distributions
wsl --list --verbose

# Update packages
sudo apt update && sudo apt upgrade
```

### **Claude Code Commands:**
```bash
# Get help
/help

# Check status
/status

# Use memory
> remember that we're building a Legal Ops Platform

# Start development
> help me with Phase 1 tasks from our development plan
```

---

## 🎉 **Success Indicators**

### **You're Ready When You See:**
- ✅ **Windows Terminal** open with Ubuntu tab
- ✅ **Ubuntu prompt**: `imali@GT1Mega:/mnt/c/LegalOps$`
- ✅ **Claude Code welcome**: `* Welcome to Claude Code!`
- ✅ **Interactive prompt**: `> Try "create a util logging.py that..."`

### **Everything is Working When:**
- ✅ **No error messages**
- ✅ **Claude Code responds** to commands
- ✅ **Project files** are accessible
- ✅ **Memory features** are available

---

## 🚀 **Next Steps After Startup**

### **Immediate Actions:**
1. **Check project status**: `> what do you remember about our project?`
2. **Review development plan**: `> show me Phase 1 tasks`
3. **Start development**: `> help me implement the first task`

### **Development Workflow:**
1. **Start Claude Code** (using this guide)
2. **Review current progress**
3. **Continue with development tasks**
4. **Follow development rules** (intensive testing)
5. **Update project documentation**

---

**This guide ensures you can quickly get back to development after any restart!** 🎯

