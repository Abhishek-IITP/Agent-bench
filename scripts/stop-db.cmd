@echo off
REM Stop the AgentBench PostgreSQL database container
REM This stops the container but preserves data in the volume

echo ========================================
echo AgentBench Database - Stop
echo ========================================
echo.

echo Stopping PostgreSQL container...
docker compose stop postgres

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to stop database container
    echo.
    echo Troubleshooting:
    echo   - Check if container exists: docker ps -a ^| findstr agentbench-db
    echo   - View container status: docker ps
    echo   - Force remove: docker rm -f agentbench-db
    echo.
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS: Database stopped
echo ========================================
echo.
echo The database container is stopped but data is preserved.
echo.
echo To start again:
echo   scripts\start-db.cmd
echo.
echo To completely remove (WARNING: deletes all data):
echo   docker compose down -v
echo.

exit /b 0
