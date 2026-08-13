@echo off
REM Start the AgentBench PostgreSQL database container
REM This script starts the database in detached mode and verifies it's healthy

echo ========================================
echo AgentBench Database - Start
echo ========================================
echo.

echo Starting PostgreSQL container...
docker compose up -d postgres

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to start database container
    echo.
    echo Troubleshooting steps:
    echo   1. Verify Docker Desktop is running
    echo   2. Check if port 5432 is available: netstat -ano ^| findstr :5432
    echo   3. View logs: docker logs agentbench-db
    echo.
    exit /b 1
)

echo.
echo Waiting for database to become healthy...
timeout /t 3 /nobreak >nul

REM Check container status
docker ps | findstr agentbench-db >nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Container is not running
    echo Check logs with: docker logs agentbench-db
    echo.
    exit /b 1
)

echo.
echo Checking database health...
docker exec agentbench-db pg_isready -U postgres >nul 2>&1

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS: Database is running and healthy
    echo ========================================
    echo.
    echo Connection details:
    echo   Host: localhost
    echo   Port: 5432
    echo   Database: agentbench
    echo   User: postgres
    echo.
    echo Next steps:
    echo   - Run benchmarks: agentbench bench ^<task-id^> --agent openai --runs 10
    echo   - View data: docker exec -it agentbench-db psql -U postgres -d agentbench
    echo   - Start API: cd dashboard\api ^&^& bun run src/index.ts
    echo.
) else (
    echo.
    echo WARNING: Container is running but not yet healthy
    echo Wait a few more seconds and check status:
    echo   docker ps ^| findstr agentbench-db
    echo.
    exit /b 0
)

exit /b 0
