# Migration Guide: File-Based to Database Storage

This guide covers migrating existing benchmark results from file-based storage to the PostgreSQL database, including data import procedures, validation, and rollback strategies.

## Overview

AgentBench originally stored benchmark results as JSON files in the `results/` directory. With database integration, results are now stored in PostgreSQL for better querying, analytics, and dashboard visualization.

This guide helps you:
- Understand the differences between storage methods
- Import existing file-based results into the database
- Validate the migration
- Handle edge cases and errors

## Storage Comparison

### File-Based Storage

**Location**: `results/<task-id>/<run-id>.json`

**Structure**:
```json
{
  "run_id": "abc-123-def-456",
  "task_id": "find-database-files",
  "agent": "openai-gpt-4",
  "started_at": "2024-01-15T10:30:00Z",
  "ended_at": "2024-01-15T10:35:45Z",
  "duration": 345.2,
  "success": true,
  "result": {
    "passed": true,
    "score": 0.95,
    "test_output": "All tests passed",
    "test_details": {}
  },
  "metrics": {
    "commands_executed": 12,
    "files_created": 2,
    "tokens_used": 1500,
    "cost": 0.045
  }
}
```

**Pros**:
- Simple to implement
- No dependencies
- Easy to inspect manually

**Cons**:
- Difficult to query across runs
- No aggregations or analytics
- Limited filtering capabilities
- No relationships between entities

### Database Storage

**Location**: PostgreSQL database with 9 tables

**Structure**:
- `tasks`: Task metadata
- `agents`: Agent configurations
- `runs`: Run records (references tasks and agents)
- `results`: Test results (references runs)
- `execution_metrics`: Performance metrics (references runs)
- `replays`: Execution traces (references runs)
- `multi_run_metrics`: Aggregated statistics
- `task_health`: Health classifications
- `task_difficulty_calibration`: Difficulty analysis

**Pros**:
- Fast queries and filtering
- Aggregations and analytics
- Referential integrity
- Efficient storage
- Powers dashboard visualizations

**Cons**:
- Requires PostgreSQL setup
- More complex infrastructure

## Prerequisites

Before migrating:

1. **Database is running**: Follow [DATABASE-SETUP.md](DATABASE-SETUP.md) to set up PostgreSQL
2. **Schema is initialized**: All tables exist in the database
3. **Backup existing files**: Copy `results/` directory to a safe location
4. **Python dependencies installed**: `pip install -e .`

## Migration Strategy

### Step 1: Analyze Existing Data

First, understand what file-based results you have:

```cmd
python scripts\analyze-file-results.py
```

**Expected Output**:
```
Analyzing file-based results in results/...

Found results:
  - 3 unique tasks
  - 5 unique agents
  - 127 total runs
  - Date range: 2024-01-10 to 2024-01-15

Tasks:
  - find-database-files: 45 runs
  - code-review-task: 52 runs
  - debug-python-error: 30 runs

Agents:
  - openai-gpt-4: 80 runs
  - openai-gpt-3.5-turbo: 35 runs
  - anthropic-claude-3: 12 runs

Ready to migrate: 127 runs
```

### Step 2: Create a Backup

Before migration, backup both the database and files:

```cmd
# Backup database
scripts\backup-db.cmd

# Backup file-based results
mkdir backups\file-results
xcopy results backups\file-results /E /I /H /Y
```

### Step 3: Run the Import Script

Use the provided import script to migrate all file-based results:

```cmd
python scripts\import-file-results.py
```

**What it does**:
1. Scans `results/` directory for JSON files
2. Extracts task and agent information
3. Inserts or updates tasks in `tasks` table
4. Inserts or updates agents in `agents` table
5. Inserts runs in `runs` table
6. Inserts results in `results` table
7. Inserts metrics in `execution_metrics` table
8. Validates foreign key relationships
9. Reports success/failure for each file

**Expected Output**:
```
AgentBench File-to-Database Import
====================================

Connecting to database...
✓ Connected to PostgreSQL at localhost:5432

Scanning results directory...
✓ Found 127 result files

Importing results...
[1/127] find-database-files/abc-123.json... ✓
[2/127] find-database-files/def-456.json... ✓
[3/127] code-review-task/ghi-789.json... ✓
...
[127/127] debug-python-error/xyz-999.json... ✓

====================================
Migration Complete!
====================================

Summary:
  - Successfully imported: 127 runs
  - Failed: 0 runs
  - New tasks created: 3
  - New agents created: 5

Database now contains:
  - 127 runs
  - 127 results
  - 127 execution metrics
```

### Step 4: Validate the Migration

Verify that data was imported correctly:

```cmd
python scripts\validate-migration.py
```

This script:
1. Counts runs in database vs. files
2. Verifies all run IDs are present
3. Checks data integrity (foreign keys, non-null values)
4. Compares sample records between files and database

**Expected Output**:
```
Validating Migration
====================

Checking counts...
✓ File-based runs: 127
✓ Database runs: 127
✓ Counts match!

Checking run IDs...
✓ All 127 run IDs found in database

Checking data integrity...
✓ All runs have valid task_id references
✓ All runs have valid agent_id references
✓ All runs have results records
✓ All runs have metrics records

Sampling 10 random records for comparison...
✓ [1/10] abc-123: Duration matches (345.2s)
✓ [2/10] def-456: Success status matches (true)
...
✓ [10/10] xyz-999: Score matches (0.87)

====================================
Migration Validation: PASSED
====================================
```

### Step 5: Test the Dashboard

Verify the dashboard can display the imported data:

```cmd
# Start API backend
cd dashboard\api
bun run src/index.ts

# In another terminal, start web frontend
cd dashboard\web
bun run dev
```

Open http://localhost:3000 and check:
- **Tasks page**: Shows imported tasks with run counts
- **Runs page**: Lists all imported runs
- **Leaderboard**: Shows agent rankings based on imported data

### Step 6: Archive or Remove Files

Once migration is validated, you can archive the file-based results:

**Option 1: Archive (Recommended)**
```cmd
mkdir archive
move results archive\results-%date:~-4,4%%date:~-10,2%%date:~-7,2%
```

**Option 2: Remove**
```cmd
# CAUTION: This permanently deletes files
rmdir /s /q results
```

Keep the backup created in Step 2 for safety.

## Import Script Details

### Script: `scripts/import-file-results.py`

```python
#!/usr/bin/env python3
"""
Import file-based benchmark results into PostgreSQL database.

This script scans the results/ directory for JSON files and imports them
into the database, creating task and agent records as needed.

Usage:
    python scripts/import-file-results.py [--dry-run] [--results-dir DIR]

Options:
    --dry-run       Preview import without making changes
    --results-dir   Directory containing result files (default: results/)
    --verbose       Show detailed output for each file
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

def load_env_config() -> Dict[str, Any]:
    """Load database configuration from environment variables."""
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'database': os.getenv('DB_NAME', 'agentbench'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
    }

def connect_db():
    """Connect to PostgreSQL database."""
    config = load_env_config()
    return psycopg2.connect(**config)

def import_task(conn, task_data: Dict[str, Any]) -> None:
    """Import or update task record."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO tasks (id, name, category, difficulty, version, timeout, docker_image)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            task_data.get('id', 'unknown'),
            task_data.get('name', task_data.get('id', 'Unknown Task')),
            task_data.get('category', 'general'),
            task_data.get('difficulty', 'medium'),
            task_data.get('version', '1.0.0'),
            task_data.get('timeout', 300),
            task_data.get('docker_image', 'ubuntu:22.04'),
        ))

def import_agent(conn, agent_str: str) -> int:
    """Import or retrieve agent record, return agent_id."""
    # Parse agent string (e.g., "openai-gpt-4")
    parts = agent_str.split('-', 1)
    agent_type = parts[0] if len(parts) > 0 else 'unknown'
    model = parts[1] if len(parts) > 1 else 'unknown'
    
    with conn.cursor() as cur:
        # Try to get existing agent
        cur.execute(
            "SELECT id FROM agents WHERE name = %s",
            (agent_str,)
        )
        row = cur.fetchone()
        
        if row:
            return row[0]
        
        # Insert new agent
        cur.execute("""
            INSERT INTO agents (name, type, model, config)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (agent_str, agent_type, model, '{}'))
        
        return cur.fetchone()[0]

def import_run(conn, result_file: Dict[str, Any], agent_id: int) -> None:
    """Import run, result, and metrics records."""
    with conn.cursor() as cur:
        # Check if run already exists
        cur.execute("SELECT id FROM runs WHERE id = %s", (result_file['run_id'],))
        if cur.fetchone():
            print(f"  ⚠ Run {result_file['run_id']} already exists, skipping")
            return
        
        # Insert run
        cur.execute("""
            INSERT INTO runs (id, task_id, agent_id, started_at, ended_at, duration, success)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            result_file['run_id'],
            result_file['task_id'],
            agent_id,
            result_file.get('started_at'),
            result_file.get('ended_at'),
            result_file.get('duration'),
            result_file.get('success'),
        ))
        
        # Insert result
        result_data = result_file.get('result', {})
        cur.execute("""
            INSERT INTO results (run_id, passed, score, test_output, test_details)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            result_file['run_id'],
            result_data.get('passed', False),
            result_data.get('score', 0.0),
            result_data.get('test_output', ''),
            json.dumps(result_data.get('test_details', {})),
        ))
        
        # Insert metrics if available
        metrics = result_file.get('metrics', {})
        if metrics:
            cur.execute("""
                INSERT INTO execution_metrics (
                    run_id, commands_executed, files_created, files_modified,
                    tokens_used, cost
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                result_file['run_id'],
                metrics.get('commands_executed', 0),
                metrics.get('files_created', 0),
                metrics.get('files_modified', 0),
                metrics.get('tokens_used', 0),
                metrics.get('cost', 0.0),
            ))

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Import file-based results to database')
    parser.add_argument('--dry-run', action='store_true', help='Preview without importing')
    parser.add_argument('--results-dir', default='results', help='Results directory')
    parser.add_argument('--verbose', action='store_true', help='Detailed output')
    args = parser.parse_args()
    
    print("AgentBench File-to-Database Import")
    print("=" * 50)
    print()
    
    # Connect to database
    print("Connecting to database...")
    try:
        conn = connect_db()
        print("✓ Connected to PostgreSQL")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return 1
    
    # Scan results directory
    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"✗ Results directory not found: {results_dir}")
        return 1
    
    print(f"Scanning {results_dir}...")
    result_files = list(results_dir.rglob('*.json'))
    print(f"✓ Found {len(result_files)} result files")
    print()
    
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        print()
    
    # Import each file
    print("Importing results...")
    success_count = 0
    error_count = 0
    
    for i, file_path in enumerate(result_files, 1):
        try:
            with open(file_path, 'r') as f:
                result_data = json.load(f)
            
            if args.verbose or i % 10 == 0:
                print(f"[{i}/{len(result_files)}] {file_path.relative_to(results_dir)}...", end=' ')
            
            if not args.dry_run:
                # Import task
                import_task(conn, {'id': result_data['task_id']})
                
                # Import agent
                agent_id = import_agent(conn, result_data['agent'])
                
                # Import run, result, metrics
                import_run(conn, result_data, agent_id)
                
                conn.commit()
            
            if args.verbose or i % 10 == 0:
                print("✓")
            success_count += 1
            
        except Exception as e:
            if args.verbose or i % 10 == 0:
                print(f"✗ {e}")
            error_count += 1
            if not args.dry_run:
                conn.rollback()
    
    # Summary
    print()
    print("=" * 50)
    print("Migration Complete!" if not args.dry_run else "Dry Run Complete!")
    print("=" * 50)
    print()
    print(f"Successfully processed: {success_count} runs")
    if error_count > 0:
        print(f"Errors: {error_count} runs")
    
    if not args.dry_run:
        # Show database counts
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM runs")
            run_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM tasks")
            task_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM agents")
            agent_count = cur.fetchone()[0]
            
        print()
        print("Database now contains:")
        print(f"  - {run_count} runs")
        print(f"  - {task_count} tasks")
        print(f"  - {agent_count} agents")
    
    conn.close()
    return 0 if error_count == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
```

## Handling Edge Cases

### Duplicate Run IDs

If a run ID already exists in the database, the import script skips it:

```
⚠ Run abc-123-def-456 already exists, skipping
```

**Solution**: This is normal and safe. The script won't overwrite existing data.

### Missing Task or Agent Metadata

If file-based results lack full task/agent details:

```python
# Import creates minimal records
task: id='find-database-files', name='find-database-files', category='general'
agent: name='openai-gpt-4', type='openai', model='gpt-4'
```

**Solution**: Update task metadata manually in the database after import, or rerun benchmarks to create complete records.

### Invalid JSON Files

If a JSON file is corrupted:

```
✗ [45/127] task-xyz/corrupted.json: JSONDecodeError: Expecting value
```

**Solution**: Fix or remove the corrupted file, then rerun the import script.

### Missing Fields

If a JSON file lacks required fields (e.g., `success` is missing):

**Solution**: The import script uses safe defaults:
- `success`: `None` (NULL in database)
- `duration`: `None`
- `score`: `0.0`
- `metrics`: Empty record

## Rollback Procedure

If migration fails or produces incorrect results:

### Option 1: Restore from Backup

```cmd
# Stop API and dashboard
# Clear database
scripts\reset-db.cmd

# Restore from backup
docker exec -i agentbench-db psql -U postgres -d agentbench < backups\agentbench_backup.sql
```

### Option 2: Delete Imported Runs

Delete all runs imported after a specific time:

```sql
DELETE FROM runs WHERE started_at > '2024-01-15 00:00:00';
```

This cascades to `results` and `execution_metrics` tables.

### Option 3: Complete Reset

Start fresh:

```cmd
# Full database reset
docker compose down -v
docker compose up -d postgres

# Restore files from backup
xcopy backups\file-results results /E /I /H /Y
```

## Post-Migration

After successful migration:

1. **Update documentation**: Note the migration date in project docs
2. **Update runner config**: Ensure `.env` file has database connection details
3. **Test new benchmarks**: Run a new benchmark to verify end-to-end workflow
4. **Monitor performance**: Check that queries are fast and database is healthy
5. **Set up backups**: Schedule automated database backups

## Hybrid Mode (Advanced)

You can run both file and database storage simultaneously:

```python
# In runner/cli.py
storage = Storage(db_host="localhost", fallback_to_files=True)
```

This stores to database first, then falls back to files if database is unavailable.

**Use cases**:
- Testing database integration while keeping file backup
- Gradual migration with safety net
- Development environments

## FAQ

**Q: Can I migrate data from multiple projects?**

A: Yes, but ensure task IDs don't collide. Consider prefixing task IDs (e.g., `project1-task-id`).

**Q: What happens to replay traces?**

A: The current import script doesn't import replays. If your file-based results include replay data, modify the script to insert into the `replays` table.

**Q: Can I revert to file-based storage after migration?**

A: Yes. Set `fallback_to_files=True` in the Storage class, or stop the database container to automatically use file storage.

**Q: Will migration affect running benchmarks?**

A: No, the migration is read-only on the file system. However, stop any active benchmarks before migration to avoid race conditions.

**Q: How long does migration take?**

A: Approximately 1-2 seconds per file. 1000 files = 15-30 minutes.

## Troubleshooting

### Import Script Fails with Connection Error

**Solution**: Ensure database is running and environment variables are set:
```cmd
docker ps | findstr agentbench-db
python scripts\test-connection.py
```

### Foreign Key Violation

**Error**: `ForeignKeyViolation: insert or update on table "runs" violates foreign key constraint`

**Solution**: Ensure tasks and agents are created before runs. The import script handles this automatically.

### Validation Fails (Count Mismatch)

**Solution**:
1. Check for hidden/duplicate JSON files
2. Check database for existing runs from previous imports
3. Use `--verbose` flag to see which files failed

### Out of Memory During Import

**Solution**: Process files in batches:
```cmd
python scripts\import-file-results.py --results-dir results\batch1
python scripts\import-file-results.py --results-dir results\batch2
```

## Additional Resources

- [DATABASE-SETUP.md](DATABASE-SETUP.md) - Database setup guide
- [DATABASE-OPERATIONS.md](DATABASE-OPERATIONS.md) - Database operations
- [PostgreSQL COPY Documentation](https://www.postgresql.org/docs/16/sql-copy.html) - Bulk import reference
