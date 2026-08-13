#!/usr/bin/env python3
"""Insert test data into the database for E2E validation."""

import psycopg2
import uuid
from datetime import datetime, timedelta
import random

# Connect to database
conn = psycopg2.connect(
    host="127.0.0.1", port=5432, database="agentbench", user="postgres", password="postgres"
)

cursor = conn.cursor()

print("Inserting test data...")

# 1. Insert test tasks
tasks = [
    ("find-database-files", "Find Database Files", "filesystem", "easy", 60),
    ("extract-emails", "Extract Emails", "parsing", "easy", 90),
    ("merge-csv-files", "Merge CSV Files", "data", "medium", 120),
]

for task_id, name, category, difficulty, timeout in tasks:
    cursor.execute(
        """
        INSERT INTO tasks (id, name, category, difficulty, timeout, version, description)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """,
        (task_id, name, category, difficulty, timeout, "1.0.0", f"Test task: {name}"),
    )

print(f"✓ Inserted {len(tasks)} tasks")

# 2. Insert test agents
agents = [
    ("gpt-4-agent", "gpt-4", "openai", "gpt-4", '{"temperature": 0.7}'),
    ("claude-agent", "claude-3", "anthropic", "claude-3-sonnet", '{"temperature": 0.5}'),
    ("mock-agent", "mock", "mock", "mock-1.0", "{}"),
]

agent_ids = {}
for agent_name, agent_type, provider, model, config in agents:
    cursor.execute(
        """
        INSERT INTO agents (name, type, model, config)
        VALUES (%s, %s, %s, %s::jsonb)
        ON CONFLICT (name) DO UPDATE SET model = EXCLUDED.model
        RETURNING id
    """,
        (agent_name, provider, model, config),
    )
    agent_id = cursor.fetchone()[0]
    agent_ids[agent_name] = agent_id

print(f"✓ Inserted {len(agents)} agents")

# 3. Insert test runs with results
base_time = datetime.now() - timedelta(hours=2)
run_count = 0

for task_id, task_name, _, _, _ in tasks:
    for agent_name in agent_ids.keys():
        # Create 3-5 runs per task-agent combination
        num_runs = random.randint(3, 5)

        for i in range(num_runs):
            run_id = str(uuid.uuid4())
            agent_id = agent_ids[agent_name]

            # Random success/failure
            success = random.random() > 0.3  # 70% success rate
            duration = random.uniform(15.0, 90.0)
            score = random.uniform(0.7, 1.0) if success else random.uniform(0.0, 0.5)

            started_at = base_time + timedelta(minutes=run_count * 5)
            ended_at = started_at + timedelta(seconds=duration)

            # Insert run
            cursor.execute(
                """
                INSERT INTO runs (id, task_id, agent_id, started_at, ended_at, duration, success)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (run_id, task_id, agent_id, started_at, ended_at, duration, success),
            )

            # Insert result
            cursor.execute(
                """
                INSERT INTO results (run_id, passed, score, test_output, test_details)
                VALUES (%s, %s, %s, %s, %s::jsonb)
            """,
                (
                    run_id,
                    success,
                    score,
                    f"Test output for {task_name}" if success else f"Failed: {task_name}",
                    (
                        '{"tests_passed": 5, "tests_failed": 1}'
                        if success
                        else '{"tests_passed": 2, "tests_failed": 4}'
                    ),
                ),
            )

            # Insert execution metrics
            cursor.execute(
                """
                INSERT INTO execution_metrics (
                    run_id, commands_executed, files_created, files_modified,
                    tokens_used, cost
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (
                    run_id,
                    random.randint(10, 50),
                    random.randint(1, 5),
                    random.randint(2, 10),
                    random.randint(500, 3000),
                    random.uniform(0.01, 0.15),
                ),
            )

            # Insert replay data
            cursor.execute(
                """
                INSERT INTO replays (run_id, data)
                VALUES (%s, %s::jsonb)
            """,
                (
                    run_id,
                    '{"steps": [{"action": "read_file", "timestamp": "2024-01-01T10:00:00Z"}]}',
                ),
            )

            run_count += 1

print(f"✓ Inserted {run_count} runs with results, metrics, and replays")

# 4. Insert multi-run metrics
for task_id, _, _, _, _ in tasks:
    for agent_name, agent_id in agent_ids.items():
        # Calculate aggregate metrics
        cursor.execute(
            """
            SELECT
                COUNT(*) as n_runs,
                AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate,
                AVG(duration) as mean_runtime,
                STDDEV(CASE WHEN success THEN 1.0 ELSE 0.0 END) as variance
            FROM runs
            WHERE task_id = %s AND agent_id = %s
        """,
            (task_id, agent_id),
        )

        result = cursor.fetchone()
        if result and result[0] > 0:
            n_runs, success_rate, mean_runtime, variance = result
            success_rate = float(success_rate) if success_rate else 0.0
            mean_runtime = float(mean_runtime) if mean_runtime else 0.0
            variance = float(variance) if variance else 0.0
            reliability_score = success_rate * 100

            cursor.execute(
                """
                INSERT INTO multi_run_metrics (
                    task_id, agent_name, n_runs, success_rate,
                    confidence_interval_lower, confidence_interval_upper,
                    variance, mean_runtime, reliability_score
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (task_id, agent_name)
                DO UPDATE SET
                    n_runs = EXCLUDED.n_runs,
                    success_rate = EXCLUDED.success_rate,
                    mean_runtime = EXCLUDED.mean_runtime
            """,
                (
                    task_id,
                    agent_name,
                    n_runs,
                    success_rate,
                    max(0, success_rate - 0.1),
                    min(1, success_rate + 0.1),
                    variance,
                    mean_runtime,
                    reliability_score,
                ),
            )

print("✓ Inserted multi-run metrics")

# 5. Insert task health data
for task_id, _, _, _, _ in tasks:
    cursor.execute(
        """
        SELECT
            AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate,
            COUNT(DISTINCT agent_id) as n_agents,
            COUNT(*) as n_runs
        FROM runs
        WHERE task_id = %s
    """,
        (task_id,),
    )

    result = cursor.fetchone()
    if result:
        success_rate, n_agents, n_runs = result
        success_rate = float(success_rate) if success_rate else 0.0

        # Determine health status
        if success_rate >= 0.8:
            health_status = "healthy"
        elif success_rate >= 0.5:
            health_status = "flaky"
        else:
            health_status = "broken"

        cursor.execute(
            """
            INSERT INTO task_health (
                task_id, health_status, success_rate, variance,
                n_agents, recommendations
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (task_id)
            DO UPDATE SET
                success_rate = EXCLUDED.success_rate,
                health_status = EXCLUDED.health_status
        """,
            (
                task_id,
                health_status,
                success_rate,
                0.05,
                n_agents,
                f"Task is {health_status}. Success rate: {success_rate:.1%}",
            ),
        )

print("✓ Inserted task health data")

# Commit and close
conn.commit()
cursor.close()
conn.close()

print("\n" + "=" * 70)
print("✓ Test data insertion complete!")
print("=" * 70)
print("\nSummary:")
print(f"  - Tasks: {len(tasks)}")
print(f"  - Agents: {len(agents)}")
print(f"  - Runs: {run_count}")
print(f"  - Multi-run metrics: {len(tasks) * len(agents)}")
print(f"  - Task health records: {len(tasks)}")
print("\nDatabase is now populated with test data for E2E validation.")
