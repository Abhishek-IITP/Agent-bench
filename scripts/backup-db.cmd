@echo off
REM Backup the AgentBench PostgreSQL database
REM Creates a timestamped SQL dump file in the backups directory

echo ========================================
echo AgentBench Database - Backup
echo ========================================
echo.

REM Create backups directory if it doesn't exist
if not exist backups mkdir backups

REM Generate timestamp (YYYYMMDD_HHMMSS)
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%

REM Set backup filename
set BACKUP_FILE=backups\agentbench_%TIMESTAMP%.sql

echo Creating backup: %BACKUP_FILE%
echo.

REM Check if container is running
docker ps | findstr agentbench-db >nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Database container is not running
    echo Start it first with: scripts\start-db.cmd
    echo.
    exit /b 1
)

REM Create backup
docker exec agentbench-db pg_dump -U postgres agentbench > %BACKUP_FILE%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Backup failed
    echo.
    echo Troubleshooting:
    echo   - Verify container is healthy: docker ps ^| findstr agentbench-db
    echo   - Check database connection: docker exec agentbench-db pg_isready -U postgres
    echo   - View logs: docker logs agentbench-db
    echo.
    exit /b 1
)

REM Check backup file size
for %%A in (%BACKUP_FILE%) do set FILESIZE=%%~zA

if %FILESIZE% LSS 1000 (
    echo.
    echo WARNING: Backup file is very small (%FILESIZE% bytes^)
    echo The backup may be incomplete or database may be empty
    echo.
) else (
    echo.
    echo ========================================
    echo SUCCESS: Backup completed
    echo ========================================
    echo.
    echo Backup file: %BACKUP_FILE%
    echo File size: %FILESIZE% bytes
    echo.
    echo To restore this backup:
    echo   docker exec -i agentbench-db psql -U postgres -d agentbench ^< %BACKUP_FILE%
    echo.
    echo CAUTION: Restoring will append data to existing tables.
    echo For a clean restore, reset the database first:
    echo   scripts\reset-db.cmd
    echo.
)

REM Show backup directory contents
echo Recent backups:
dir /b /o-d backups\agentbench_*.sql 2>nul | findstr /n "^"
if %ERRORLEVEL% NEQ 0 (
    echo   (no other backups found)
)
echo.

exit /b 0
