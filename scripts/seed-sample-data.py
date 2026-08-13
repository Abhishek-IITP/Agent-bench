#!/usr/bin/env python3
"""
Seed the AgentBench database with sample data for testing.

This script creates realistic sample data including:
- Multiple tasks
- Multiple agents
- Benchmark runs with results
- Execution metrics
- Multi-run aggregated metrics

Usage:
    python scripts/seed-sample-data.py [--runs N] [--clean]

Options:
    --runs N    Number of sample runs to create per task/agent combo (default: 5)
    --clean     Clear existing data before seeding
    --verbose   Show detailed output
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from uuid import uuid4
from random import random, randint
from typing import List, Tuple
import psycopg2


def load_env_config():
    """Load database configuration from environment variables."""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "database": os.getenv("DB_NAME", "agentbench"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "postgres"),
    }


def connect_db():
    """Connect to PostgreSQL database."""
    config = load_env_config()
    return psycopg2.connect(**config)


def clean_database(conn):
    """Remove all existing data."""
    print("Cleaning existing data...")
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE execution_metrics CASCADE")
        cur.execute("TRUNCATE TABLE replays CASCADE")
        cur.execute("TRUNCATE TABLE results CASCADE")
        cur.execute("TRUNCATE TABLE runs CASCADE")
        cur.execute("TRUNCATE TABLE multi_run_metrics CASCADE")
        cur.execute("TRUNCATE TABLE task_health CASCADE")
        cur.execute("TRUNCATE TABLE task_difficulty_calibration CASCADE")
        cur.execute("TRUNCATE TABLE agents CASCADE")
        cur.execute("TRUNCATE TABLE tasks CASCADE")
    conn.commit()
    print("✓ Database cleaned")


def seed_tasks(conn) -> List[str]:
    """Create sample tasks."""
    tasks = [
        {
            "id": "find-database-files",
            "name": "Find Database Files",
            "category": "filesystem",
            "difficulty": "easy",
            "version": "1.0.0",
            "timeout": 300,
            "docker_image": "ubuntu:22.04",
            "description": "Find files containing specific database-related keywords",
        },
        {
            "id": "code-review-task",
            "name": "Code Review Assistant",
            "category": "coding",
            "difficulty": "medium",
            "version": "1.0.0",
            "timeout": 600,
            "docker_image": "python:3.11",
            "description": "Review Python code and identify issues",
        },
        {
            "id": "debug-python-error",
            "name": "Debug Python Error",
            "category": "debugging",
            "difficulty": "medium",
            "version": "1.0.0",
            "timeout": 450,
            "docker_image": "python:3.11",
            "description": "Find and fix a bug in Python code",
        },
        {
            "id": "json-data-transform",
            "name": "JSON Data Transformation",
            "category": "data-processing",
            "difficulty": "easy",
            "version": "1.0.0",
            "timeout": 300,
            "docker_image": "node:20",
            "description": "Transform JSON data according to specification",
        },
        {
            "id": "api-integration-test",
            "name": "API Integration Test",
            "category": "testing",
            "difficulty": "hard",
            "version": "1.0.0",
            "timeout": 900,
            "docker_image": "python:3.11",
            "description": "Write comprehensive tests for REST API",
        },
    ]

    print("Creating sample tasks...")
    with conn.cursor() as cur:
        for task in tasks:
            cur.execute(
                """
                INSERT INTO tasks (id, name, category, difficulty, version, timeout, docker_image, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """,
                (
                    task["id"],
                    task["name"],
                    task["category"],
                    task["difficulty"],
                    task["version"],
                    task["timeout"],
                    task["docker_image"],
                    task["description"],
                ),
            )
    conn.commit()
    print(f"✓ Created {len(tasks)} tasks")

    return [t["id"] for t in tasks]


def seed_agents(conn) -> List[Tuple[int, str]]:
    """Create sample agents."""
    agents = [
        {
            "name": "openai-gpt-4",
            "type": "openai",
            "model": "gpt-4",
            "config": {"temperature": 0.7},
        },
        {
            "name": "openai-gpt-3.5-turbo",
            "type": "openai",
            "model": "gpt-3.5-turbo",
            "config": {"temperature": 0.7},
        },
        {
            "name": "anthropic-claude-3-opus",
            "type": "anthropic",
            "model": "claude-3-opus",
            "config": {},
        },
        {
            "name": "anthropic-claude-3-sonnet",
            "type": "anthropic",
            "model": "claude-3-sonnet",
            "config": {},
        },
    ]

    print("Creating sample agents...")
    agent_ids = []

    with conn.cursor() as cur:
        for agent in agents:
            cur.execute(
                """
                INSERT INTO agents (name, type, model, config)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name) DO UPDATE SET
                    type = EXCLUDED.type,
                    model = EXCLUDED.model,
                    config = EXCLUDED.config
                RETURNING id
            """,
                (agent["name"], agent["type"], agent["model"], json.dumps(agent["config"])),
            )

            agent_id = cur.fetchone()[0]
            agent_ids.append((agent_id, agent["name"]))

    conn.commit()
    print(f"✓ Created {len(agents)} agents")

    return agent_ids


def seed_runs(
    conn, task_ids: List[str], agent_data: List[Tuple[int, str]], runs_per_combo: int, verbose: bool
):
    """Create sample runs with results and metrics."""
    print(f"Creating sample runs ({runs_per_combo} per task/agent combo)...")

    total_runs = len(task_ids) * len(agent_data) * runs_per_combo
    run_count = 0

    base_time = datetime.now() - timedelta(days=30)

    for task_id in task_ids:
        for agent_id, agent_name in agent_data:
            # Generate characteristic success rate for this task/agent combo
            # Some combos are better than others
            base_success_rate = random() * 0.5 + 0.5  # 0.5 to 1.0

            for i in range(runs_per_combo):
                run_count += 1

                # Generate run data
                run_id = str(uuid4())
                started_at = base_time + timedelta(hours=run_count * 2, minutes=randint(0, 59))

                # Success varies around the base rate
                success = random() < (base_success_rate + (random() - 0.5) * 0.2)
                score = (random() * 0.3 + 0.7) if success else (random() * 0.4)
                duration = randint(30, 600) if success else randint(10, 300)

                ended_at = started_at + timedelta(seconds=duration)

                # Insert run
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO runs (id, task_id, agent_id, started_at, ended_at, duration, success)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                        (run_id, task_id, agent_id, started_at, ended_at, duration, success),
                    )

                    # Insert result
                    test_output = (
                        "All tests passed"
                        if success
                        else f"Test failed: assertion error in test_{randint(1,5)}"
                    )
                    test_details = {
                        "tests_run": randint(5, 20),
                        "tests_passed": randint(5, 20) if success else randint(0, 5),
                        "coverage": (
                            round(random() * 30 + 70, 1) if success else round(random() * 40, 1)
                        ),
                    }

                    cur.execute(
                        """
                        INSERT INTO results (run_id, passed, score, test_output, test_details)
                        VALUES (%s, %s, %s, %s, %s)
                    """,
                        (run_id, success, score, test_output, json.dumps(test_details)),
                    )

                    # Insert execution metrics
                    cur.execute(
                        """
                        INSERT INTO execution_metrics (
                            run_id, commands_executed, files_created, files_modified,
                            tokens_used, cost
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                        (
                            run_id,
                            randint(5, 50),
                            randint(0, 10),
                            randint(0, 15),
                            randint(500, 5000),
                            round(random() * 0.5, 3),
                        ),
                    )

                if verbose and run_count % 10 == 0:
                    print(f"  [{run_count}/{total_runs}] Created run for {task_id} + {agent_name}")

    conn.commit()
    print(f"✓ Created {total_runs} runs with results and metrics")


def seed_multi_run_metrics(conn, task_ids: List[str], agent_data: List[Tuple[int, str]]):
    """Create aggregated multi-run metrics."""
    print("Computing multi-run metrics...")

    with conn.cursor() as cur:
        for task_id in task_ids:
            for agent_id, agent_name in agent_data:
                # Compute metrics from runs
                cur.execute(
                    """
                    SELECT
                        COUNT(*) as n_runs,
                        AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate,
                        AVG(duration) as mean_runtime,
                        VARIANCE(CASE WHEN success THEN 1.0 ELSE 0.0 END) as variance
                    FROM runs
                    WHERE task_id = %s AND agent_id = %s
                """,
                    (task_id, agent_id),
                )

                metrics = cur.fetchone()

                if metrics and metrics[0] > 0:
                    n_runs, success_rate, mean_runtime, variance = metrics

                    # Compute confidence interval (simplified)
                    ci_margin = 1.96 * (variance**0.5) / (n_runs**0.5) if variance else 0
                    ci_lower = max(0, success_rate - ci_margin)
                    ci_upper = min(1, success_rate + ci_margin)

                    # Reliability score (higher is better)
                    reliability_score = success_rate * (1 - variance) if variance else success_rate

                    cur.execute(
                        """
                        INSERT INTO multi_run_metrics (
                            task_id, agent_name, n_runs, success_rate,
                            confidence_interval_lower, confidence_interval_upper,
                            variance, mean_runtime, reliability_score
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (task_id, agent_name) DO UPDATE SET
                            n_runs = EXCLUDED.n_runs,
                            success_rate = EXCLUDED.success_rate,
                            confidence_interval_lower = EXCLUDED.confidence_interval_lower,
                            confidence_interval_upper = EXCLUDED.confidence_interval_upper,
                            variance = EXCLUDED.variance,
                            mean_runtime = EXCLUDED.mean_runtime,
                            reliability_score = EXCLUDED.reliability_score
                    """,
                        (
                            task_id,
                            agent_name,
                            n_runs,
                            success_rate,
                            ci_lower,
                            ci_upper,
                            variance,
                            mean_runtime,
                            reliability_score,
                        ),
                    )

    conn.commit()
    print("✓ Created multi-run metrics")


def seed_task_health(conn, task_ids: List[str]):
    """Create task health classifications."""
    print("Computing task health...")

    with conn.cursor() as cur:
        for task_id in task_ids:
            # Compute health metrics from runs
            cur.execute(
                """
                SELECT
                    AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate,
                    VARIANCE(CASE WHEN success THEN 1.0 ELSE 0.0 END) as variance,
                    COUNT(DISTINCT agent_id) as n_agents
                FROM runs
                WHERE task_id = %s
            """,
                (task_id,),
            )

            metrics = cur.fetchone()

            if metrics:
                success_rate, variance, n_agents = metrics

                # Classify health status
                if success_rate >= 0.95:
                    health_status = "healthy"
                    recommendations = "Task is performing well across agents"
                elif success_rate >= 0.8 and variance < 0.05:
                    health_status = "healthy"
                    recommendations = "Task is stable with good success rate"
                elif variance > 0.15:
                    health_status = "flaky"
                    recommendations = "Task shows high variance; review test stability"
                elif success_rate < 0.3:
                    health_status = "broken"
                    recommendations = "Task has low success rate; review task specification"
                elif success_rate > 0.99 and n_agents >= 3:
                    health_status = "trivial"
                    recommendations = "Task may be too easy; consider increasing difficulty"
                else:
                    health_status = "healthy"
                    recommendations = "Task is within acceptable parameters"

                cur.execute(
                    """
                    INSERT INTO task_health (task_id, health_status, success_rate, variance, n_agents, recommendations)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (task_id) DO UPDATE SET
                        health_status = EXCLUDED.health_status,
                        success_rate = EXCLUDED.success_rate,
                        variance = EXCLUDED.variance,
                        n_agents = EXCLUDED.n_agents,
                        recommendations = EXCLUDED.recommendations
                """,
                    (
                        task_id,
                        health_status,
                        success_rate,
                        variance or 0,
                        n_agents,
                        recommendations,
                    ),
                )

    conn.commit()
    print("✓ Created task health classifications")


def show_summary(conn):
    """Display database summary."""
    print("\n" + "=" * 60)
    print("Database Summary")
    print("=" * 60)

    with conn.cursor() as cur:
        # Count records
        cur.execute("SELECT COUNT(*) FROM tasks")
        task_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM agents")
        agent_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM runs")
        run_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM results")
        result_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM execution_metrics")
        metrics_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM multi_run_metrics")
        multi_run_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM task_health")
        health_count = cur.fetchone()[0]

        print("\nRecords created:")
        print(f"  Tasks: {task_count}")
        print(f"  Agents: {agent_count}")
        print(f"  Runs: {run_count}")
        print(f"  Results: {result_count}")
        print(f"  Execution Metrics: {metrics_count}")
        print(f"  Multi-run Metrics: {multi_run_count}")
        print(f"  Task Health: {health_count}")

        # Show sample data
        print("\nSample leaderboard:")
        cur.execute("""
            SELECT
                a.name,
                COUNT(DISTINCT r.task_id) as tasks_solved,
                AVG(CASE WHEN r.success THEN 1.0 ELSE 0.0 END) as success_rate,
                AVG(r.duration) as avg_duration
            FROM agents a
            LEFT JOIN runs r ON a.id = r.agent_id
            GROUP BY a.id, a.name
            ORDER BY success_rate DESC
            LIMIT 5
        """)

        print(f"  {'Agent':<30} {'Tasks':<8} {'Success Rate':<15} {'Avg Duration':<15}")
        print("  " + "-" * 70)
        for row in cur.fetchall():
            agent, tasks, success, duration = row
            print(f"  {agent:<30} {tasks:<8} {success*100:>6.1f}%         {duration:>6.1f}s")

        print("\nTask health summary:")
        cur.execute("""
            SELECT health_status, COUNT(*) as count
            FROM task_health
            GROUP BY health_status
            ORDER BY count DESC
        """)

        for row in cur.fetchall():
            status, count = row
            print(f"  {status}: {count} tasks")

    print("\n" + "=" * 60)
    print("✓ Sample data seeding complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  - View data: docker exec -it agentbench-db psql -U postgres -d agentbench")
    print("  - Start API: cd dashboard/api && bun run src/index.ts")
    print("  - Start web: cd dashboard/web && bun run dev")
    print("  - Open dashboard: http://localhost:3000")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Seed AgentBench database with sample data for testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--runs", type=int, default=5, help="Runs per task/agent combo (default: 5)"
    )
    parser.add_argument("--clean", action="store_true", help="Clear existing data first")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    args = parser.parse_args()

    print("=" * 60)
    print("AgentBench Sample Data Seeder")
    print("=" * 60)
    print()

    # Connect to database
    print("Connecting to database...")
    try:
        conn = connect_db()
        print(f"✓ Connected to PostgreSQL at {conn.get_dsn_parameters()['host']}")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("  - Ensure database is running: docker ps | findstr agentbench-db")
        print("  - Check environment variables in .env file")
        print("  - Test connection: python scripts/test-connection.py")
        return 1

    print()

    try:
        # Clean if requested
        if args.clean:
            clean_database(conn)
            print()

        # Seed data
        task_ids = seed_tasks(conn)
        agent_data = seed_agents(conn)
        seed_runs(conn, task_ids, agent_data, args.runs, args.verbose)
        seed_multi_run_metrics(conn, task_ids, agent_data)
        seed_task_health(conn, task_ids)

        # Show summary
        show_summary(conn)

    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        import traceback

        traceback.print_exc()
        conn.rollback()
        return 1

    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
