#!/usr/bin/env python3
"""Performance testing script for database queries."""

import psycopg2
import time
from statistics import mean, stdev

# Performance targets from requirements
TARGETS = {
    "single_task_lookup": 10,  # < 10ms (REQ-2.1.1)
    "list_recent_runs": 50,  # < 50ms (REQ-2.1.2)
    "leaderboard_query": 200,  # < 200ms (REQ-2.1.3)
    "task_health_summary": 100,  # < 100ms (REQ-2.1.4)
}


def connect_db():
    """Connect to database."""
    return psycopg2.connect(
        host="127.0.0.1", port=5432, database="agentbench", user="postgres", password="postgres"
    )


def measure_query(cursor, query, params=None, iterations=10):
    """Measure query execution time over multiple iterations."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        cursor.fetchall()
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms

    return {
        "mean": mean(times),
        "min": min(times),
        "max": max(times),
        "stdev": stdev(times) if len(times) > 1 else 0,
    }


def main():
    """Run performance tests."""
    print("=" * 80)
    print("Database Query Performance Testing")
    print("=" * 80)
    print()

    conn = connect_db()
    cursor = conn.cursor()

    results = []

    # Test 1: Single Task Lookup (REQ-2.1.1)
    print("Test 1: Single Task Lookup")
    print("-" * 80)
    query = "SELECT * FROM tasks WHERE id = %s"
    stats = measure_query(cursor, query, ("find-database-files",), iterations=20)
    print(f"  Mean: {stats['mean']:.2f}ms")
    print(f"  Min: {stats['min']:.2f}ms")
    print(f"  Max: {stats['max']:.2f}ms")
    print(f"  StdDev: {stats['stdev']:.2f}ms")
    print(f"  Target: < {TARGETS['single_task_lookup']}ms")
    passed = stats["mean"] < TARGETS["single_task_lookup"]
    print(f"  Status: {'✓ PASS' if passed else '✗ FAIL'}")
    results.append(("Single Task Lookup", passed, stats["mean"], TARGETS["single_task_lookup"]))
    print()

    # Test 2: List Recent Runs (50 records) (REQ-2.1.2)
    print("Test 2: List Recent Runs (50 records)")
    print("-" * 80)
    query = """
        SELECT r.*, a.name as agent_name
        FROM runs r
        JOIN agents a ON r.agent_id = a.id
        ORDER BY r.started_at DESC
        LIMIT 50
    """
    stats = measure_query(cursor, query, iterations=20)
    print(f"  Mean: {stats['mean']:.2f}ms")
    print(f"  Min: {stats['min']:.2f}ms")
    print(f"  Max: {stats['max']:.2f}ms")
    print(f"  StdDev: {stats['stdev']:.2f}ms")
    print(f"  Target: < {TARGETS['list_recent_runs']}ms")
    passed = stats["mean"] < TARGETS["list_recent_runs"]
    print(f"  Status: {'✓ PASS' if passed else '✗ FAIL'}")
    results.append(("List Recent Runs", passed, stats["mean"], TARGETS["list_recent_runs"]))
    print()

    # Test 3: Leaderboard Aggregation (REQ-2.1.3)
    print("Test 3: Leaderboard Aggregation Query")
    print("-" * 80)
    query = """
        SELECT
            a.name as agent_name,
            COUNT(DISTINCT r.task_id) as tasks_solved,
            COUNT(r.id) as total_runs,
            AVG(CASE WHEN r.success THEN 1.0 ELSE 0.0 END) as success_rate,
            AVG(m.cost) as avg_cost,
            AVG(m.tokens_used) as avg_tokens
        FROM agents a
        LEFT JOIN runs r ON a.id = r.agent_id
        LEFT JOIN execution_metrics m ON r.id = m.run_id
        GROUP BY a.id, a.name
        HAVING COUNT(r.id) > 0
        ORDER BY success_rate DESC, avg_cost ASC
    """
    stats = measure_query(cursor, query, iterations=15)
    print(f"  Mean: {stats['mean']:.2f}ms")
    print(f"  Min: {stats['min']:.2f}ms")
    print(f"  Max: {stats['max']:.2f}ms")
    print(f"  StdDev: {stats['stdev']:.2f}ms")
    print(f"  Target: < {TARGETS['leaderboard_query']}ms")
    passed = stats["mean"] < TARGETS["leaderboard_query"]
    print(f"  Status: {'✓ PASS' if passed else '✗ FAIL'}")
    results.append(("Leaderboard Aggregation", passed, stats["mean"], TARGETS["leaderboard_query"]))
    print()

    # Test 4: Task Health Summary (REQ-2.1.4)
    print("Test 4: Task Health Summary Query")
    print("-" * 80)
    query = """
        SELECT
            t.id as task_id,
            t.name,
            th.health_status,
            th.success_rate,
            th.variance,
            th.n_agents,
            COUNT(r.id) as total_runs
        FROM tasks t
        LEFT JOIN task_health th ON t.id = th.task_id
        LEFT JOIN runs r ON t.id = r.task_id
        GROUP BY t.id, t.name, th.health_status, th.success_rate, th.variance, th.n_agents
        ORDER BY th.success_rate DESC
    """
    stats = measure_query(cursor, query, iterations=15)
    print(f"  Mean: {stats['mean']:.2f}ms")
    print(f"  Min: {stats['min']:.2f}ms")
    print(f"  Max: {stats['max']:.2f}ms")
    print(f"  StdDev: {stats['stdev']:.2f}ms")
    print(f"  Target: < {TARGETS['task_health_summary']}ms")
    passed = stats["mean"] < TARGETS["task_health_summary"]
    print(f"  Status: {'✓ PASS' if passed else '✗ FAIL'}")
    results.append(("Task Health Summary", passed, stats["mean"], TARGETS["task_health_summary"]))
    print()

    # Test 5: Complex Join Query (Run Details)
    print("Test 5: Run Details with Joins")
    print("-" * 80)
    query = """
        SELECT
            r.id, r.task_id, r.agent_id, r.started_at, r.ended_at, r.duration, r.success,
            a.name as agent_name,
            res.passed, res.score, res.test_output, res.test_details,
            m.commands_executed, m.files_created, m.files_modified, m.tokens_used, m.cost
        FROM runs r
        JOIN agents a ON r.agent_id = a.id
        LEFT JOIN results res ON r.id = res.run_id
        LEFT JOIN execution_metrics m ON r.id = m.run_id
        WHERE r.id = %s
    """
    cursor.execute("SELECT id FROM runs LIMIT 1")
    sample_run_id = cursor.fetchone()[0]
    stats = measure_query(cursor, query, (sample_run_id,), iterations=20)
    print(f"  Mean: {stats['mean']:.2f}ms")
    print(f"  Min: {stats['min']:.2f}ms")
    print(f"  Max: {stats['max']:.2f}ms")
    print(f"  StdDev: {stats['stdev']:.2f}ms")
    print("  Note: No specific target, measuring for reference")
    print()

    # Summary
    print("=" * 80)
    print("Performance Test Summary")
    print("=" * 80)
    print()

    all_passed = all(r[1] for r in results)

    for name, passed, actual, target in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {name:30s} {status:10s} {actual:8.2f}ms / {target:5d}ms")

    print()
    print("=" * 80)

    if all_passed:
        print("✓ All performance targets met!")
    else:
        print("✗ Some performance targets not met")
        failed = [r for r in results if not r[1]]
        print(f"  Failed tests: {len(failed)}/{len(results)}")

    print("=" * 80)

    cursor.close()
    conn.close()

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
