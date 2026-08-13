#!/usr/bin/env python3
"""Quick verification that all system components are running and accessible."""

import psycopg2
import requests
import sys


def check_database():
    """Check database connectivity."""
    try:
        conn = psycopg2.connect(
            host="127.0.0.1", port=5432, database="agentbench", user="postgres", password="postgres"
        )
        cursor = conn.cursor()

        # Check tables
        cursor.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname='public'")
        table_count = cursor.fetchone()[0]

        # Check data
        cursor.execute("SELECT COUNT(*) FROM runs")
        run_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tasks")
        task_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM agents")
        agent_count = cursor.fetchone()[0]

        conn.close()

        print("✓ Database Status: HEALTHY")
        print(f"  - Tables: {table_count}")
        print(f"  - Runs: {run_count}")
        print(f"  - Tasks: {task_count}")
        print(f"  - Agents: {agent_count}")
        return True

    except Exception as e:
        print("✗ Database Status: FAILED")
        print(f"  Error: {e}")
        return False


def check_api():
    """Check API server."""
    try:
        # Health check
        response = requests.get("http://localhost:3001/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ API Server Status: HEALTHY")
            print(f"  - Status: {data.get('status')}")
            print(f"  - Database: {data.get('database')}")

            # Test endpoints
            endpoints_ok = 0
            endpoints = [
                "/api/tasks",
                "/api/runs",
                "/api/leaderboard",
                "/api/health/tasks",
            ]

            for endpoint in endpoints:
                try:
                    r = requests.get(f"http://localhost:3001{endpoint}", timeout=5)
                    if r.status_code == 200:
                        endpoints_ok += 1
                except Exception:
                    pass

            print(f"  - Endpoints working: {endpoints_ok}/{len(endpoints)}")
            return True
        else:
            print("✗ API Server Status: UNHEALTHY")
            print(f"  Status code: {response.status_code}")
            return False

    except Exception as e:
        print("✗ API Server Status: FAILED")
        print(f"  Error: {e}")
        return False


def check_dashboard():
    """Check dashboard accessibility."""
    try:
        response = requests.get("http://localhost:3002", timeout=5)
        if response.status_code == 200:
            print("✓ Dashboard Status: ACCESSIBLE")
            print("  - URL: http://localhost:3002")
            return True
        else:
            print("✗ Dashboard Status: INACCESSIBLE")
            print(f"  Status code: {response.status_code}")
            return False

    except Exception as e:
        print("✗ Dashboard Status: FAILED")
        print(f"  Error: {e}")
        return False


def main():
    """Run all checks."""
    print("=" * 70)
    print("System Status Verification")
    print("=" * 70)
    print()

    db_ok = check_database()
    print()

    api_ok = check_api()
    print()

    dashboard_ok = check_dashboard()
    print()

    print("=" * 70)
    if db_ok and api_ok and dashboard_ok:
        print("✓ All systems operational")
        print("=" * 70)
        print()
        print("Access Points:")
        print("  - Database: localhost:5432")
        print("  - API: http://localhost:3001")
        print("  - Dashboard: http://localhost:3002")
        return 0
    else:
        print("✗ Some systems not operational")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
