"""
Verify all database tables have data after E2E testing.
"""

import os
import sys

os.chdir(r'E:\Abhishek-IITP\ABHILIB\agent-bench')
sys.path.insert(0, r'E:\Abhishek-IITP\ABHILIB\agent-bench')

from runner.storage import Storage

def main():
    print("\n" + "="*70)
    print("DATABASE TABLE VERIFICATION")
    print("="*70)
    
    storage = Storage(
        db_host=os.getenv("DB_HOST", "127.0.0.1"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_name=os.getenv("DB_NAME", "agentbench"),
        db_user=os.getenv("DB_USER", "postgres"),
        db_password=os.getenv("DB_PASSWORD", "postgres"),
    )
    
    if not storage.db_connected:
        print("✗ Database not connected")
        return
    
    print("✓ Connected to database\n")
    
    # List all tables
    tables = [
        "tasks",
        "agents",
        "runs",
        "results",
        "replays",
        "execution_metrics",
        "multi_run_metrics",
        "task_health",
        "task_difficulty_calibration"
    ]
    
    for table in tables:
        try:
            result = storage.db.execute(f"SELECT COUNT(*) FROM {table}", fetch=True)
            count = result[0][0] if result else 0
            print(f"  {table:30} {count:5} rows")
        except Exception as e:
            print(f"  {table:30} ERROR: {e}")
    
    print("\n" + "="*70)
    print("DETAILED TASK DATA")
    print("="*70)
    
    # Show task details
    result = storage.db.execute(
        """SELECT id, name, category, difficulty, version 
           FROM tasks 
           WHERE id = 'find-database-files'""",
        fetch=True
    )
    if result:
        print("\nTask: find-database-files")
        row = result[0]
        print(f"  Name:       {row[1]}")
        print(f"  Category:   {row[2]}")
        print(f"  Difficulty: {row[3]}")
        print(f"  Version:    {row[4]}")
    
    print("\n" + "="*70)
    print("DETAILED AGENT DATA")
    print("="*70)
    
    # Show agent details
    result = storage.db.execute(
        "SELECT id, name, type, model FROM agents",
        fetch=True
    )
    if result:
        for row in result:
            print(f"\nAgent ID: {row[0]}")
            print(f"  Name:  {row[1]}")
            print(f"  Type:  {row[2]}")
            print(f"  Model: {row[3]}")
    
    print("\n" + "="*70)
    print("DETAILED RUN DATA")
    print("="*70)
    
    # Show run details
    result = storage.db.execute(
        """SELECT r.id, r.task_id, r.success, r.duration, a.name
           FROM runs r
           JOIN agents a ON r.agent_id = a.id
           WHERE r.task_id = 'find-database-files'
           ORDER BY r.started_at DESC
           LIMIT 5""",
        fetch=True
    )
    if result:
        print(f"\nLast 5 runs for 'find-database-files':")
        for row in result:
            success_str = "✓ PASS" if row[2] else "✗ FAIL"
            print(f"  {row[0][:8]}... | {row[4]:15} | {success_str} | {row[3]:.1f}s")
    
    print("\n" + "="*70)
    print("DETAILED RESULTS DATA")
    print("="*70)
    
    # Show result details
    result = storage.db.execute(
        """SELECT res.run_id, res.passed, res.score, LEFT(res.test_output, 50)
           FROM results res
           JOIN runs r ON res.run_id = r.id
           WHERE r.task_id = 'find-database-files'
           ORDER BY res.id DESC
           LIMIT 5""",
        fetch=True
    )
    if result:
        print(f"\nLast 5 results:")
        for row in result:
            passed_str = "✓" if row[1] else "✗"
            print(f"  {passed_str} | Score: {row[2]:.1f} | {row[3]}")
    
    print("\n" + "="*70)
    print("DETAILED EXECUTION METRICS")
    print("="*70)
    
    # Show metrics details
    result = storage.db.execute(
        """SELECT em.commands_executed, em.files_created, em.files_modified,
                  em.tokens_used, em.cost
           FROM execution_metrics em
           JOIN runs r ON em.run_id = r.id
           WHERE r.task_id = 'find-database-files'
           LIMIT 5""",
        fetch=True
    )
    if result:
        print(f"\nExecution metrics (sample):")
        print(f"  Commands | Files Created | Files Modified | Tokens | Cost")
        for row in result:
            print(f"  {row[0]:8} | {row[1]:13} | {row[2]:14} | {row[3]:6} | ${row[4]:.4f}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
