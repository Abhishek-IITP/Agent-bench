"""
Integration tests for TaskExecutor with Docker.

These tests require Docker to be running but don't require building an image.
They test the execution lifecycle and error handling.
"""

import pytest

from runner.executor import TaskExecutor
from runner.models import EvaluationResult


class TestTaskExecutorIntegration:
    """Integration tests for TaskExecutor."""

    @pytest.fixture
    def executor(self):
        """Create an executor instance."""
        try:
            executor = TaskExecutor()
            # Don't build image, just verify initialization
            assert executor.docker_client is not None
            assert executor.loader is not None
            return executor
        except Exception as e:
            pytest.skip(f"Docker not available: {e}")

    def test_executor_initialization(self, executor):
        """Test TaskExecutor initializes correctly."""
        assert executor.base_image == "agentbench-base:latest"
        assert executor.dockerfile_path == "Dockerfile"

    def test_executor_has_docker_client(self, executor):
        """Test executor has Docker client."""
        assert executor.docker_client is not None

    def test_executor_has_task_loader(self, executor):
        """Test executor has task loader."""
        assert executor.loader is not None

    def test_execute_task_returns_evaluation_result(self, executor):
        """Test execute_task returns EvaluationResult."""
        # Use a valid task ID
        result = executor.execute_task("count-error-lines")

        assert isinstance(result, EvaluationResult)
        assert result.task_id == "count-error-lines"
        assert hasattr(result, "passed")
        assert hasattr(result, "score")
        assert hasattr(result, "test_output")

    def test_execute_nonexistent_task(self, executor):
        """Test execute_task with nonexistent task."""
        result = executor.execute_task("nonexistent-task-xyz")

        assert isinstance(result, EvaluationResult)
        assert result.passed is False
        # Should fail with appropriate error message
        assert (
            "error" in result.test_output.lower()
            or "not found" in result.test_output.lower()
            or "invalid" in result.test_output.lower()
        )
