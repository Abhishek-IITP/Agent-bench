# Database Operations Guide

This guide covers daily database operations including starting/stopping the database, running benchmarks, backup/restore procedures, data management, and maintenance tasks.

## Table of Contents

- [Starting and Stopping](#starting-and-stopping)
- [Running Benchmarks](#running-benchmarks)
- [Viewing Data](#viewing-data)
- [Backup and Restore](#backup-and-restore)
- [Database Reset](#database-reset)
- [Logs and Monitoring](#logs-and-monitoring)
- [Connection Strings](#connection-strings)
- [Maintenance Tasks](#maintenance-tasks)

## Starting and Stopping

### Start Database

Start the PostgreSQL container in detached mode:

```cmd
docker compose up -d postgres
```

**Expected Output**:
```
[+] Running 1/1
 ✔ Container agentbench-db  Started
```

**Verify it's running**:
```cmd
docker ps | findstr agentbench-db
```

**Quick Script**: Use the provided utility script:
```cmd
scripts\start-db.cmd
```

### Stop Database

Stop the PostgreSQL container:

```cmd
docker compose stop postgres
```

**Expected Output**:
```
[+] Stopping 1/1
 ✔ Container agentbench-db  Stopped
```

**Note**: This stops the container but preserves data in the volume.

**Quick Script**: Use the provided utility script:
```cmd
scripts\stop-db.cmd
```

### Restart Database

Restart the container (useful after configuration changes):

```cmd
docker compose restart postgres
```

### Check Status

Check if the database container is running and healthy:

```cmd
docker ps | findstr agentbench-db
```

Look for **(healthy)** in the status column.

**Direct health check**:
```cmd
docker exec agentbench-db pg_isready -U postgres
```

**Expected Output**:
```
/var/run/postgresql:5432 - accepting connections
```

## Running Benchmarks

### Basic Benchmark Run

Run a single benchmark task with database storage:

```cmd
agentbench bench find-database-files --agent openai --model gpt-4 --runs 1
```

This will:
1. Store task metadata in the `tasks` table
2. Store agent configuration in the `agents` table
3. Execute the benchmark
4. Store run record in the `runs` table
5. Store results in the `results` table
6. Store execution metrics in the `execution_metrics` table

### Multi-Run Benchmark

Run the same task multiple times for reliability testing:

```cmd
agentbench bench find-database-files --agent openai --model gpt-4 --runs 10
```

This additionally stores:
- Aggregated metrics in `multi_run_metrics` table
- Success rate, confidence intervals, and reliability scores

### Verify Data was Stored

After running a benchmark, verify data in the database:

```cmd
docker exec -it agentbench-db psql -U postgres -d agentbench
```

Then run SQL queries:

```sql
-- Check total runs
SELECT COUNT(*) FROM runs;

-- Check recent runs
SELECT id, task_id, started_at, success, duration 
FROM runs 
ORDER BY started_at DESC 
LIMIT 5;

-- Check task statistics
SELECT 
    task_id,
    COUNT(*) as total_runs,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) as passes,
    AVG(duration) as avg_duration
FROM runs
GROUP BY task_id;

-- Exit psql
\q
```

### Fallback to File-Based Storage

If the database is unavailable, the runner automatically falls back to file-based storage in the `results/` directory:

```cmd
# Stop database
docker compose stop postgres

# Run benchmark (will use file storage)
agentbench bench find-database-files --agent openai --model gpt-4 --runs 1
```

Results will be saved as JSON files in `results/<task-id>/`.

## Viewing Data

### Using psql (Interactive SQL Shell)

Connect to the database:

```cmd
docker exec -it agentbench-db psql -U postgres -d agentbench
```

**Useful Commands**:

```sql
-- List all tables
\dt

-- Describe a table structure
\d tasks
\d runs
\d results

-- View recent runs with agent names
SELECT r.id, r.task_id, a.name as agent, r.success, r.duration
FROM runs r
JOIN agents a ON r.agent_id = a.id
ORDER BY r.started_at DESC
LIMIT 10;

-- View task health classifications
SELECT task_id, health_status, success_rate, n_agents
FROM task_health
ORDER BY success_rate DESC;

-- View leaderboard
SELECT 
    a.name as agent,
    COUNT(DISTINCT r.task_id) as tasks_solved,
    AVG(CASE WHEN r.success THEN 1.0 ELSE 0.0 END) as success_rate,
    AVG(r.duration) as avg_duration
FROM agents a
LEFT JOIN runs r ON a.id = r.agent_id
GROUP BY a.id, a.name
ORDER BY success_rate DESC;

-- Exit
\q
```

### Using SQL Scripts

Run SQL queries from a file:

```cmd
docker exec -i agentbench-db psql -U postgres -d agentbench < query.sql
```

### Using the API

Query data via the REST API:

**List all tasks**:
```cmd
curl http://localhost:3001/api/tasks
```

**Get task details**:
```cmd
curl http://localhost:3001/api/tasks/find-database-files
```

**List recent runs**:
```cmd
curl http://localhost:3001/api/runs?limit=10
```

**Get run details**:
```cmd
curl "http://localhost:3001/api/runs/<run-id>"
```

**View leaderboard**:
```cmd
curl http://localhost:3001/api/leaderboard
```

### Using the Dashboard

Start the web dashboard to visualize results:

```cmd
cd dashboard\web
bun install
bun run dev
```

Open browser to http://localhost:3000 and navigate through:
- **Tasks page**: View all benchmark tasks and statistics
- **Runs page**: View all benchmark runs with filtering
- **Health page**: View task health classifications
- **Leaderboard page**: View agent rankings

## Backup and Restore

### Create a Backup

**Method 1: Using pg_dump (Recommended)**

Create a complete database backup:

```cmd
docker exec agentbench-db pg_dump -U postgres agentbench > backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%.sql
```

This creates a file like `backup_20240115.sql` with all data and schema.

**Method 2: Using the utility script**

```cmd
scripts\backup-db.cmd
```

This creates a timestamped backup in the `backups/` directory.

**What gets backed up**:
- All table schemas
- All data in all tables
- Indexes and constraints
- Sequences (for auto-increment IDs)

### Restore from Backup

**Prerequisites**:
- Database container must be running
- Backup file must exist

**Restore procedure**:

```cmd
# Stop any running API or dashboard connections
# Then restore
docker exec -i agentbench-db psql -U postgres -d agentbench < backup_20240115.sql
```

**Warning**: This will append data to existing tables. To restore to a clean state, [reset the database](#database-reset) first.

### Backup to a Different Database

Create a separate backup database:

```cmd
# Create new database
docker exec agentbench-db psql -U postgres -c "CREATE DATABASE agentbench_backup;"

# Dump and restore
docker exec agentbench-db pg_dump -U postgres agentbench | docker exec -i agentbench-db psql -U postgres -d agentbench_backup
```

### Automated Backups

Create a scheduled task (Windows Task Scheduler) to run daily backups:

**Script** (`scripts\backup-db.cmd`):
```cmd
@echo off
set BACKUP_DIR=backups
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%
set BACKUP_FILE=%BACKUP_DIR%\agentbench_%TIMESTAMP%.sql

if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%

echo Creating backup: %BACKUP_FILE%
docker exec agentbench-db pg_dump -U postgres agentbench > %BACKUP_FILE%

echo Backup completed successfully
```

**Schedule in Task Scheduler**:
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 2 AM
4. Action: Start a program
5. Program: `C:\path\to\agent-bench\scripts\backup-db.cmd`

## Database Reset

### Reset All Data (Keep Schema)

Delete all data but keep table structures:

```cmd
# Connect to database
docker exec -it agentbench-db psql -U postgres -d agentbench

# Run TRUNCATE commands
TRUNCATE TABLE execution_metrics CASCADE;
TRUNCATE TABLE replays CASCADE;
TRUNCATE TABLE results CASCADE;
TRUNCATE TABLE runs CASCADE;
TRUNCATE TABLE multi_run_metrics CASCADE;
TRUNCATE TABLE task_health CASCADE;
TRUNCATE TABLE task_difficulty_calibration CASCADE;
TRUNCATE TABLE agents CASCADE;
TRUNCATE TABLE tasks CASCADE;

# Exit
\q
```

**Quick Script**: Use the provided utility:
```cmd
scripts\reset-db.cmd
```

### Complete Reset (Drop and Recreate)

Completely remove and recreate the database:

```cmd
# Stop container and remove volume
docker compose down -v

# Start container (schema auto-applies)
docker compose up -d postgres

# Wait for healthy status
timeout /t 10

# Verify tables
docker exec -it agentbench-db psql -U postgres -d agentbench -c "\dt"
```

**Warning**: This permanently deletes all data. Create a backup first if needed.

### Reset Specific Tables

Delete data from specific tables only:

```cmd
docker exec -it agentbench-db psql -U postgres -d agentbench -c "TRUNCATE TABLE runs CASCADE;"
```

The `CASCADE` option automatically deletes dependent records in related tables (e.g., results, replays).

## Logs and Monitoring

### View Container Logs

View recent database logs:

```cmd
docker logs agentbench-db
```

**Follow logs in real-time**:
```cmd
docker logs -f agentbench-db
```

**View last 50 lines**:
```cmd
docker logs --tail 50 agentbench-db
```

### PostgreSQL Query Logs

Enable query logging for debugging:

```cmd
docker exec -it agentbench-db psql -U postgres -d agentbench -c "ALTER SYSTEM SET log_statement = 'all';"
docker compose restart postgres
```

**View query logs**:
```cmd
docker logs agentbench-db | findstr "LOG:  statement:"
```

**Disable query logging** (reduces performance overhead):
```cmd
docker exec -it agentbench-db psql -U postgres -d agentbench -c "ALTER SYSTEM SET log_statement = 'none';"
docker compose restart postgres
```

### Monitor Database Size

Check database and table sizes:

```cmd
docker exec -it agentbench-db psql -U postgres -d agentbench
```

```sql
-- Database size
SELECT pg_size_pretty(pg_database_size('agentbench'));

-- Table sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

\q
```

### Monitor Active Connections

Check active database connections:

```sql
SELECT 
    datname,
    count(*) as connections
FROM pg_stat_activity
WHERE datname = 'agentbench'
GROUP BY datname;
```

### Performance Monitoring

View slow queries:

```sql
SELECT 
    pid,
    now() - query_start as duration,
    query
FROM pg_stat_activity
WHERE state = 'active'
AND query NOT LIKE '%pg_stat_activity%'
ORDER BY duration DESC;
```

## Connection Strings

### Standard Connection String

```
postgresql://postgres:postgres@localhost:5432/agentbench
```

### Python (psycopg2)

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="agentbench",
    user="postgres",
    password="postgres"
)
```

### TypeScript (postgres library)

```typescript
import postgres from 'postgres';

const sql = postgres({
  host: 'localhost',
  port: 5432,
  database: 'agentbench',
  user: 'postgres',
  password: 'postgres',
});
```

### Using Environment Variables

Python:
```python
import os
from runner.storage import Storage

storage = Storage(
    db_host=os.getenv("DB_HOST", "localhost"),
    db_port=int(os.getenv("DB_PORT", "5432")),
    db_name=os.getenv("DB_NAME", "agentbench"),
    db_user=os.getenv("DB_USER", "postgres"),
    db_password=os.getenv("DB_PASSWORD", "postgres"),
)
```

TypeScript:
```typescript
const sql = postgres({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME || 'agentbench',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'postgres',
});
```

## Maintenance Tasks

### Vacuum Database

Reclaim storage and optimize performance:

```cmd
docker exec agentbench-db psql -U postgres -d agentbench -c "VACUUM ANALYZE;"
```

Run this weekly or after large data deletions.

### Update Statistics

Update query planner statistics for better performance:

```cmd
docker exec agentbench-db psql -U postgres -d agentbench -c "ANALYZE;"
```

### Reindex Database

Rebuild all indexes (useful after data corruption or performance issues):

```cmd
docker exec agentbench-db psql -U postgres -d agentbench -c "REINDEX DATABASE agentbench;"
```

**Warning**: This can take several minutes on large databases and blocks write operations.

### Check for Bloat

Identify tables with excessive dead tuples:

```sql
SELECT 
    schemaname,
    tablename,
    n_live_tup,
    n_dead_tup,
    round(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) as dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY dead_pct DESC;
```

If `dead_pct` is high (>20%), run VACUUM on those tables.

### Archive Old Data

Archive old benchmark runs to keep database performant:

```sql
-- Move runs older than 90 days to archive table
CREATE TABLE IF NOT EXISTS runs_archive (LIKE runs INCLUDING ALL);

INSERT INTO runs_archive
SELECT * FROM runs
WHERE started_at < NOW() - INTERVAL '90 days';

DELETE FROM runs
WHERE started_at < NOW() - INTERVAL '90 days';

-- Vacuum to reclaim space
VACUUM ANALYZE runs;
```

### Update Docker Image

Update to the latest PostgreSQL 16 image:

```cmd
# Pull latest image
docker compose pull postgres

# Recreate container with new image
docker compose up -d postgres
```

Data in the named volume is preserved during updates.

## Common Operations Quick Reference

| Operation | Command |
|-----------|---------|
| Start database | `docker compose up -d postgres` |
| Stop database | `docker compose stop postgres` |
| Restart database | `docker compose restart postgres` |
| View logs | `docker logs agentbench-db` |
| Connect to psql | `docker exec -it agentbench-db psql -U postgres -d agentbench` |
| Check status | `docker ps \| findstr agentbench-db` |
| Health check | `docker exec agentbench-db pg_isready -U postgres` |
| Create backup | `scripts\backup-db.cmd` |
| Reset data | `scripts\reset-db.cmd` |
| Run benchmark | `agentbench bench <task-id> --agent openai --runs 10` |
| View runs | `curl http://localhost:3001/api/runs` |

## Troubleshooting

### Database Won't Start

1. Check Docker is running: `docker info`
2. Check logs: `docker logs agentbench-db`
3. Verify port 5432 is available: `netstat -ano | findstr :5432`
4. Try complete reset: `docker compose down -v && docker compose up -d postgres`

### Slow Queries

1. Check for missing indexes
2. Run ANALYZE to update statistics
3. Review query execution plans with EXPLAIN
4. Consider adding indexes on frequently queried columns

### Connection Timeout

1. Check firewall settings
2. Verify container is healthy: `docker ps`
3. Check connection limit: `SHOW max_connections;`
4. Restart container: `docker compose restart postgres`

### Data Not Persisting

1. Verify named volume exists: `docker volume ls | findstr postgres_data`
2. Check volume mount in `docker-compose.yml`
3. Don't use `docker compose down -v` unless you want to delete data

## Next Steps

- [DATABASE-SETUP.md](DATABASE-SETUP.md) - Initial database setup guide
- [MIGRATION-GUIDE.md](MIGRATION-GUIDE.md) - Migrate from file-based storage
- [PostgreSQL Documentation](https://www.postgresql.org/docs/16/) - Official docs
