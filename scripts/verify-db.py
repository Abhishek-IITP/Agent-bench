#!/usr/bin/env python3
"""
Database verification script.
Verifies database schema, tables, indexes, and foreign key constraints.
"""

import psycopg2
import sys
import os
from typing import List, Tuple

# Expected tables based on schema.sql
EXPECTED_TABLES = [
    "tasks",
    "agents",
    "runs",
    "results",
    "replays",
    "execution_metrics",
    "multi_run_metrics",
    "task_health",
    "task_difficulty_calibration",
]

# Expected indexes
EXPECTED_INDEXES = [
    "idx_runs_task_id",
    "idx_runs_agent_id",
    "idx_runs_created",
    "idx_results_run_id",
    "idx_replays_run_id",
    "idx_metrics_run_id",
    "idx_multi_run_metrics_task",
    "idx_multi_run_metrics_agent",
    "idx_task_health_status",
    "idx_task_difficulty_match",
]


def get_connection():
    """Get database connection using environment variables."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "agentbench"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )


def verify_connection(conn) -> bool:
    """Verify database connection and version."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✓ PostgreSQL version: {version.split(',')[0]}")
        cursor.close()
        return True
    except Exception as e:
        print(f"❌ Connection verification failed: {e}")
        return False


def verify_tables(conn) -> Tuple[bool, List[str]]:
    """Verify all expected tables exist."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)

    actual_tables = [row[0] for row in cursor.fetchall()]
    cursor.close()

    missing_tables = [t for t in EXPECTED_TABLES if t not in actual_tables]
    extra_tables = [t for t in actual_tables if t not in EXPECTED_TABLES]

    print("\n📊 Table Verification:")
    print(f"  Expected: {len(EXPECTED_TABLES)} tables")
    print(f"  Found: {len(actual_tables)} tables")

    if missing_tables:
        print(f"  ❌ Missing tables: {', '.join(missing_tables)}")
        return False, missing_tables

    if extra_tables:
        print(f"  ⚠️  Extra tables (unexpected): {', '.join(extra_tables)}")

    print("  ✓ All expected tables exist:")
    for table in EXPECTED_TABLES:
        print(f"    - {table}")

    return True, []


def verify_indexes(conn) -> bool:
    """Verify all expected indexes exist."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT indexname
        FROM pg_indexes
        WHERE schemaname = 'public'
        ORDER BY indexname
    """)

    actual_indexes = [row[0] for row in cursor.fetchall()]
    cursor.close()

    missing_indexes = [idx for idx in EXPECTED_INDEXES if idx not in actual_indexes]

    print("\n🔍 Index Verification:")
    print(f"  Expected: {len(EXPECTED_INDEXES)} indexes")
    print(
        f"  Found: {len([idx for idx in actual_indexes if idx in EXPECTED_INDEXES])} expected indexes"
    )

    if missing_indexes:
        print(f"  ❌ Missing indexes: {', '.join(missing_indexes)}")
        return False

    print("  ✓ All expected indexes exist")

    return True


def verify_foreign_keys(conn) -> bool:
    """Verify foreign key constraints exist."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
          AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema = 'public'
        ORDER BY tc.table_name
    """)

    foreign_keys = cursor.fetchall()
    cursor.close()

    print("\n🔗 Foreign Key Constraints:")
    print(f"  Found: {len(foreign_keys)} constraints")

    if not foreign_keys:
        print("  ❌ No foreign key constraints found")
        return False

    print("  ✓ Foreign key constraints verified:")
    for fk in foreign_keys:
        table, column, ref_table, ref_column = fk
        print(f"    - {table}.{column} → {ref_table}.{ref_column}")

    return True


def get_table_counts(conn) -> None:
    """Display record counts for all tables."""
    cursor = conn.cursor()

    print("\n📈 Table Record Counts:")
    for table in EXPECTED_TABLES:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table:30} {count:>6} records")
        except Exception as e:
            print(f"  {table:30} ERROR: {e}")

    cursor.close()


def main():
    """Main verification routine."""
    print("=" * 70)
    print("AgentBench Database Verification")
    print("=" * 70)

    # Get connection details
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "agentbench")
    db_user = os.getenv("DB_USER", "postgres")

    print("\n🔌 Connection Details:")
    print(f"  Host: {db_host}")
    print(f"  Port: {db_port}")
    print(f"  Database: {db_name}")
    print(f"  User: {db_user}")
    print()

    # Connect to database
    try:
        conn = get_connection()
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure Docker container is running: docker ps")
        print("  2. Start database if not running: docker compose up -d postgres")
        print("  3. Check environment variables in .env file")
        sys.exit(1)

    # Run verification checks
    all_passed = True

    if not verify_connection(conn):
        all_passed = False

    tables_ok, missing = verify_tables(conn)
    if not tables_ok:
        all_passed = False
        print("\n⚠️  To initialize schema, run:")
        print(
            "  docker exec -i agentbench-db psql -U postgres -d agentbench < runner\\db\\schema.sql"
        )

    if not verify_indexes(conn):
        all_passed = False

    if not verify_foreign_keys(conn):
        all_passed = False

    # Display table counts
    get_table_counts(conn)

    conn.close()

    # Final result
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ Database verification PASSED - All checks successful!")
        print("=" * 70)
        sys.exit(0)
    else:
        print("❌ Database verification FAILED - See errors above")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
