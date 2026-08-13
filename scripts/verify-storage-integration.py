"""
Manual verification script for storage integration in CLI.

This script manually tests that the storage integration is working correctly
in the CLI commands without relying on pytest.
"""

import os
import sys
from unittest.mock import patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runner.cli import get_storage


def test_get_storage_with_env_vars():
    """Test that get_storage reads environment variables correctly."""
    print("Test 1: get_storage reads environment variables")

    test_env = {
        "DB_HOST": "test-host",
        "DB_PORT": "5433",
        "DB_NAME": "test-db",
        "DB_USER": "test-user",
        "DB_PASSWORD": "test-password",
    }

    with patch.dict(os.environ, test_env, clear=False):
        with patch("runner.storage.Storage") as mock_storage:
            # Call get_storage
            get_storage()

            # Check if Storage was called with correct parameters
            call_args = mock_storage.call_args
            if call_args:
                kwargs = call_args.kwargs
                assert (
                    kwargs["db_host"] == "test-host"
                ), f"Expected test-host, got {kwargs['db_host']}"
                assert kwargs["db_port"] == 5433, f"Expected 5433, got {kwargs['db_port']}"
                assert kwargs["db_name"] == "test-db", f"Expected test-db, got {kwargs['db_name']}"
                assert (
                    kwargs["db_user"] == "test-user"
                ), f"Expected test-user, got {kwargs['db_user']}"
                assert (
                    kwargs["db_password"] == "test-password"
                ), f"Expected test-password, got {kwargs['db_password']}"
                print("  ✓ PASSED: get_storage reads environment variables correctly")
            else:
                print("  ✗ FAILED: Storage was not called")
                return False

    return True


def test_get_storage_with_defaults():
    """Test that get_storage uses default values when env vars not set."""
    print("\nTest 2: get_storage uses default values")

    # Remove DB env vars
    for key in ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]:
        os.environ.pop(key, None)

    with patch("runner.storage.Storage") as mock_storage:
        # Call get_storage
        get_storage()

        # Check if Storage was called with defaults
        call_args = mock_storage.call_args
        if call_args:
            kwargs = call_args.kwargs
            assert kwargs["db_host"] == "localhost", f"Expected localhost, got {kwargs['db_host']}"
            assert kwargs["db_port"] == 5432, f"Expected 5432, got {kwargs['db_port']}"
            assert (
                kwargs["db_name"] == "agentbench"
            ), f"Expected agentbench, got {kwargs['db_name']}"
            assert kwargs["db_user"] == "postgres", f"Expected postgres, got {kwargs['db_user']}"
            assert (
                kwargs["db_password"] == "postgres"
            ), f"Expected postgres, got {kwargs['db_password']}"
            print("  ✓ PASSED: get_storage uses default values correctly")
        else:
            print("  ✗ FAILED: Storage was not called")
            return False

    return True


def test_cli_commands_have_storage_integration():
    """Test that CLI commands have storage integration code."""
    print("\nTest 3: CLI commands have storage integration")

    # Read CLI file and check for storage integration
    cli_path = os.path.join(os.path.dirname(__file__), "..", "runner", "cli.py")
    with open(cli_path, "r") as f:
        cli_content = f.read()

    # Check for key integration points
    checks = [
        ("get_storage() helper function", "def get_storage()"),
        ("Storage imported in get_storage", "from runner.storage import Storage"),
        ("Environment variables read", 'os.getenv("DB_HOST"'),
        ("bench command calls get_storage", "storage = get_storage()"),
        ("bench stores task", "storage.store_task("),
        ("bench stores agent", "storage.store_agent("),
        ("agent_run stores results", "storage.store_result("),
        ("Database connection logging", "logger.info"),
    ]

    all_passed = True
    for check_name, check_string in checks:
        if check_string in cli_content:
            print(f"  ✓ PASSED: {check_name}")
        else:
            print(f"  ✗ FAILED: {check_name}")
            all_passed = False

    return all_passed


if __name__ == "__main__":
    print("=" * 60)
    print("Storage Integration Verification")
    print("=" * 60)
    print()

    results = []
    results.append(test_get_storage_with_env_vars())
    results.append(test_get_storage_with_defaults())
    results.append(test_cli_commands_have_storage_integration())

    print()
    print("=" * 60)
    if all(results):
        print("✓ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED")
        sys.exit(1)
