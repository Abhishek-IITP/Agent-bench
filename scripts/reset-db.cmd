@echo off
REM Reset the AgentBench PostgreSQL database
REM WARNING: This deletes all data but keeps the schema

echo ========================================
echo AgentBench Database - Reset
echo ========================================
echo.
echo WARNING: This will delete ALL data from the database!
echo.
echo Tables that will be cleared:
echo   - tasks
echo   - agents
echo   - runs
echo   - results
echo   - replays
echo   - execution_metrics
echo   - multi_run_metrics
echo   - task_health
echo   - task_difficulty_calibration
echo.
echo The schema will be preserved.
echo.

REM Prompt for confirmation
set /p CONFIRM="Are you sure you want to reset the database? (yes/no): "
if /i not "%CONFIRM%"=="yes" (
    echo.
    echo Reset cancelled.
    echo.
    exit /b 0
)

echo.
echo Checking if database is running...

REM Check if container is running
docker ps | findstr agentbench-db >nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Database container is not running
    echo Start it first with: scripts\start-db.cmd
    echo.
    exit /b 1
)

echo Database is running. Proceeding with reset...
echo.

REM Create backup before reset (safety measure)
set /p CREATE_BACKUP="Create a backup before reset? (yes/no): "
if /i "%CREATE_BACKUP%"=="yes" (
    echo.
    echo Creating automatic backup...
    call scripts\backup-db.cmd
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo Backup failed. Reset cancelled for safety.
        echo.
        exit /b 1
    )
    echo.
)

echo Truncating all tables...
echo.

REM Execute TRUNCATE commands
docker exec agentbench-db psql -U postgres -d agentbench -c "TRUNCATE TABLE execution_metrics CASCADE;" >nul
docker exec agentbench-db psql -U postgres -d agentbench -c "TRUNCATE TABLE replays CASCADE;" >nul
docker exec agentbench-db psql -U postgres -d agentbench -c "TRUNCATE TABLE results CASCADE;" >nul
docker exec agentbench-db psql -U postgres -d agentbench -c "TRUNCATE TABLE runs CASCADE;" >nul
docker exec agentbench-db psql -U postgres -d agentbench -c "TRUNCATE TABLE multi_run_metrics CASCADE;" >nul
docker exec agentbench-db psql -U postgres -d agentbench -c "TRUNCATE TABLE task_health CASCADE;" >nul
docker exec agentbench-db psql -U postgres -d agentbench -c "TRUNCATE TABLE task_difficulty_calibration CASCADE;" >nul
docker exec agentbench-db psql -U postgres -d agentbench -c "TRUNCATE TABLE agents CASCADE;" >nul
docker exec agentbench-db psql -U postgres -d agentbench -c "TRUNCATE TABLE tasks CASCADE;" >nul

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Reset failed
    echo.
    echo Troubleshooting:
    echo   - Check database connection: docker exec agentbench-db pg_isready -U postgres
    echo   - View logs: docker logs agentbench-db
    echo   - Try complete reset: docker compose down -v ^&^& docker compose up -d postgres
    echo.
    exit /b 1
)

REM Verify tables are empty
echo Verifying reset...
docker exec agentbench-db psql -U postgres -d agentbench -c "SELECT COUNT(*) FROM runs;" | findstr "0" >nul

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS: Database reset complete
    echo ========================================
    echo.
    echo All data has been deleted.
    echo Schema and table structures are preserved.
    echo.
    echo The database is ready for new benchmark runs.
    echo.
) else (
    echo.
    echo WARNING: Reset may not be complete
    echo Verify with: docker exec -it agentbench-db psql -U postgres -d agentbench -c "SELECT COUNT(*) FROM runs;"
    echo.
)

exit /b 0
