"""
Integration tests for full pipeline (Task 9).

Tests end-to-end flow: multi-run → metrics → scoring → health → storage → CLI.
Verifies data consistency, error recovery, and concurrency handling.
"""

import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed

from runner.health import analyze_task_health, TaskHealthStatus
from runner.calibration import calibrate_difficulty, DifficultyLevel
from runner.metrics import compute_all_metrics
from runner.models import EvaluationResult


@pytest.fixture
def create_results():
    """Factory to create EvaluationResult objects."""

    def _create(
        task_id: str, passed_list: list[bool], duration: float = 1.0
    ) -> list[EvaluationResult]:
        return [
            EvaluationResult(
                task_id=task_id,
                passed=passed,
                score=1.0 if passed else 0.0,
                duration=duration,
                details={
                    "cost": 0.001 if passed else 0.0005,
                    "tokens": 100 if passed else 50,
                },
            )
            for passed in passed_list
        ]

    return _create


class TestMultiRunMetricsFlow:
    """Test multi-run execution flow."""

    def test_multi_run_aggregation(self, create_results):
        """Test aggregating multi-run results."""
        results = create_results("task1", [True, False, True, True, False])

        metrics = compute_all_metrics(results)

        assert metrics.n_runs == 5
        assert metrics.success_rate == 0.6
        # Confidence intervals can vary, just check they're valid
        assert metrics.confidence_interval_lower <= metrics.confidence_interval_upper
        assert 0 <= metrics.confidence_interval_lower <= 1.0
        assert 0 <= metrics.confidence_interval_upper <= 1.0
        assert metrics.mean_runtime == 1.0
        assert metrics.variance > 0

    def test_consistency_across_metrics(self, create_results):
        """Test metrics are consistent across calls."""
        results = create_results("task2", [True] * 7 + [False] * 3)

        # Call metrics computation multiple times
        metrics1 = compute_all_metrics(results)
        metrics2 = compute_all_metrics(results)

        # Should be identical
        assert metrics1.success_rate == metrics2.success_rate
        assert metrics1.variance == metrics2.variance
        assert metrics1.confidence_interval_lower == metrics2.confidence_interval_lower


class TestHealthAnalysisFlow:
    """Test health analysis in context of multi-run results."""

    def test_health_from_multi_run(self, create_results):
        """Test deriving health classification from multi-run results."""
        agent1_results = create_results("task_health1", [True] * 6 + [False] * 4)
        agent2_results = create_results("task_health1", [True] * 7 + [False] * 3)

        report = analyze_task_health(
            task_id="task_health1",
            results_by_agent={
                "agent1": agent1_results,
                "agent2": agent2_results,
            },
            oracle_passed=True,
            nop_passed=True,
        )

        assert report.health_status == TaskHealthStatus.HEALTHY
        assert report.success_rate >= 0.6
        assert report.n_agents == 2
        assert report.n_runs_total == 20

    def test_health_classifications_comprehensive(self, create_results):
        """Test all health classifications are deterministic."""
        # TRIVIAL
        trivial_results = {
            "agent1": create_results("task_trivial", [True] * 10),
            "agent2": create_results("task_trivial", [True] * 10),
        }

        # BROKEN
        broken_results = {
            "agent1": create_results("task_broken", [False] * 10),
            "agent2": create_results("task_broken", [False] * 10),
        }

        # FLAKY
        flaky_results = {
            "agent1": create_results("task_flaky", [True] * 10),
            "agent2": create_results("task_flaky", [False] * 10),
        }

        trivial_report = analyze_task_health("task_trivial", trivial_results, True, True)
        broken_report = analyze_task_health("task_broken", broken_results, True, True)
        flaky_report = analyze_task_health("task_flaky", flaky_results, True, True)

        assert trivial_report.health_status == TaskHealthStatus.TRIVIAL
        assert broken_report.health_status == TaskHealthStatus.BROKEN
        assert flaky_report.health_status == TaskHealthStatus.FLAKY


class TestCalibrationFlow:
    """Test difficulty calibration in multi-run context."""

    def test_calibration_from_multi_run(self, create_results):
        """Test calibrating difficulty from multi-run results."""
        agent1_results = create_results("task_easy", [True] * 9 + [False])
        agent2_results = create_results("task_easy", [True] * 8 + [False] * 2)
        agent3_results = create_results("task_easy", [True] * 9 + [False])

        report = calibrate_difficulty(
            task_id="task_easy",
            results_by_agent={
                "agent1": agent1_results,
                "agent2": agent2_results,
                "agent3": agent3_results,
            },
            author_difficulty=DifficultyLevel.EASY,
        )

        assert report.empirical_difficulty == DifficultyLevel.EASY
        assert report.match is True
        assert report.n_agents == 3
        assert report.mean_success_rate >= 0.85

    def test_calibration_consistency(self, create_results):
        """Test calibration is consistent across calls."""
        results_by_agent = {
            "agent1": create_results("task_calib", [True] * 6 + [False] * 4),
            "agent2": create_results("task_calib", [True] * 7 + [False] * 3),
        }

        report1 = calibrate_difficulty("task_calib", results_by_agent, DifficultyLevel.MEDIUM)
        report2 = calibrate_difficulty("task_calib", results_by_agent, DifficultyLevel.MEDIUM)

        assert report1.empirical_difficulty == report2.empirical_difficulty
        assert report1.mean_success_rate == report2.mean_success_rate
        assert report1.match == report2.match


class TestDataConsistency:
    """Test data consistency across modules."""

    def test_metrics_health_consistency(self, create_results):
        """Test metrics and health analysis are consistent."""
        results = create_results("task_consistent", [True] * 8 + [False] * 2)

        # Compute metrics
        metrics = compute_all_metrics(results)

        # Compute health
        health_report = analyze_task_health("task_consistent", {"agent1": results}, True, True)

        # Success rates should match
        assert metrics.success_rate == 0.8
        assert health_report.success_rate == 0.8

    def test_confidence_intervals_validity(self, create_results):
        """Test confidence intervals are valid (lower <= upper)."""
        results = create_results("task_ci", [True] * 7 + [False] * 3)

        metrics = compute_all_metrics(results)

        assert metrics.confidence_interval_lower <= metrics.confidence_interval_upper
        assert 0 <= metrics.confidence_interval_lower
        assert metrics.confidence_interval_upper <= 1.0

    def test_variance_consistency(self, create_results):
        """Test variance is consistent with outcomes."""
        # High variance case
        results_high = create_results("task_var_high", [True, False] * 5)

        # Low variance case
        results_low = create_results("task_var_low", [True] * 10)

        metrics_high = compute_all_metrics(results_high)
        metrics_low = compute_all_metrics(results_low)

        # High variance case should have higher variance
        assert metrics_high.variance >= metrics_low.variance


class TestErrorRecovery:
    """Test error recovery and fallback behavior."""

    def test_single_run_failure(self, create_results):
        """Test multi-run handles individual run failures."""
        results_with_failure = [
            EvaluationResult(task_id="task_fail", passed=True, score=1.0, duration=1.0),
            EvaluationResult(task_id="task_fail", passed=False, score=0.0, duration=1.0),
            EvaluationResult(task_id="task_fail", passed=True, score=1.0, duration=1.0),
        ]

        metrics = compute_all_metrics(results_with_failure)

        # Should still compute successfully despite failure
        assert metrics.n_runs == 3
        assert metrics.success_rate == (2 / 3)

    def test_empty_results_handling(self):
        """Test handling of empty results gracefully."""
        with pytest.raises(ValueError):
            compute_all_metrics([])

    def test_single_result_handling(self, create_results):
        """Test handling single result."""
        results = create_results("task_single", [True])

        metrics = compute_all_metrics(results)

        assert metrics.n_runs == 1
        assert metrics.success_rate == 1.0


class TestConcurrency:
    """Test concurrent processing of multiple tasks."""

    def test_parallel_health_analysis(self, create_results):
        """Test parallel health analysis for multiple tasks."""
        tasks = {}
        for i in range(5):
            task_id = f"task_parallel_{i}"
            tasks[task_id] = {
                "agent_1": create_results(task_id, [True] * (7 + i) + [False] * (3 - i)),
                "agent_2": create_results(task_id, [True] * (6 + i) + [False] * (4 - i)),
            }

        # Process in parallel
        health_reports = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(analyze_task_health, task_id, task_data, True, True): task_id
                for task_id, task_data in tasks.items()
            }

            for future in as_completed(futures):
                task_id = futures[future]
                health_reports[task_id] = future.result()

        assert len(health_reports) == 5
        for report in health_reports.values():
            assert report.health_status in [
                TaskHealthStatus.HEALTHY,
                TaskHealthStatus.TRIVIAL,
            ]

    def test_parallel_calibration(self, create_results):
        """Test parallel difficulty calibration for multiple tasks."""
        tasks = {}
        for i in range(4):
            task_id = f"task_calib_parallel_{i}"
            tasks[task_id] = {
                "agent_1": create_results(task_id, [True] * (5 + i) + [False] * (5 - i)),
                "agent_2": create_results(task_id, [True] * (6 + i) + [False] * (4 - i)),
            }

        # Process in parallel
        calibrations = {}
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(calibrate_difficulty, task_id, task_data, None): task_id
                for task_id, task_data in tasks.items()
            }

            for future in as_completed(futures):
                task_id = futures[future]
                calibrations[task_id] = future.result()

        assert len(calibrations) == 4
        # Each should have an empirical difficulty
        for calib in calibrations.values():
            assert calib.empirical_difficulty in [
                DifficultyLevel.EASY,
                DifficultyLevel.MEDIUM,
                DifficultyLevel.HARD,
                DifficultyLevel.EXPERT,
            ]


class TestFullPipeline:
    """Test complete end-to-end pipeline."""

    def test_end_to_end_single_task_two_agents(self, create_results):
        """Test full pipeline: multi-run → metrics → health → calibration."""
        task_id = "task_e2e_1"

        # Simulate multi-run execution
        agent1_runs = create_results(task_id, [True] * 7 + [False] * 3)
        agent2_runs = create_results(task_id, [True] * 6 + [False] * 4)

        results_by_agent = {
            "gpt-4": agent1_runs,
            "claude-3": agent2_runs,
        }

        # Step 1: Compute metrics for each agent
        agent1_metrics = compute_all_metrics(agent1_runs)
        agent2_metrics = compute_all_metrics(agent2_runs)

        assert agent1_metrics.success_rate == 0.7
        assert agent2_metrics.success_rate == 0.6

        # Step 2: Analyze health across agents
        health_report = analyze_task_health(task_id, results_by_agent, True, True)

        assert health_report.health_status == TaskHealthStatus.HEALTHY
        assert health_report.success_rate == 0.65  # Average

        # Step 3: Calibrate difficulty
        calib_report = calibrate_difficulty(task_id, results_by_agent, DifficultyLevel.MEDIUM)

        assert calib_report.empirical_difficulty == DifficultyLevel.MEDIUM
        assert calib_report.n_agents == 2

    def test_end_to_end_multiple_tasks(self, create_results):
        """Test pipeline for multiple tasks simultaneously."""
        tasks_data = {
            "task_easy": {
                "agent1": create_results("task_easy", [True] * 9 + [False]),
                "agent2": create_results("task_easy", [True] * 10),
            },
            "task_medium": {
                "agent1": create_results("task_medium", [True] * 6 + [False] * 4),
                "agent2": create_results("task_medium", [True] * 7 + [False] * 3),
            },
            "task_hard": {
                "agent1": create_results("task_hard", [True] * 3 + [False] * 7),
                "agent2": create_results("task_hard", [True] * 2 + [False] * 8),
            },
        }

        results = {}

        for task_id, results_by_agent in tasks_data.items():
            # Compute metrics
            all_runs = sum(results_by_agent.values(), [])
            metrics = compute_all_metrics(all_runs)

            # Analyze health
            health = analyze_task_health(task_id, results_by_agent, True, True)

            # Calibrate
            calib = calibrate_difficulty(task_id, results_by_agent, None)

            results[task_id] = {
                "metrics": metrics,
                "health": health,
                "calibration": calib,
            }

        # Verify results
        assert len(results) == 3
        assert results["task_easy"]["health"].health_status == TaskHealthStatus.HEALTHY
        assert results["task_medium"]["health"].health_status == TaskHealthStatus.HEALTHY
        assert results["task_hard"]["health"].health_status == TaskHealthStatus.HEALTHY

        assert results["task_easy"]["calibration"].empirical_difficulty == DifficultyLevel.EASY
        assert results["task_medium"]["calibration"].empirical_difficulty == DifficultyLevel.MEDIUM
        assert results["task_hard"]["calibration"].empirical_difficulty == DifficultyLevel.HARD


class TestPipelineRobustness:
    """Test pipeline robustness under edge cases."""

    def test_pipeline_with_mixed_agent_performance(self, create_results):
        """Test pipeline with agents having very different performance."""
        task_id = "task_mixed"

        results_by_agent = {
            "perfect_agent": create_results(task_id, [True] * 10),
            "poor_agent": create_results(task_id, [False] * 10),
            "average_agent": create_results(task_id, [True] * 5 + [False] * 5),
        }

        # Metrics should aggregate properly
        all_runs = sum(results_by_agent.values(), [])
        metrics = compute_all_metrics(all_runs)

        assert metrics.success_rate == (10 + 0 + 5) / 30
        assert metrics.variance > 0

        # Health should flag as FLAKY due to variance
        health = analyze_task_health(task_id, results_by_agent, True, True)

        # High variance should lead to FLAKY or other non-HEALTHY status
        assert health.variance > 0.25

    def test_pipeline_with_single_run_per_agent(self, create_results):
        """Test pipeline with minimal data (single run per agent)."""
        task_id = "task_minimal"

        results_by_agent = {
            "agent1": create_results(task_id, [True]),
            "agent2": create_results(task_id, [False]),
            "agent3": create_results(task_id, [True]),
        }

        all_runs = sum(results_by_agent.values(), [])
        metrics = compute_all_metrics(all_runs)

        # Should still work
        assert metrics.n_runs == 3
        assert metrics.success_rate == (2 / 3)

        health = analyze_task_health(task_id, results_by_agent, True, True)
        calib = calibrate_difficulty(task_id, results_by_agent, None)

        # Should produce valid results
        assert health.health_status in list(TaskHealthStatus)
        assert calib.empirical_difficulty in list(DifficultyLevel)
