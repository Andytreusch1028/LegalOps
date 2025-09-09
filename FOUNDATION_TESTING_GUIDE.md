# Foundation Testing Guide

## Prerequisites Check

### 1. Docker Desktop
**CRITICAL**: Docker Desktop must be running before testing!

**To start Docker Desktop:**
- Open Docker Desktop application
- Wait for it to fully start (green status indicator)
- Verify it's running: `docker --version` should work

### 2. PowerShell Workarounds
**Remember**: These commands stall in PowerShell:
- `docker-compose --version` → Use `docker compose version`
- `git add .` → Use batch files or VS Code Git
- `mkdir` → Use `write` tool
- `cd ..` → Use `Set-Location ..`

## Testing Steps

### Step 1: Start Docker Desktop
1. Open Docker Desktop application
2. Wait for "Engine running" status
3. Verify with: `docker --version`

### Step 2: Test Environment
Run the test batch file:
```bash
.\test_environment.bat
```

### Step 3: Manual Testing (if batch file fails)
```bash
# Check Docker
docker --version
docker compose version

# Start services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs --tail=20
```

### Step 4: Test Individual Services
```bash
# Test database connection
docker compose exec postgres psql -U legalops_user -d legalops -c "SELECT version();"

# Test backend
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000
```

## Expected Results

### ✅ Success Indicators:
- Docker containers start without errors
- PostgreSQL accessible on port 5432
- Backend API accessible on port 8000
- Frontend accessible on port 3000
- No error messages in logs

### ❌ Common Issues:
- **Docker Desktop not running**: Start Docker Desktop first
- **Port conflicts**: Check if ports 3000, 8000, 5432 are free
- **Permission issues**: Run as administrator if needed
- **Memory issues**: Ensure Docker has enough memory allocated

## Next Steps After Successful Test

1. **Verify Database Connection**: Test PostgreSQL connectivity
2. **Test API Endpoints**: Verify backend health check
3. **Test Frontend**: Verify React app loads
4. **Test Authentication**: Verify login/register flow
5. **Test Error Handling**: Verify error boundaries work

## Troubleshooting

### If Docker Desktop won't start:
1. Restart Docker Desktop
2. Check Windows features (WSL2, Hyper-V)
3. Run as administrator
4. Check system resources

### If containers fail to start:
1. Check logs: `docker compose logs`
2. Check port availability
3. Check Docker memory allocation
4. Restart Docker Desktop
