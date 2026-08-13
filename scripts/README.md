# AgentBench Scripts

This directory contains utility scripts for database management, verification, system health checks, and data operations.

## Quick Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `start-db.cmd` | Start database | `scripts\start-db.cmd` |
| `stop-db.cmd` | Stop database | `scripts\stop-db.cmd` |
| `backup-db.cmd` | Backup database | `scripts\backup-db.cmd` |
| `reset-db.cmd` | Reset database | `scripts\reset-db.cmd` |
| `seed-sample-data.py` | Seed sample data | `python scripts\seed-sample-data.py` |
| `test-connection.py` | Test connection | `python scripts\test-connection.py` |
| `verify-db.py` | Verify schema | `python scripts\verify-db.py` |
| `check-health.py` | Health check | `python scripts\check-health.py` |

## Available Scripts

### 1. test-connection.py

**Purpose**: Simple database connection test

**Usage**:
```bash
python scripts/test-connection.py
```

**What it does**:
- Tests basic connection to PostgreSQL database
- Displays PostgreSQL version
- Shows table count
- Exits with code 0 on success, 1 on failure

**When to use**:
- Quick check if database is accessible
- Verify basic connectivity after starting Docker container
- Simple troubleshooting

---

### 2. verify-db.py

**Purpose**: Comprehensive database schema verification

**Usage**:
```bash
python scripts/verify-db.py
```

**What it does**:
- Verifies all 9 expected tables exist
- Checks all 10 indexes are created
- Validates foreign key constraints (16 constraints)
- Displays record counts for all tables
- Provides detailed troubleshooting guidance if issues found

**Expected tables**:
1. `tasks` - Task metadata
2. `agents` - Agent configurations
3. `runs` - Execution records
4. `results` - Test evaluation results
5. `replays` - Execution traces
6. `execution_metrics` - Performance metrics
7. `multi_run_metrics` - Aggregated statistics
8. `task_health` - Task health classifications
9. `task_difficulty_calibration` - Difficulty analysis

**When to use**:
- After initial database setup
- After schema migrations
- When debugging database issues
- Before running benchmarks

**Example output**:
```
======================================================================
AgentBench Database Verification
======================================================================

🔌 Connection Details:
  Host: 127.0.0.1
  Port: 5432
  Database: agentbench
  User: postgres

✓ PostgreSQL version: PostgreSQL 16.14

📊 Table Verification:
  Expected: 9 tables
  Found: 9 tables
  ✓ All expected tables exist

🔍 Index Verification:
  Expected: 10 indexes
  Found: 10 expected indexes
  ✓ All expected indexes exist

🔗 Foreign Key Constraints:
  Found: 16 constraints
  ✓ Foreign key constraints verified

📈 Table Record Counts:
  tasks                               0 records
  agents                              0 records
  ...

======================================================================
✅ Database verification PASSED - All checks successful!
======================================================================
```

---

### 3. start-db.cmd

**Purpose**: Start the PostgreSQL database container

**Usage**:
```cmd
scripts\start-db.cmd
```

**What it does**:
- Starts the PostgreSQL container in detached mode
- Waits for the database to become healthy
- Verifies the database is accessible
- Displays connection details and next steps

**When to use**:
- Starting development work
- After system restart
- When database container is stopped

**Example output**:
```
========================================
AgentBench Database - Start
========================================

Starting PostgreSQL container...
Waiting for database to become healthy...
Checking database health...

========================================
SUCCESS: Database is running and healthy
========================================

Connection details:
  Host: localhost
  Port: 5432
  Database: agentbench
  User: postgres

Next steps:
  - Run benchmarks: agentbench bench <task-id> --agent openai --runs 10
  - View data: docker exec -it agentbench-db psql -U postgres -d agentbench
  - Start API: cd dashboard\api && bun run src/index.ts
```

---

### 4. stop-db.cmd

**Purpose**: Stop the PostgreSQL database container

**Usage**:
```cmd
scripts\stop-db.cmd
```

**What it does**:
- Stops the PostgreSQL container gracefully
- Preserves all data in the volume
- Confirms successful shutdown

**When to use**:
- Ending development session
- Freeing up system resources
- Before system maintenance

**Note**: Data is NOT deleted. Use `docker compose down -v` to delete data.

---

### 5. backup-db.cmd

**Purpose**: Create a timestamped database backup

**Usage**:
```cmd
scripts\backup-db.cmd
```

**What it does**:
- Creates `backups/` directory if needed
- Generates timestamped backup file (e.g., `agentbench_20240115_143022.sql`)
- Uses `pg_dump` to create complete database dump
- Displays backup file location and size
- Shows restore instructions

**When to use**:
- Before making risky changes
- Before database reset
- Regular scheduled backups
- Before database migrations

**Example output**:
```
========================================
AgentBench Database - Backup
========================================

Creating backup: backups\agentbench_20240115_143022.sql

========================================
SUCCESS: Backup completed
========================================

Backup file: backups\agentbench_20240115_143022.sql
File size: 458392 bytes

To restore this backup:
  docker exec -i agentbench-db psql -U postgres -d agentbench < backups\agentbench_20240115_143022.sql
```

---

### 6. reset-db.cmd

**Purpose**: Delete all data from the database (keeps schema)

**Usage**:
```cmd
scripts\reset-db.cmd
```

**What it does**:
- Prompts for confirmation (requires "yes")
- Optionally creates automatic backup
- Truncates all tables (CASCADE deletes)
- Preserves schema and table structures
- Verifies reset was successful

**When to use**:
- Starting fresh testing
- Clearing old benchmark data
- After importing corrupted data
- Development cleanup

**Warning**: This permanently deletes ALL benchmark data!

**Example output**:
```
========================================
AgentBench Database - Reset
========================================

WARNING: This will delete ALL data from the database!

Tables that will be cleared:
  - tasks
  - agents
  - runs
  - results
  - replays
  - execution_metrics
  - multi_run_metrics
  - task_health
  - task_difficulty_calibration

Are you sure you want to reset the database? (yes/no): yes

Create a backup before reset? (yes/no): yes

Creating automatic backup...
Truncating all tables...
Verifying reset...

========================================
SUCCESS: Database reset complete
========================================

All data has been deleted.
Schema and table structures are preserved.
```

---

### 7. seed-sample-data.py

**Purpose**: Populate database with realistic sample data for testing

**Usage**:
```cmd
# Seed with default settings (5 runs per combo)
python scripts\seed-sample-data.py

# Seed with more runs
python scripts\seed-sample-data.py --runs 10

# Clean existing data first
python scripts\seed-sample-data.py --clean --runs 10

# Verbose output
python scripts\seed-sample-data.py --runs 5 --verbose
```

**What it does**:
- Creates 5 sample tasks (various categories and difficulties)
- Creates 4 sample agents (OpenAI GPT-4, GPT-3.5, Claude variants)
- Generates realistic benchmark runs with:
  - Varying success rates per task/agent combo
  - Realistic durations and scores
  - Execution metrics (commands, files, tokens, cost)
- Computes multi-run aggregated metrics
- Classifies task health
- Displays summary statistics

**Sample data includes**:
- **Tasks**: find-database-files, code-review-task, debug-python-error, json-data-transform, api-integration-test
- **Agents**: openai-gpt-4, openai-gpt-3.5-turbo, anthropic-claude-3-opus, anthropic-claude-3-sonnet
- **Runs**: Configurable (default 5 per task/agent = 100 total runs)

**When to use**:
- Testing dashboard visualization
- Demonstrating the system
- Developing new features
- API endpoint testing
- Performance testing with realistic data

**Example output**:
```
============================================================
AgentBench Sample Data Seeder
============================================================

Connecting to database...
✓ Connected to PostgreSQL at localhost:5432

Creating sample tasks...
✓ Created 5 tasks

Creating sample agents...
✓ Created 4 agents

Creating sample runs (5 per task/agent combo)...
✓ Created 100 runs with results and metrics

Computing multi-run metrics...
✓ Created multi-run metrics

Computing task health...
✓ Created task health classifications

============================================================
Database Summary
============================================================

Records created:
  Tasks: 5
  Agents: 4
  Runs: 100
  Results: 100
  Execution Metrics: 100
  Multi-run Metrics: 20
  Task Health: 5

Sample leaderboard:
  Agent                          Tasks    Success Rate    Avg Duration
  ----------------------------------------------------------------------
  openai-gpt-4                   5        87.5%           234.2s
  anthropic-claude-3-opus        5        82.1%           198.7s
  openai-gpt-3.5-turbo          5        76.3%           189.4s
  anthropic-claude-3-sonnet      5        71.8%           215.3s

Task health summary:
  healthy: 4 tasks
  flaky: 1 tasks

============================================================
✓ Sample data seeding complete!
============================================================

Next steps:
  - View data: docker exec -it agentbench-db psql -U postgres -d agentbench
  - Start API: cd dashboard/api && bun run src/index.ts
  - Start web: cd dashboard/web && bun run dev
  - Open dashboard: http://localhost:3000
```

---

### 8. check-health.py

**Purpose**: System health monitoring for all components

**Usage**:
```bash
# Check all components (database + API)
python scripts/check-health.py

# Check only database (skip API checks)
python scripts/check-health.py --skip-api
```

**What it does**:
- Checks Docker container status
- Tests database connection and accessibility
- Verifies database schema is initialized
- Measures database query performance
- Tests API server availability (unless --skip-api)
- Checks critical API endpoints (unless --skip-api)
- Provides comprehensive troubleshooting guidance

**Health checks performed**:
1. **Docker Container** - Verifies agentbench-db container is running
2. **Database Connection** - Tests PostgreSQL connectivity
3. **Database Schema** - Confirms 9 tables exist
4. **Database Performance** - Measures query latency (should be < 100ms)
5. **API Server** - Checks /api/health endpoint (optional)
6. **API Endpoints** - Tests /api/tasks, /api/runs, /api/health/benchmark (optional)

**When to use**:
- Before starting development work
- After system changes or updates
- When troubleshooting issues
- As part of CI/CD pipeline
- Monitoring production health

**Example output**:
```
======================================================================
AgentBench System Health Check
======================================================================

🔧 Configuration:
  Database: postgres@127.0.0.1:5432/agentbench
  API URL: http://localhost:3001

🏥 Health Checks:
  ✓ Docker Container               Status: Up 39 minutes (healthy)
  ✓ Database Connection            PostgreSQL is accessible
  ✓ Database Schema                9 tables found
  ✓ Database Performance           Query latency: 2.51ms
  ✓ API Server                     API is running on http://localhost:3001
  ✓ API /api/tasks                 Status 200
  ✓ API /api/runs                  Status 200
  ✓ API /api/health/benchmark      Status 200

======================================================================
✅ System Health: HEALTHY - All checks passed
======================================================================
```

---

## Configuration

All scripts use environment variables from `.env` file:

```bash
# Database Configuration
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=agentbench
DB_USER=postgres
DB_PASSWORD=postgres

# API Configuration
API_URL=http://localhost:3001
```

**Default values** (if environment variables not set):
- DB_HOST: `127.0.0.1`
- DB_PORT: `5432`
- DB_NAME: `agentbench`
- DB_USER: `postgres`
- DB_PASSWORD: `postgres`
- API_URL: `http://localhost:3001`

---

## Common Workflows

### Initial Setup Verification

After setting up the database for the first time:

```bash
# 1. Start database
scripts\start-db.cmd

# 2. Test basic connection
python scripts\test-connection.py

# 3. Verify schema
python scripts\verify-db.py

# 4. Check overall health
python scripts\check-health.py --skip-api

# 5. Seed sample data for testing (optional)
python scripts\seed-sample-data.py --runs 10 --clean
```

### Daily Development Startup

Before starting development work:

```bash
# Start database
scripts\start-db.cmd

# Quick health check (database only)
python scripts\check-health.py --skip-api

# If API is running, check everything
python scripts\check-health.py
```

### Daily Development Shutdown

After finishing development work:

```bash
# Stop database (preserves data)
scripts\stop-db.cmd
```

### Troubleshooting Database Issues

If benchmarks aren't storing data or API returns errors:

```bash
# 1. Verify schema
python scripts/verify-db.py

# 2. Check for specific issues
python scripts/check-health.py

# 3. If schema missing, reinitialize
docker exec -i agentbench-db psql -U postgres -d agentbench < runner\db\schema.sql

# 4. Verify again
python scripts/verify-db.py
```

### Pre-Benchmark Checklist

Before running benchmarks:

```bash
# Comprehensive health check
python scripts\check-health.py --skip-api

# Expected: All checks pass with ✅
# If any checks fail, resolve issues before proceeding
```

### Testing Dashboard with Sample Data

To quickly test the dashboard with realistic data:

```bash
# 1. Reset database (optional, clears old data)
scripts\reset-db.cmd

# 2. Seed sample data
python scripts\seed-sample-data.py --runs 10 --clean

# 3. Start API backend
cd dashboard\api
bun run src/index.ts

# 4. Start web frontend (in another terminal)
cd dashboard\web
bun run dev

# 5. Open browser to http://localhost:3000
```

### Backup Before Risky Operations

Before making changes that could affect data:

```bash
# Create backup
scripts\backup-db.cmd

# Proceed with risky operation...

# If something goes wrong, restore from backup:
# docker exec -i agentbench-db psql -U postgres -d agentbench < backups\agentbench_YYYYMMDD_HHMMSS.sql
```

---

## Exit Codes

All scripts follow standard exit code conventions:

- **0**: Success - All checks passed
- **1**: Failure - One or more checks failed

This allows scripts to be used in automation:

```bash
# Example: Only run benchmark if health check passes
python scripts/check-health.py --skip-api && agentbench bench task-id --agent openai
```

---

## Dependencies

All scripts require:
- Python 3.11+
- `psycopg2` (PostgreSQL driver)
- `requests` (for check-health.py API checks)

Install dependencies:
```bash
pip install psycopg2-binary requests
```

Or use the project's virtual environment:
```bash
# Activate virtual environment
.venv\Scripts\activate

# Dependencies already installed via pyproject.toml
```

---

## Troubleshooting

### "Connection failed" errors

**Cause**: Database container not running or not accessible

**Solution**:
```bash
# Check if container is running
docker ps | findstr agentbench-db

# If not running, start it
docker compose up -d postgres

# Wait for healthy status
docker ps | findstr agentbench-db
# Should show "Up X minutes (healthy)"
```

### "Schema not initialized" errors

**Cause**: Database exists but tables not created

**Solution**:
```bash
# Apply schema manually
docker exec -i agentbench-db psql -U postgres -d agentbench < runner\db\schema.sql

# Verify tables created
python scripts/verify-db.py
```

### "API is not running" errors

**Cause**: API server not started

**Solution**:
```bash
# Start API server
cd dashboard/api
bun run dev

# Or skip API checks
python scripts/check-health.py --skip-api
```

### Import errors (psycopg2, requests)

**Cause**: Python dependencies not installed

**Solution**:
```bash
# Install dependencies
pip install psycopg2-binary requests

# Or use project environment
.venv\Scripts\activate
```

---

## Future Enhancements

Potential improvements for these scripts:

1. **JSON output mode** - For machine-readable results in CI/CD
2. **Slack/email notifications** - Alert on health check failures
3. **Historical tracking** - Track health metrics over time
4. **Auto-repair mode** - Automatically fix common issues
5. **Performance benchmarking** - Track query performance trends
6. **Data validation** - Verify data integrity and consistency

---

## See Also

- [Database Setup Guide](../docs/DATABASE-SETUP.md) - Complete setup instructions
- [Database Operations Guide](../docs/DATABASE-OPERATIONS.md) - Management tasks
- [Main README](../README.md) - Project overview
