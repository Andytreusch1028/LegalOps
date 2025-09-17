# LegalOps GitHub Setup Script
# Run this script AFTER installing Git

Write-Host "🚀 LegalOps GitHub Setup Script" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Check if Git is installed
try {
    $gitVersion = git --version
    Write-Host "✅ Git is installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git is not installed. Please install Git first:" -ForegroundColor Red
    Write-Host "   https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "   Then restart your terminal and run this script again." -ForegroundColor Yellow
    exit 1
}

# Get user information
Write-Host "`n📝 Git Configuration" -ForegroundColor Cyan
$userName = Read-Host "Enter your full name (for Git commits)"
$userEmail = Read-Host "Enter your email address"
$githubUsername = Read-Host "Enter your GitHub username"

# Configure Git
Write-Host "`n🔧 Configuring Git..." -ForegroundColor Yellow
git config --global user.name "$userName"
git config --global user.email "$userEmail"
git config --global init.defaultBranch main
git config --global core.autocrlf true

Write-Host "✅ Git configured successfully" -ForegroundColor Green

# Initialize Git repository
Write-Host "`n📁 Initializing Git repository..." -ForegroundColor Yellow
git init

# Add all files
Write-Host "📦 Adding files to Git..." -ForegroundColor Yellow
git add .

# Create initial commit
Write-Host "💾 Creating initial commit..." -ForegroundColor Yellow
git commit -m "Initial commit: LegalOps Docker setup with PostgreSQL, Redis, Elasticsearch, and Nginx"

Write-Host "✅ Initial commit created" -ForegroundColor Green

# Add GitHub remote
Write-Host "`n🔗 Setting up GitHub remote..." -ForegroundColor Yellow
$githubUrl = "https://github.com/$githubUsername/LegalOps.git"
git remote add origin $githubUrl

Write-Host "✅ GitHub remote added: $githubUrl" -ForegroundColor Green

# Display next steps
Write-Host "`n🎉 Setup Complete!" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Create a new repository on GitHub:" -ForegroundColor White
Write-Host "   - Go to: https://github.com/new" -ForegroundColor Gray
Write-Host "   - Repository name: LegalOps" -ForegroundColor Gray
Write-Host "   - Description: Legal Operations Management System" -ForegroundColor Gray
Write-Host "   - Choose Public or Private" -ForegroundColor Gray
Write-Host "   - DO NOT initialize with README, .gitignore, or license" -ForegroundColor Gray
Write-Host "   - Click 'Create repository'" -ForegroundColor Gray

Write-Host "`n2. Push to GitHub:" -ForegroundColor White
Write-Host "   git push -u origin main" -ForegroundColor Gray

Write-Host "`n3. Verify connection:" -ForegroundColor White
Write-Host "   git remote -v" -ForegroundColor Gray

Write-Host "`n📚 Your project is ready for GitHub!" -ForegroundColor Green
Write-Host "All files have been prepared and committed locally." -ForegroundColor Green
