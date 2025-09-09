@echo off
echo ========================================
echo Legal Ops Foundation Testing
echo ========================================
echo.

echo 1. Checking current directory...
echo Current directory: %CD%
echo.

echo 2. Checking Docker...
docker --version
echo.

echo 3. Checking Docker Compose...
docker compose version
echo.

echo 4. Building and starting services...
docker compose up -d --build
echo.

echo 5. Waiting for services to start...
timeout /t 10 /nobreak
echo.

echo 6. Checking container status...
docker compose ps
echo.

echo 7. Testing database connection...
docker compose exec postgres psql -U legalops_user -d legalops -c "SELECT version();" 2>nul
if %errorlevel% equ 0 (
    echo Database connection: SUCCESS
) else (
    echo Database connection: FAILED
)
echo.

echo 8. Testing backend health...
curl -s http://localhost:8000/health 2>nul
if %errorlevel% equ 0 (
    echo Backend health check: SUCCESS
) else (
    echo Backend health check: FAILED
)
echo.

echo 9. Testing frontend...
curl -s http://localhost:3000 2>nul
if %errorlevel% equ 0 (
    echo Frontend accessibility: SUCCESS
) else (
    echo Frontend accessibility: FAILED
)
echo.

echo 10. Viewing recent logs...
docker compose logs --tail=10
echo.

echo ========================================
echo Foundation testing completed!
echo ========================================
pause
