# Git and GitHub Setup Guide for LegalOps

## Step 1: Install Git for Windows

1. **Download Git for Windows**:
   - Go to: https://git-scm.com/download/win
   - Download the latest version (64-bit)
   - Run the installer with default settings

2. **Verify Installation**:
   - Open a new PowerShell/Command Prompt window
   - Run: `git --version`
   - You should see the Git version number

## Step 2: Configure Git (First Time Setup)

```bash
# Set your name and email (replace with your actual details)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default branch name to 'main'
git config --global init.defaultBranch main

# Set line ending preferences for Windows
git config --global core.autocrlf true
```

## Step 3: Create GitHub Repository

1. Go to https://github.com and sign in
2. Click the "+" icon → "New repository"
3. Repository name: `LegalOps`
4. Description: `Legal Operations Management System`
5. Choose Public or Private
6. **DO NOT** check "Add a README file"
7. **DO NOT** check "Add .gitignore"
8. **DO NOT** check "Choose a license"
9. Click "Create repository"

## Step 4: Link Local Project to GitHub

After installing Git, run these commands in the LegalOps directory:

```bash
# Initialize Git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: LegalOps Docker setup with PostgreSQL, Redis, Elasticsearch, and Nginx"

# Add GitHub remote (replace YOUR_USERNAME with your actual GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/LegalOps.git

# Push to GitHub
git push -u origin main
```

## Step 5: Verify Connection

```bash
# Check remote connection
git remote -v

# Check status
git status
```

## Troubleshooting

- **Authentication Issues**: You may need to set up a Personal Access Token
- **Branch Issues**: If you get branch errors, try: `git branch -M main`
- **Force Push**: If needed: `git push -u origin main --force`

## Next Steps

After successful setup:
1. Create feature branches for development
2. Set up GitHub Actions for CI/CD
3. Add collaborators if needed
4. Configure branch protection rules
