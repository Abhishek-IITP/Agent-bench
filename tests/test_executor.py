"""
Tests for the task executor module.

Note: Executor tests require Docker. Skipped if Docker is not available.
"""

import pytest

from runner.executor import TaskExecutor


class TestTaskExecutor:
    """Test suite for TaskExecutor."""

    @pytest.fixture
    def executor(self):
        """Create a TaskExecutor instance."""
        try:
            return TaskExecutor()
        except Exception as e:
            pytest.skip(f"Docker not available: {e}")

    def test_executor_init(self, executor):
        """Test TaskExecutor initialization."""
        assert executor is not None
        assert executor.docker_client is not None
        assert executor.loader is not None

    def test_executor_has_dockerfile(self):
        """Test that Dockerfile exists."""
        from pathlib import Path

        dockerfile = Path("Dockerfile")
        assert dockerfile.exists()

    def test_executor_loader_finds_tasks(self, executor):
        """Test that executor loader finds tasks."""
        tasks = executor.loader.discover_tasks()
        assert len(tasks) >= 9, f"Expected at least 9 tasks, found {len(tasks)}"
