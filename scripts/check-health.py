#!/usr/bin/env python3
"""
System health check script.
Verifies database connectivity, API availability, and overall system health.
"""

import psycopg2
import requests
import sys
import os
from typing import List, Tuple
import time


class HealthCheck:
    """System health checker."""

    def __init__(self):
        self.db_host = os.getenv("DB_HOST", "127.0.0.1")
        self.db_port = int(os.getenv("DB_PORT", "5432"))
        self.db_name = os.getenv("DB_NAME", "agentbench")
        self.db_user = os.getenv("DB_USER", "postgres")
        self.db_password = os.getenv("DB_PASSWORD", "postgres")
        self.api_url = os.getenv("API_URL", "http://localhost:3001")

        self.checks: List[Tuple[str, bool, str]] = []

    def add_check(self, name: str, passed: bool, message: str = ""):
        """Add a health check result."""
        self.checks.append((name, passed, message))

    def check_database_connection(self) -> bool:
        """Check if database is accessible."""
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
                connect_timeout=5,
            )
            conn.close()
            self.add_check("Database Connection", True, "PostgreSQL is accessible")
            return True
        except psycopg2.OperationalError as e:
            self.add_check("Database Connection", False, f"Connection failed: {e}")
            return False
        except Exception as e:
            self.add_check("Database Connection", False, f"Unexpected error: {e}")
            return False

    def check_database_schema(self) -> bool:
        """Check if database schema is initialized."""
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            table_count = cursor.fetchone()[0]
            cursor.close()
            conn.close()

            if table_count >= 9:
                self.add_check("Database Schema", True, f"{table_count} tables found")
                return True
            else:
                self.add_check(
                    "Database Schema", False, f"Only {table_count} tables found (expected 9)"
                )
                return False
        except Exception as e:
            self.add_check("Database Schema", False, f"Schema check failed: {e}")
            return False

    def check_database_performance(self) -> bool:
        """Check database query performance."""
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
            )
            cursor = conn.cursor()

            # Test simple query performance
            start = time.time()
            cursor.execute("SELECT 1")
            duration = (time.time() - start) * 1000  # Convert to ms

            cursor.close()
            conn.close()

            if duration < 100:
                self.add_check("Database Performance", True, f"Query latency: {duration:.2f}ms")
                return True
            else:
                self.add_check("Database Performance", False, f"Slow query: {duration:.2f}ms")
                return False
        except Exception as e:
            self.add_check("Database Performance", False, f"Performance check failed: {e}")
            return False

    def check_api_health(self) -> bool:
        """Check if API server is running and healthy."""
        try:
            response = requests.get(f"{self.api_url}/api/health", timeout=5)
            if response.status_code == 200:
                self.add_check("API Server", True, f"API is running on {self.api_url}")
                return True
            else:
                self.add_check("API Server", False, f"API returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.add_check("API Server", False, "API is not running")
            return False
        except requests.exceptions.Timeout:
            self.add_check("API Server", False, "API request timed out")
            return False
        except Exception as e:
            self.add_check("API Server", False, f"API check failed: {e}")
            return False

    def check_api_endpoints(self) -> bool:
        """Check if critical API endpoints are accessible."""
        endpoints = [
            "/api/tasks",
            "/api/runs",
            "/api/health/benchmark",
        ]

        all_passed = True
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.api_url}{endpoint}", timeout=5)
                if response.status_code in [200, 404]:  # 404 is OK for empty data
                    self.add_check(f"API {endpoint}", True, f"Status {response.status_code}")
                else:
                    self.add_check(f"API {endpoint}", False, f"Status {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.add_check(f"API {endpoint}", False, f"Request failed: {e}")
                all_passed = False

        return all_passed

    def check_docker_container(self) -> bool:
        """Check if Docker container is running."""
        try:
            import subprocess

            result = subprocess.run(
                ["docker", "ps", "--filter", "name=agentbench-db", "--format", "{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0 and result.stdout.strip():
                status = result.stdout.strip()
                if "Up" in status:
                    self.add_check("Docker Container", True, f"Status: {status}")
                    return True
                else:
                    self.add_check("Docker Container", False, f"Status: {status}")
                    return False
            else:
                self.add_check("Docker Container", False, "Container not found")
                return False
        except FileNotFoundError:
            self.add_check("Docker Container", False, "Docker CLI not found")
            return False
        except Exception as e:
            self.add_check("Docker Container", False, f"Check failed: {e}")
            return False

    def print_results(self) -> bool:
        """Print health check results and return overall status."""
        print("=" * 70)
        print("AgentBench System Health Check")
        print("=" * 70)

        print("\n🔧 Configuration:")
        print(f"  Database: {self.db_user}@{self.db_host}:{self.db_port}/{self.db_name}")
        print(f"  API URL: {self.api_url}")

        print("\n🏥 Health Checks:")

        all_passed = True
        for name, passed, message in self.checks:
            status = "✓" if passed else "❌"
            print(f"  {status} {name:30} {message}")
            if not passed:
                all_passed = False

        print("\n" + "=" * 70)
        if all_passed:
            print("✅ System Health: HEALTHY - All checks passed")
            print("=" * 70)
            return True
        else:
            print("⚠️  System Health: DEGRADED - Some checks failed")
            print("\nTroubleshooting:")
            print("  1. Database: docker compose up -d postgres")
            print("  2. API: cd dashboard/api && bun run dev")
            print("  3. Check logs: docker logs agentbench-db")
            print("=" * 70)
            return False

    def run_all_checks(self, skip_api: bool = False) -> bool:
        """Run all health checks."""
        # Core checks
        self.check_docker_container()
        db_ok = self.check_database_connection()

        if db_ok:
            self.check_database_schema()
            self.check_database_performance()

        # API checks (optional)
        if not skip_api:
            api_ok = self.check_api_health()
            if api_ok:
                self.check_api_endpoints()

        return self.print_results()


def main():
    """Main health check routine."""
    # Parse arguments
    skip_api = "--skip-api" in sys.argv or "--no-api" in sys.argv

    health_check = HealthCheck()
    all_healthy = health_check.run_all_checks(skip_api=skip_api)

    sys.exit(0 if all_healthy else 1)


if __name__ == "__main__":
    main()
