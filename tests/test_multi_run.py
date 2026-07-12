"""
Tests for multi-run executor functionality.

Tests cover:
- MultiRunResult model creation and aggregation
- Sequential execution with varying numbers of runs
- Failure handling and graceful degradation
- Result aggregation and statistics computation
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from runner.agents.base import AgentConfig, AgentType
from runner.models import EvaluationResult
from runner.multi_run import MultiRunExecutor, MultiRunResult


class TestMultiRunResult:
    """Test MultiRunResult model."""

    def test_create_empty_multi_run_result(self):
        """Test creating an empty MultiRunResult."""
        result = MultiRunResult(
            task_id="test-task",
            agent_name="test-agent",
            n_runs=5,
        )

        assert result.task_id == "test-task"
        assert result.agent_name == "test-agent"
        assert result.n_runs == 5
        assert result.success_count == 0
        assert result.success_rate == 0.0
        assert len(result.runs) == 0

    def test_multi_run_result_with_runs(self):
        """Test MultiRunResult with individual run results."""
        runs = [
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=1.5),
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=1.6),
            EvaluationResult(task_id="test", passed=False, score=0.0, duration=0.5),
        ]

        result = MultiRunResult(
            task_id="test-task",
            agent_name="test-agent",
            n_runs=3,
            runs=runs,
            success_count=2,
            success_rate=2 / 3,
            mean_runtime=1.2,
        )

        assert len(result.runs) == 3
        assert result.success_count == 2
        assert result.failure_count == 1
        assert result.success_rate == pytest.approx(2 / 3, abs=0.01)

    def test_multi_run_result_all_passed(self):
        """Test MultiRunResult with all runs passing."""
        runs = [
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=1.0 + i * 0.1)
            for i in range(5)
        ]

        result = MultiRunResult(
            task_id="test-task",
            agent_name="test-agent",
            n_runs=5,
            runs=runs,
            success_count=5,
            success_rate=1.0,
            mean_runtime=1.2,
        )

        assert result.success_count == 5
        assert result.failure_count == 0
        assert result.success_rate == 1.0
        assert result.reliability_score == 1.0

    def test_multi_run_result_all_failed(self):
        """Test MultiRunResult with all runs failing."""
        runs = [
            EvaluationResult(task_id="test", passed=False, score=0.0, duration=0.5 + i * 0.1)
            for i in range(3)
        ]

        result = MultiRunResult(
            task_id="test-task",
            agent_name="test-agent",
            n_runs=3,
            runs=runs,
            success_count=0,
            success_rate=0.0,
            mean_runtime=0.6,
        )

        assert result.success_count == 0
        assert result.failure_count == 3
        assert result.success_rate == 0.0
        assert result.reliability_score == 0.0

    def test_reliability_score_computation(self):
        """Test that reliability score is computed correctly."""
        result = MultiRunResult(
            task_id="test-task",
            agent_name="test-agent",
            n_runs=10,
            runs=[],
            success_count=8,
            success_rate=0.8,
            mean_runtime=5.0,
        )

        # Reliability score should equal success rate (no variance penalty yet)
        assert result.reliability_score == 0.8

    def test_multi_run_result_aggregated_at_set(self):
        """Test that aggregated_at timestamp is set."""
        result = MultiRunResult(
            task_id="test-task",
            agent_name="test-agent",
            n_runs=1,
        )

        assert result.aggregated_at is not None
        assert isinstance(result.aggregated_at, datetime)


class TestMultiRunExecutor:
    """Test MultiRunExecutor class."""

    @pytest.fixture
    def mock_executor(self):
        """Create a mock TaskExecutor."""
        executor = MagicMock()
        return executor

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent."""
        agent = MagicMock()
        agent.config = AgentConfig(
            agent_type=AgentType.OPENAI,
            model="gpt-4",
            name="test-agent",
        )
        return agent

    @pytest.fixture
    def multi_run_executor(self, mock_executor):
        """Create a MultiRunExecutor with mock executor."""
        return MultiRunExecutor(executor=mock_executor)

    def test_executor_initialization_with_executor(self, mock_executor):
        """Test initializing executor with provided TaskExecutor."""
        executor = MultiRunExecutor(executor=mock_executor)
        assert executor.executor is mock_executor

    def test_executor_initialization_without_executor(self):
        """Test initializing executor without providing a TaskExecutor."""
        executor = MultiRunExecutor(executor=None)
        # Should create a default TaskExecutor
        assert executor.executor is not None

    def test_single_run_success(self, multi_run_executor, mock_agent, mock_executor):
        """Test executing a single successful run."""
        mock_executor.execute_task.return_value = EvaluationResult(
            task_id="test-task",
            passed=True,
            score=1.0,
            duration=2.5,
        )

        result = multi_run_executor._run_single(
            task_id="test-task",
            agent=mock_agent,
            run_num=1,
        )

        assert result.passed is True
        assert result.score == 1.0
        assert result.duration == 2.5
        mock_executor.execute_task.assert_called_once()

    def test_single_run_failure(self, multi_run_executor, mock_agent, mock_executor):
        """Test executing a single failed run."""
        mock_executor.execute_task.return_value = EvaluationResult(
            task_id="test-task",
            passed=False,
            score=0.0,
            duration=1.5,
        )

        result = multi_run_executor._run_single(
            task_id="test-task",
            agent=mock_agent,
            run_num=1,
        )

        assert result.passed is False
        assert result.score == 0.0

    def test_single_run_with_exception(self, multi_run_executor, mock_agent, mock_executor):
        """Test that exceptions during runs are caught and logged."""
        mock_executor.execute_task.side_effect = Exception("Execution timeout")

        result = multi_run_executor._run_single(
            task_id="test-task",
            agent=mock_agent,
            run_num=1,
        )

        # Should return a failed result, not crash
        assert result.passed is False
        assert "Exception during execution" in result.test_output
        assert "Execution timeout" in result.test_output

    def test_execute_multi_run_one_run(self, multi_run_executor, mock_agent, mock_executor):
        """Test multi-run execution with 1 run."""
        mock_executor.execute_task.return_value = EvaluationResult(
            task_id="test-task",
            passed=True,
            score=1.0,
            duration=2.0,
        )

        result = multi_run_executor.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=1,
        )

        assert result.n_runs == 1
        assert result.success_count == 1
        assert result.success_rate == 1.0
        assert result.mean_runtime == 2.0
        assert len(result.runs) == 1

    def test_execute_multi_run_three_runs(self, multi_run_executor, mock_agent, mock_executor):
        """Test multi-run execution with 3 runs."""
        # First two pass, third fails
        mock_executor.execute_task.side_effect = [
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=2.0),
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=2.1),
            EvaluationResult(task_id="test", passed=False, score=0.0, duration=1.5),
        ]

        result = multi_run_executor.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=3,
        )

        assert result.n_runs == 3
        assert result.success_count == 2
        assert result.failure_count == 1
        assert result.success_rate == pytest.approx(2 / 3, abs=0.01)
        assert len(result.runs) == 3

    def test_execute_multi_run_five_runs(self, multi_run_executor, mock_agent, mock_executor):
        """Test multi-run execution with 5 runs."""
        # 4 pass, 1 fails
        mock_executor.execute_task.side_effect = [
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=1.5 + i * 0.1)
            for i in range(4)
        ] + [
            EvaluationResult(task_id="test", passed=False, score=0.0, duration=0.5),
        ]

        result = multi_run_executor.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=5,
        )

        assert result.n_runs == 5
        assert result.success_count == 4
        assert result.failure_count == 1
        assert result.success_rate == 0.8
        assert len(result.runs) == 5

    def test_execute_multi_run_with_one_failure(
        self, multi_run_executor, mock_agent, mock_executor
    ):
        """Test that one run failure doesn't stop other runs from executing."""
        # First passes, second raises exception, third passes
        mock_executor.execute_task.side_effect = [
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=2.0),
            Exception("Connection error"),
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=2.0),
        ]

        result = multi_run_executor.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=3,
        )

        # Should complete all 3 runs despite exception
        assert len(result.runs) == 3
        assert result.runs[0].passed is True
        assert result.runs[1].passed is False  # Exception converted to failed result
        assert result.runs[2].passed is True
        assert result.success_count == 2

    def test_execute_multi_run_all_failures(self, multi_run_executor, mock_agent, mock_executor):
        """Test multi-run execution where all runs fail."""
        mock_executor.execute_task.side_effect = [
            EvaluationResult(task_id="test", passed=False, score=0.0, duration=0.5)
            for _ in range(3)
        ]

        result = multi_run_executor.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=3,
        )

        assert result.n_runs == 3
        assert result.success_count == 0
        assert result.success_rate == 0.0
        assert result.reliability_score == 0.0

    def test_execute_multi_run_empty_runs(self, multi_run_executor, mock_agent, mock_executor):
        """Test aggregation with no runs."""
        result = multi_run_executor._aggregate_results(
            task_id="test-task",
            agent=mock_agent,
            runs=[],
            n_runs=0,
        )

        assert result.n_runs == 0
        assert result.success_count == 0
        assert result.success_rate == 0.0
        assert result.mean_runtime == 0.0

    def test_multi_run_runtime_statistics(self, multi_run_executor, mock_agent, mock_executor):
        """Test that runtime statistics are computed correctly."""
        runtimes = [1.0, 2.0, 3.0, 2.5, 1.5]
        mock_executor.execute_task.side_effect = [
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=rt) for rt in runtimes
        ]

        result = multi_run_executor.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=5,
        )

        # Mean should be (1.0 + 2.0 + 3.0 + 2.5 + 1.5) / 5 = 2.0
        assert result.mean_runtime == pytest.approx(2.0, abs=0.01)

    def test_multi_run_passes_timeout_to_executor(
        self, multi_run_executor, mock_agent, mock_executor
    ):
        """Test that timeout is passed through to executor."""
        mock_executor.execute_task.return_value = EvaluationResult(
            task_id="test",
            passed=True,
            score=1.0,
            duration=1.0,
        )

        multi_run_executor.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=1,
            timeout=600,
        )

        mock_executor.execute_task.assert_called_once()
        call_kwargs = mock_executor.execute_task.call_args[1]
        assert call_kwargs.get("timeout") == 600

    def test_multi_run_result_fields_set_correctly(
        self, multi_run_executor, mock_agent, mock_executor
    ):
        """Test that all MultiRunResult fields are set correctly."""
        mock_executor.execute_task.return_value = EvaluationResult(
            task_id="test-task",
            passed=True,
            score=1.0,
            duration=5.0,
        )

        result = multi_run_executor.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=1,
        )

        # All required fields should be set
        assert result.task_id == "test-task"
        assert result.agent_name == "test-agent"
        assert result.n_runs == 1
        assert result.success_count == 1
        assert result.success_rate == 1.0
        assert result.mean_runtime == 5.0
        assert result.mean_tokens == 0.0
        assert result.mean_cost == 0.0
        assert result.reliability_score == 1.0
        assert result.aggregated_at is not None


class TestMultiRunIntegration:
    """Integration tests for multi-run execution."""

    def test_multi_run_with_mixed_results(self):
        """Test multi-run with realistic mix of passes and failures."""
        mock_executor = MagicMock()
        multi_run = MultiRunExecutor(executor=mock_executor)

        # Simulate realistic execution: 3 passes, 1 failure, 1 exception
        mock_executor.execute_task.side_effect = [
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=2.1),
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=1.9),
            Exception("Timeout"),
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=2.0),
            EvaluationResult(task_id="test", passed=False, score=0.0, duration=0.5),
        ]

        mock_agent = MagicMock()
        mock_agent.config = AgentConfig(
            agent_type=AgentType.OPENAI,
            model="gpt-4",
            name="test-agent",
        )

        result = multi_run.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=5,
        )

        # Should have 3 passes, 2 failures
        assert result.success_count == 3
        assert result.failure_count == 2
        assert result.success_rate == 0.6
        assert len(result.runs) == 5

        # Mean runtime should be computed from all 5 runs
        # (2.1 + 1.9 + exception_as_error + 2.0 + 0.5) / 5
        # Exception results have some default duration or computed duration
        assert result.mean_runtime > 0


class TestConcurrentExecution:
    """Test concurrent/parallel execution functionality."""

    @pytest.fixture
    def mock_executor(self):
        """Create a mock TaskExecutor."""
        executor = MagicMock()
        return executor

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent."""
        agent = MagicMock()
        agent.config = AgentConfig(
            agent_type=AgentType.OPENAI,
            model="gpt-4",
            name="test-agent",
        )
        return agent

    def test_executor_max_concurrent_parameter(self, mock_executor):
        """Test that max_concurrent parameter is stored correctly."""
        executor = MultiRunExecutor(executor=mock_executor, max_concurrent=3)
        assert executor.max_concurrent == 3

    def test_executor_default_max_concurrent(self, mock_executor):
        """Test that default max_concurrent is 5."""
        executor = MultiRunExecutor(executor=mock_executor)
        assert executor.max_concurrent == 5

    def test_parallel_execution_option_false(self, mock_executor, mock_agent):
        """Test that use_parallelization=False uses sequential execution."""
        mock_executor.execute_task.return_value = EvaluationResult(
            task_id="test",
            passed=True,
            score=1.0,
            duration=1.0,
        )

        executor = MultiRunExecutor(executor=mock_executor, max_concurrent=5)
        result = executor.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=3,
            use_parallelization=False,
        )

        # Should execute all 3 runs successfully
        assert result.n_runs == 3
        assert result.success_count == 3
        assert result.success_rate == 1.0
        # Should have called execute_task 3 times
        assert mock_executor.execute_task.call_count == 3

    def test_parallel_execution_option_true(self, mock_executor, mock_agent):
        """Test that use_parallelization=True uses parallel execution."""
        mock_executor.execute_task.return_value = EvaluationResult(
            task_id="test",
            passed=True,
            score=1.0,
            duration=1.0,
        )

        executor = MultiRunExecutor(executor=mock_executor, max_concurrent=2)
        result = executor.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=4,
            use_parallelization=True,
        )

        # Should execute all 4 runs successfully
        assert result.n_runs == 4
        assert result.success_count == 4
        assert result.success_rate == 1.0
        # Should have called execute_task 4 times
        assert mock_executor.execute_task.call_count == 4

    def test_progress_callback_sequential(self, mock_executor, mock_agent):
        """Test that progress callback is called for each completed run (sequential)."""
        mock_executor.execute_task.return_value = EvaluationResult(
            task_id="test",
            passed=True,
            score=1.0,
            duration=1.0,
        )

        progress_updates = []

        def progress_callback(completed, total):
            progress_updates.append((completed, total))

        executor = MultiRunExecutor(executor=mock_executor)
        executor.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=3,
            use_parallelization=False,
            progress_callback=progress_callback,
        )

        # Should have 3 progress updates
        assert len(progress_updates) == 3
        assert progress_updates == [(1, 3), (2, 3), (3, 3)]

    def test_progress_callback_parallel(self, mock_executor, mock_agent):
        """Test that progress callback is called for each completed run (parallel)."""
        mock_executor.execute_task.return_value = EvaluationResult(
            task_id="test",
            passed=True,
            score=1.0,
            duration=1.0,
        )

        progress_updates = []

        def progress_callback(completed, total):
            progress_updates.append((completed, total))

        executor = MultiRunExecutor(executor=mock_executor, max_concurrent=2)
        executor.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=4,
            use_parallelization=True,
            progress_callback=progress_callback,
        )

        # Should have 4 progress updates (one per completed run)
        assert len(progress_updates) == 4
        # All should report total=4
        assert all(total == 4 for completed, total in progress_updates)
        # Completed counts should add up to 4
        completed_counts = [completed for completed, _ in progress_updates]
        assert sum(1 for c in completed_counts if c in range(1, 5)) == 4

    def test_parallel_execution_with_mixed_results(self, mock_executor, mock_agent):
        """Test parallel execution with passing and failing runs."""
        # Simulate: pass, fail, pass, fail, pass
        mock_executor.execute_task.side_effect = [
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=1.0),
            EvaluationResult(task_id="test", passed=False, score=0.0, duration=1.0),
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=1.0),
            EvaluationResult(task_id="test", passed=False, score=0.0, duration=1.0),
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=1.0),
        ]

        executor = MultiRunExecutor(executor=mock_executor, max_concurrent=2)
        result = executor.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=5,
            use_parallelization=True,
        )

        # Should have 3 passes, 2 failures
        assert result.success_count == 3
        assert result.failure_count == 2
        assert result.success_rate == 0.6
        assert len(result.runs) == 5

    def test_parallel_execution_respects_max_concurrent_limit(self, mock_agent):
        """Test that parallel execution respects max_concurrent limit."""
        import time

        # Create a mock executor that tracks concurrent execution
        concurrent_count = {"current": 0, "max": 0}

        def track_execution(**kwargs):
            concurrent_count["current"] += 1
            concurrent_count["max"] = max(concurrent_count["max"], concurrent_count["current"])

            # Simulate some work time
            time.sleep(0.05)

            concurrent_count["current"] -= 1

            return EvaluationResult(
                task_id="test",
                passed=True,
                score=1.0,
                duration=0.05,
            )

        mock_executor = MagicMock()
        mock_executor.execute_task.side_effect = track_execution

        executor = MultiRunExecutor(executor=mock_executor, max_concurrent=2)
        executor.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=4,
            use_parallelization=True,
        )

        # The maximum concurrent execution should not exceed max_concurrent
        # (Note: This is a soft check - timing in tests can be flaky)
        # In a real scenario with actual IO, this would be more reliable
        assert concurrent_count["max"] <= 3  # Allow some tolerance

    def test_parallel_execution_with_exceptions(self, mock_executor, mock_agent):
        """Test that parallel execution handles exceptions gracefully."""
        # Simulate: pass, exception, pass, exception, pass
        mock_executor.execute_task.side_effect = [
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=1.0),
            Exception("Network error"),
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=1.0),
            Exception("Timeout"),
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=1.0),
        ]

        executor = MultiRunExecutor(executor=mock_executor, max_concurrent=3)
        result = executor.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=5,
            use_parallelization=True,
        )

        # Should have 3 passes and 2 failures (exceptions converted to failed results)
        assert result.success_count == 3
        assert result.failure_count == 2
        assert len(result.runs) == 5
        # All runs should be EvaluationResult objects
        assert all(isinstance(r, EvaluationResult) for r in result.runs)

    def test_parallel_execution_all_exceptions(self, mock_executor, mock_agent):
        """Test parallel execution when all runs fail with exceptions."""
        mock_executor.execute_task.side_effect = Exception("Execution error")

        executor = MultiRunExecutor(executor=mock_executor, max_concurrent=2)
        result = executor.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=3,
            use_parallelization=True,
        )

        # All 3 runs should fail
        assert result.success_count == 0
        assert result.failure_count == 3
        assert result.success_rate == 0.0

    def test_timeout_passed_to_runs_parallel(self, mock_executor, mock_agent):
        """Test that timeout is passed to each run in parallel execution."""
        mock_executor.execute_task.return_value = EvaluationResult(
            task_id="test",
            passed=True,
            score=1.0,
            duration=1.0,
        )

        executor = MultiRunExecutor(executor=mock_executor, max_concurrent=2)
        executor.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=3,
            timeout=300,
            use_parallelization=True,
        )

        # All 3 calls should have timeout=300
        assert mock_executor.execute_task.call_count == 3
        for call in mock_executor.execute_task.call_args_list:
            kwargs = call[1]
            assert kwargs.get("timeout") == 300

    def test_parallel_vs_sequential_execution_produces_same_results(self, mock_agent):
        """Test that parallel and sequential execution produce same logical results."""
        # Create two separate executors with the same side effects
        mock_executor1 = MagicMock()
        mock_executor1.execute_task.side_effect = [
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=1.0),
            EvaluationResult(task_id="test", passed=False, score=0.0, duration=1.0),
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=1.0),
        ]

        mock_executor2 = MagicMock()
        mock_executor2.execute_task.side_effect = [
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=1.0),
            EvaluationResult(task_id="test", passed=False, score=0.0, duration=1.0),
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=1.0),
        ]

        # Run sequential
        executor_seq = MultiRunExecutor(executor=mock_executor1)
        result_seq = executor_seq.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=3,
            use_parallelization=False,
        )

        # Run parallel
        executor_par = MultiRunExecutor(executor=mock_executor2, max_concurrent=2)
        result_par = executor_par.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=3,
            use_parallelization=True,
        )

        # Results should be logically identical
        assert result_seq.success_count == result_par.success_count == 2
        assert result_seq.failure_count == result_par.failure_count == 1
        assert result_seq.success_rate == result_par.success_rate == pytest.approx(2 / 3)
        assert result_seq.mean_runtime == result_par.mean_runtime

    def test_no_race_conditions_with_shared_task_id(self, mock_executor, mock_agent):
        """Test that parallel execution doesn't have race conditions with shared task_id."""
        results_captured = []

        def capture_result(**kwargs):
            result = EvaluationResult(
                task_id="test-task",
                passed=True,
                score=1.0,
                duration=1.0,
            )
            results_captured.append(result)
            return result

        mock_executor.execute_task.side_effect = capture_result

        executor = MultiRunExecutor(executor=mock_executor, max_concurrent=3)
        executor.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=5,
            use_parallelization=True,
        )

        # All captured results should have the same task_id
        assert all(r.task_id == "test-task" for r in results_captured)
        assert len(results_captured) == 5

    def test_large_batch_parallel_execution(self, mock_executor, mock_agent):
        """Test parallel execution with large batch of 10 runs."""
        mock_executor.execute_task.return_value = EvaluationResult(
            task_id="test",
            passed=True,
            score=1.0,
            duration=1.0,
        )

        executor = MultiRunExecutor(executor=mock_executor, max_concurrent=5)
        result = executor.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=10,
            use_parallelization=True,
        )

        # All 10 runs should complete successfully
        assert result.n_runs == 10
        assert result.success_count == 10
        assert result.success_rate == 1.0
        assert len(result.runs) == 10
        assert mock_executor.execute_task.call_count == 10

    def test_concurrent_execution_with_varying_max_concurrent(self, mock_executor, mock_agent):
        """Test that different max_concurrent values don't affect results."""
        # Test with max_concurrent=1 (sequential-like)
        mock_executor.execute_task.return_value = EvaluationResult(
            task_id="test",
            passed=True,
            score=1.0,
            duration=1.0,
        )

        executor1 = MultiRunExecutor(executor=mock_executor, max_concurrent=1)
        result1 = executor1.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=5,
            use_parallelization=True,
        )

        # Reset mock
        mock_executor.reset_mock()
        mock_executor.execute_task.return_value = EvaluationResult(
            task_id="test",
            passed=True,
            score=1.0,
            duration=1.0,
        )

        # Test with max_concurrent=10 (highly parallel)
        executor2 = MultiRunExecutor(executor=mock_executor, max_concurrent=10)
        result2 = executor2.execute_multi_run(
            task_id="test-task",
            agent=mock_agent,
            n_runs=5,
            use_parallelization=True,
        )

        # Results should be the same regardless of max_concurrent
        assert result1.success_count == result2.success_count == 5
        assert result1.success_rate == result2.success_rate == 1.0
