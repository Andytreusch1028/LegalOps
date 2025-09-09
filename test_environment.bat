@echo off
echo Testing Legal Ops Foundation Environment...
echo.

echo 1. Checking Docker...
docker --version
echo.

echo 2. Checking Docker Compose...
docker compose version
echo.

echo 3. Checking if containers are running...
docker compose ps
echo.

echo 4. Starting development environment...
docker compose up -d
echo.

echo 5. Checking container status...
docker compose ps
echo.

echo 6. Viewing logs...
docker compose logs --tail=20
echo.

echo Environment test completed!
pause
