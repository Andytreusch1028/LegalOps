# FCHECKLIST Usage Instructions

## Overview
The `fchecklist` command provides easy access to the LegalOps Platform Design Checklist, a comprehensive list of 200+ design items across 20 categories that need to be reviewed and approved.

## Quick Start

### View the Checklist
```bash
./fchecklist
```

### Edit the Checklist
```bash
nano checklist.md
```

## Detailed Instructions

### 1. Accessing the Checklist

#### View Only (Read-Only)
```bash
# Display the entire checklist
./fchecklist

# View specific sections
./fchecklist | grep "Core Platform"
./fchecklist | head -50
./fchecklist | tail -50
```

#### Edit the Checklist
```bash
# Using nano (recommended for beginners)
nano checklist.md

# Using VS Code/Cursor (if installed)
code checklist.md

# Using vim (advanced users)
vim checklist.md
```

### 2. Marking Items as Approved

#### Step-by-Step Process

1. **Open the checklist for editing:**
   ```bash
   nano checklist.md
   ```

2. **Navigate to the item you want to approve:**
   - Use **arrow keys** to move around
   - Use **Page Up/Page Down** to move through sections
   - Use **Ctrl+W** to search for specific text

3. **Find an unapproved item:**
   ```markdown
   - [ ] **Florida-First Architecture**: Modular state architecture
   ```

4. **Position your cursor on the space inside the brackets:**
   ```markdown
   - [| ] **Florida-First Architecture**: Modular state architecture
   ```

5. **Replace the space with 'x':**
   - Press **Delete** or **Backspace** to remove the space
   - Type **x**
   - Result: `[x]`

6. **Save your changes:**
   - Press **Ctrl+X** to exit nano
   - Press **Y** to confirm saving
   - Press **Enter** to confirm filename

#### Visual Example
```markdown
# Before (not approved)
- [ ] **Florida-First Architecture**: Modular state architecture

# After (approved)
- [x] **Florida-First Architecture**: Modular state architecture
```

### 3. Adding New Items

#### Add New Items to Existing Categories
```markdown
## Core Platform Architecture
- [ ] **Florida-First Architecture**: Modular state architecture
- [ ] **Multi-Tenant Architecture**: Support for multiple user types
- [ ] **NEW ITEM**: Description of new item
```

#### Add New Categories
```markdown
## New Category Name
- [ ] **Item 1**: Description
- [ ] **Item 2**: Description
```

### 4. Updating and Committing Changes

#### Save Your Changes
```bash
# After editing with nano
# Press Ctrl+X, then Y, then Enter

# After editing with VS Code
# Press Ctrl+S
```

#### Commit Changes to Repository
```bash
# Add the modified checklist
git add checklist.md

# Commit with descriptive message
git commit -m "Updated checklist - approved X items"

# Or with specific details
git commit -m "Approved Core Platform Architecture items"
```

### 5. Advanced Usage

#### Search for Specific Items
```bash
# Search for specific text in the checklist
grep -n "Florida" checklist.md

# Search for approved items
grep -n "\[x\]" checklist.md

# Search for unapproved items
grep -n "\[ \]" checklist.md
```

#### Count Items
```bash
# Count total items
grep -c "\[ \]\|\[x\]" checklist.md

# Count approved items
grep -c "\[x\]" checklist.md

# Count unapproved items
grep -c "\[ \]" checklist.md
```

#### View Progress
```bash
# Show progress summary
echo "Total items: $(grep -c '\[ \]\|\[x\]' checklist.md)"
echo "Approved items: $(grep -c '\[x\]' checklist.md)"
echo "Remaining items: $(grep -c '\[ \]' checklist.md)"
```

### 6. Troubleshooting

#### Common Issues

**Issue: "Permission denied" when running ./fchecklist**
```bash
# Fix: Make the script executable
chmod +x fchecklist
```

**Issue: "checklist.md not found"**
```bash
# Fix: Ensure you're in the correct directory
pwd
ls -la checklist.md
```

**Issue: Can't save changes in nano**
```bash
# Make sure you have write permissions
ls -la checklist.md
# If needed, fix permissions
chmod 644 checklist.md
```

**Issue: Git commit fails**
```bash
# Check git status
git status

# If file is not staged, add it
git add checklist.md

# Then commit
git commit -m "Your commit message"
```

### 7. Best Practices

#### Organizing Your Work
1. **Review by category** - Work through one category at a time
2. **Use descriptive commit messages** - Include what you approved
3. **Regular commits** - Commit changes frequently
4. **Backup your work** - The git repository serves as backup

#### Efficient Editing
1. **Use search** - Ctrl+W in nano to find specific items
2. **Batch approvals** - Approve multiple related items at once
3. **Use keyboard shortcuts** - Learn nano shortcuts for efficiency
4. **Save frequently** - Save your work regularly

#### Collaboration
1. **Pull latest changes** before editing:
   ```bash
   git pull origin master
   ```

2. **Push your changes** after committing:
   ```bash
   git push origin master
   ```

3. **Resolve conflicts** if they occur:
   ```bash
   git status
   # Edit conflicted files
   git add .
   git commit -m "Resolved conflicts"
   ```

### 8. Example Workflow

#### Complete Approval Workflow
```bash
# 1. View the checklist
./fchecklist

# 2. Edit the checklist
nano checklist.md

# 3. Approve items by changing [ ] to [x]
# Navigate, edit, save (Ctrl+X, Y, Enter)

# 4. Check your changes
git status

# 5. Add and commit changes
git add checklist.md
git commit -m "Approved Core Platform Architecture items"

# 6. Push changes (if working with others)
git push origin master
```

#### Quick Approval Session
```bash
# Open, edit, save, commit in one session
nano checklist.md
# Make your changes, save with Ctrl+X, Y, Enter
git add checklist.md && git commit -m "Updated approvals"
```

### 9. File Structure

```
LegalOps_SDD/
├── checklist.md          # Main checklist file
├── fchecklist           # Command script to view checklist
├── FCHECKLIST_INSTRUCTIONS.md  # This instruction file
└── .claude/commands/
    └── checklist.md     # Command documentation
```

### 10. Command Reference

| Command | Description |
|---------|-------------|
| `./fchecklist` | View the checklist |
| `nano checklist.md` | Edit the checklist |
| `code checklist.md` | Edit with VS Code/Cursor |
| `git add checklist.md` | Stage changes |
| `git commit -m "message"` | Commit changes |
| `git status` | Check git status |
| `chmod +x fchecklist` | Make script executable |

### 11. Tips and Tricks

#### Nano Editor Shortcuts
- **Ctrl+W**: Search for text
- **Ctrl+X**: Exit nano
- **Ctrl+K**: Cut line
- **Ctrl+U**: Paste line
- **Ctrl+G**: Get help
- **Ctrl+O**: Save file (without exiting)

#### VS Code/Cursor Shortcuts
- **Ctrl+F**: Find text
- **Ctrl+H**: Find and replace
- **Ctrl+S**: Save file
- **Ctrl+Z**: Undo
- **Ctrl+Y**: Redo

#### Git Shortcuts
- **git add .**: Add all changes
- **git commit -am "message"**: Add and commit in one command
- **git log --oneline**: View commit history
- **git diff**: View changes

---

## Quick Reference Card

```bash
# View checklist
./fchecklist

# Edit checklist
nano checklist.md

# Save in nano: Ctrl+X, Y, Enter

# Commit changes
git add checklist.md
git commit -m "Updated checklist"

# Check progress
grep -c "\[x\]" checklist.md  # Approved items
grep -c "\[ \]" checklist.md  # Remaining items
```

---

**Last Updated**: $(date)
**Version**: 1.0
**Total Checklist Items**: 200+

