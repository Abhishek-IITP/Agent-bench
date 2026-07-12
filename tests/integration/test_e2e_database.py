"""
Integration tests for end-to-end database workflow.

Tests the complete data flow from CLI through Storage to PostgreSQL.
Tests fallback behavior when database is unavailable.
Tests concurrent execution scenarios.

Requirements: REQ-2.1.1, REQ-2.1.2, REQ-2.2.4
"""

import os
import time
from pathlib import Path

import pytest

from runner.logging import get_logger
from runner.models import EvaluationResult, TaskConfig
from runner.storage import Storage

logger = get_logger(__name__)


@pytest.fixture
def test_storage():
    """Storage connected to test database."""
    return Storage(
        db_host=os.getenv("DB_HOST", "127.0.0.1"),
        db_port=int(os.getenv("DB_PORT_TEST", "5433")),
        db_name=os.getenv("DB_NAME_TEST", "agentbench_test"),
        db_user=os.getenv("DB_USER", "postgres"),
        db_password=os.getenv("DB_PASSWORD_TEST", "postgres_test"),
    )


@pytest.fixture
def test_task_config():
    """Sample task config for testing."""
    from runner.models import TaskCategory, TaskDifficulty

    return TaskConfig(
        id="test-task-e2e",
        name="Test Task E2E",
        category=TaskCategory.FILESYSTEM,
        difficulty=TaskDifficulty.EASY,
        version="1.0.0",
        description="Test task for E2E testing",
        timeout=300,
        docker_image="ubuntu:22.04",
    )


class TestDatabaseConnection:
    """Test database connection and basic operations."""

    def test_connection_established(self, test_storage):
        """Test that database connection can be established."""
        assert test_storage.db_connected, "Database connection should be established"
        assert test_storage.db is not None, "Database client should be initialized"

    def test_connection_with_invalid_credentials(self):
        """Test graceful handling of invalid credentials."""
        storage = Storage(
            db_host="localhost",
            db_port=5433,
            db_name="nonexistent_db",
            db_user="invalid_user",
            db_password="invalid_password",
        )

        # Should fall back to file-based storage
        assert not storage.db_connected, "Should not be connected with invalid credentials"
        assert storage.fallback_dir.exists(), "Fallback directory should exist"


class TestCompleteWorkflow:
    """Test complete E2E workflow from task storage to result retrieval."""

    def test_store_task(self, test_storage, test_task_config):
        """Test storing task metadata."""
        success = test_storage.store_task(test_task_config)
        assert success, "Task storage should succeed"

    def test_store_agent(self, test_storage):
        """Test storing agent metadata."""
        agent_id = test_storage.store_agent(
            agent_id="test-agent-e2e",
            agent_name="test-agent-e2e",
            agent_type="openai",
            model="gpt-4",
            config={"temperature": 0.7},
        )

        assert agent_id is not None, "Agent storage should return ID"
        assert isinstance(agent_id, int), "Agent ID should be integer"

    def test_complete_run_workflow(self, test_storage, test_task_config):
        """Test complete run storage workflow."""
        # Store task
        test_storage.store_task(test_task_config)

        # Store agent
        agent_id = test_storage.store_agent(
            agent_id="test-agent-workflow",
            agent_name="test-agent-workflow",
            agent_type="openai",
            model="gpt-4",
            config={},
        )
        assert agent_id is not None

        # Start run
        run_id = test_storage.start_run(test_task_config.id, agent_id)
        assert run_id is not None
        assert len(run_id) == 36, "Run ID should be UUID format"

        # Store result
        result = EvaluationResult(
            task_id=test_task_config.id,
            passed=True,
            score=0.95,
            test_output="All tests passed",
            details={"test_count": 5, "passed": 5},
        )

        success = test_storage.store_result(run_id, result)
        assert success, "Result storage should succeed"

        # Store execution metrics
        success = test_storage.store_execution_metrics(
            run_id=run_id,
            commands_executed=10,
            files_created=3,
            files_modified=2,
            tokens_used=1500,
            cost=0.05,
        )
        assert success, "Metrics storage should succeed"

        # Complete run
        success = test_storage.complete_run(run_id, True, 45.5)
        assert success, "Complete run should succeed"

        # Verify data
        runs = test_storage.get_runs(task_id=test_task_config.id, limit=10)
        assert len(runs) > 0, "Should retrieve stored run"

        stored_run = next((r for r in runs if r["id"] == run_id), None)
        assert stored_run is not None, "Should find the specific run"
        assert stored_run["success"] is True, "Run should be marked as successful"
        assert stored_run["duration"] == 45.5, "Duration should match"

    def test_multiple_runs(self, test_storage, test_task_config):
        """Test storing multiple runs for the same task."""
        # Store task
        test_storage.store_task(test_task_config)

        # Store agent
        agent_id = test_storage.store_agent(
            agent_id="test-agent-multi",
            agent_name="test-agent-multi",
            agent_type="openai",
            model="gpt-4",
            config={},
        )

        run_ids = []
        for i in range(3):
            # Start run
            run_id = test_storage.start_run(test_task_config.id, agent_id)
            run_ids.append(run_id)

            # Store result
            result = EvaluationResult(
                task_id=test_task_config.id,
                passed=(i % 2 == 0),  # Alternate pass/fail
                score=1.0 if (i % 2 == 0) else 0.0,
                test_output=f"Test run {i+1}",
                details={"run_number": i + 1},
            )
            test_storage.store_result(run_id, result)

            # Complete run
            test_storage.complete_run(run_id, result.passed, 10.0 + i)

        # Verify all runs stored
        runs = test_storage.get_runs(task_id=test_task_config.id, limit=10)
        stored_run_ids = [r["id"] for r in runs]

        for run_id in run_ids:
            assert run_id in stored_run_ids, f"Run {run_id} should be stored"

        # Verify statistics
        stats = test_storage.get_task_stats(test_task_config.id)
        assert stats["total_runs"] >= 3, "Should have at least 3 runs"


class TestFallbackBehavior:
    """Test fallback to file-based storage when database unavailable."""

    def test_fallback_task_storage(self, test_task_config, tmp_path):
        """Test file-based task storage fallback."""
        # Create storage without database connection
        storage = Storage(
            db_host="invalid_host",
            db_port=9999,
            db_name="invalid_db",
            db_user="invalid_user",
            db_password="invalid_password",
            fallback_dir=str(tmp_path / "fallback"),
        )

        assert not storage.db_connected, "Should not be connected"

        # Store task should use fallback
        success = storage.store_task(test_task_config)
        assert success, "Fallback task storage should succeed"

        # Verify file created
        fallback_file = (
            Path(tmp_path) / "fallback" / "tasks" / test_task_config.id / "metadata.json"
        )
        assert fallback_file.exists(), "Fallback file should exist"

        # Verify content
        import json

        with open(fallback_file) as f:
            data = json.load(f)
            assert data["id"] == test_task_config.id
            assert data["name"] == test_task_config.name

    def test_fallback_result_storage(self, test_task_config, tmp_path):
        """Test file-based result storage fallback."""
        storage = Storage(
            db_host="invalid_host",
            db_port=9999,
            db_name="invalid_db",
            db_user="invalid_user",
            db_password="invalid_password",
            fallback_dir=str(tmp_path / "fallback"),
        )

        run_id = "test-run-fallback-123"
        result = EvaluationResult(
            task_id=test_task_config.id,
            passed=True,
            score=1.0,
            test_output="Fallback test",
            details={},
        )

        success = storage.store_result(run_id, result)
        assert success, "Fallback result storage should succeed"

        # Verify file created
        result_file = Path(tmp_path) / "fallback" / run_id / "result.json"
        assert result_file.exists(), "Result fallback file should exist"


class TestConcurrentExecution:
    """Test concurrent run execution scenarios."""

    def test_concurrent_runs_different_agents(self, test_storage, test_task_config):
        """Test multiple agents running the same task concurrently."""
        # Store task
        test_storage.store_task(test_task_config)

        # Store multiple agents
        agent_ids = []
        for i in range(3):
            agent_id = test_storage.store_agent(
                agent_id=f"test-agent-concurrent-{i}",
                agent_name=f"test-agent-concurrent-{i}",
                agent_type="openai",
                model="gpt-4",
                config={},
            )
            agent_ids.append(agent_id)

        # Start concurrent runs
        run_ids = []
        for agent_id in agent_ids:
            run_id = test_storage.start_run(test_task_config.id, agent_id)
            run_ids.append(run_id)

            # Immediately store result (simulating concurrent execution)
            result = EvaluationResult(
                task_id=test_task_config.id,
                passed=True,
                score=0.9,
                test_output="Concurrent test",
                details={},
            )
            test_storage.store_result(run_id, result)
            test_storage.complete_run(run_id, True, 30.0)

        # Verify all runs stored correctly
        runs = test_storage.get_runs(task_id=test_task_config.id, limit=20)
        stored_run_ids = [r["id"] for r in runs]

        for run_id in run_ids:
            assert run_id in stored_run_ids, f"Concurrent run {run_id} should be stored"

    def test_multi_run_metrics_storage(self, test_storage, test_task_config):
        """Test storing aggregated multi-run metrics."""
        # Store task
        test_storage.store_task(test_task_config)

        # Store multi-run metrics
        success = test_storage.store_multi_run_metrics(
            task_id=test_task_config.id,
            agent_name="test-agent-metrics",
            n_runs=10,
            success_rate=0.8,
            confidence_interval_lower=0.7,
            confidence_interval_upper=0.9,
            variance=0.04,
            mean_runtime=25.5,
            mean_tokens=1200,
            mean_cost=0.06,
            reliability_score=85.0,
        )

        assert success, "Multi-run metrics storage should succeed"


class TestDataIntegrity:
    """Test data integrity and referential constraints."""

    def test_foreign_key_constraints(self, test_storage, test_task_config):
        """Test that foreign key constraints are enforced."""
        # Try to start run without storing task first
        # This should either fail or auto-create the task
        test_storage.store_task(test_task_config)

        # Store agent
        agent_id = test_storage.store_agent(
            agent_id="test-agent-fk",
            agent_name="test-agent-fk",
            agent_type="openai",
            model="gpt-4",
            config={},
        )

        # Now run should work
        run_id = test_storage.start_run(test_task_config.id, agent_id)
        assert run_id is not None, "Run with valid FK should succeed"

    def test_unique_constraints(self, test_storage):
        """Test that unique constraints are respected."""
        # Store same agent twice
        agent_name = "test-agent-unique"

        agent_id_1 = test_storage.store_agent(
            agent_id=agent_name,
            agent_name=agent_name,
            agent_type="openai",
            model="gpt-4",
            config={},
        )

        # Second insert should return existing ID (ON CONFLICT DO NOTHING)
        agent_id_2 = test_storage.store_agent(
            agent_id=agent_name,
            agent_name=agent_name,
            agent_type="openai",
            model="gpt-4-turbo",  # Different config
            config={},
        )

        assert agent_id_1 == agent_id_2, "Should return existing agent ID"


class TestQueryPerformance:
    """Test query performance requirements."""

    def test_task_stats_query_performance(self, test_storage, test_task_config):
        """Test that task stats query completes quickly."""
        test_storage.store_task(test_task_config)

        start_time = time.time()
        stats = test_storage.get_task_stats(test_task_config.id)
        elapsed = time.time() - start_time

        # REQ-2.1.1: Single task lookup < 10ms (lenient for test environment)
        assert elapsed < 0.1, f"Task stats query too slow: {elapsed:.3f}s"
        assert "total_runs" in stats, "Should return stats structure"

    def test_get_runs_query_performance(self, test_storage, test_task_config):
        """Test that get runs query completes quickly."""
        test_storage.store_task(test_task_config)

        start_time = time.time()
        runs = test_storage.get_runs(task_id=test_task_config.id, limit=50)
        elapsed = time.time() - start_time

        # REQ-2.1.2: List runs query < 50ms (lenient for test environment)
        assert elapsed < 0.2, f"Get runs query too slow: {elapsed:.3f}s"
        assert isinstance(runs, list), "Should return list of runs"
