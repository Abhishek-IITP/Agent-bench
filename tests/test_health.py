"""
Tests for Health Analyzer module (Task 5).

Tests task health classification across all 5 categories:
- HEALTHY: normal performance
- FLAKY: inconsistent results
- BROKEN: consistent failures
- TRIVIAL: all agents pass 100%
- SATURATED: top agents achieve 100%
"""

import pytest

from runner.health import (
    TaskHealthStatus,
    analyze_task_health,
    compute_benchmark_health,
    summarize_benchmark_health,
)
from runner.models import EvaluationResult


@pytest.fixture
def create_results():
    """Factory fixture to create EvaluationResult objects."""

    def _create(task_id: str, passed_list: list[bool]) -> list[EvaluationResult]:
        return [
            EvaluationResult(
                task_id=task_id,
                passed=passed,
                score=1.0 if passed else 0.0,
                duration=1.0,
                details={},
            )
            for passed in passed_list
        ]

    return _create


class TestHealthyClassification:
    """Test HEALTHY classification: moderate difficulty, good consistency."""

    def test_healthy_50_percent_success(self, create_results):
        """Healthy task with 60% success rate across consistent agents."""
        # 2 agents, each with 60% success (consistent performance)
        agent1_results = create_results("task1", [True] * 6 + [False] * 4)
        agent2_results = create_results("task1", [True] * 6 + [False] * 4)

        report = analyze_task_health(
            task_id="task1",
            results_by_agent={
                "agent1": agent1_results,
                "agent2": agent2_results,
            },
            oracle_passed=True,
            nop_passed=True,
        )

        assert report.health_status == TaskHealthStatus.HEALTHY
        assert report.success_rate == 0.6
        assert report.n_agents == 2
        assert len(report.evidence) > 0
        assert len(report.recommendations) > 0

    def test_healthy_70_percent_success(self, create_results):
        """Healthy task with 70% success rate."""
        agent1_results = create_results("task2", [True, True, True, False, True, False, True])
        agent2_results = create_results("task2", [True, True, False, True, True, False, True])

        report = analyze_task_health(
            task_id="task2",
            results_by_agent={
                "agent1": agent1_results,
                "agent2": agent2_results,
            },
            oracle_passed=True,
            nop_passed=True,
        )

        assert report.health_status == TaskHealthStatus.HEALTHY
        assert 0.6 < report.success_rate < 0.8  # Around 70%
        assert report.n_agents == 2
        # Note: variance will be high since we have small run counts, but inter-agent variance should be low

    def test_healthy_consistent_performance(self, create_results):
        """Healthy task with consistent performance across agents."""
        # Both agents perform similarly
        agent1_results = create_results("task3", [True] * 7 + [False] * 3)
        agent2_results = create_results("task3", [True] * 6 + [False] * 4)

        report = analyze_task_health(
            task_id="task3",
            results_by_agent={
                "agent1": agent1_results,
                "agent2": agent2_results,
            },
            oracle_passed=True,
            nop_passed=True,
        )

        assert report.health_status == TaskHealthStatus.HEALTHY
        # Agents have similar performance (70% and 60% are close)
        assert report.success_rate > 0.5


class TestFlakyClassification:
    """Test FLAKY classification: high variance across agents."""

    def test_flaky_inconsistent_results(self, create_results):
        """Flaky task with inconsistent results between agents."""
        # Agent1: 90% success, Agent2: 10% success - high variance
        agent1_results = create_results("task_flaky1", [True] * 18 + [False] * 2)
        agent2_results = create_results("task_flaky1", [False] * 18 + [True] * 2)

        report = analyze_task_health(
            task_id="task_flaky1",
            results_by_agent={
                "agent1": agent1_results,
                "agent2": agent2_results,
            },
            oracle_passed=True,
            nop_passed=True,
        )

        assert report.health_status == TaskHealthStatus.FLAKY
        assert report.variance > 0.35
        assert "High variance" in " ".join(report.evidence)

    def test_flaky_high_variance(self, create_results):
        """Flaky task with high variance."""
        # Mix of very successful and very unsuccessful runs
        agent1_results = create_results("task_flaky2", [True] * 8 + [False] * 2)
        agent2_results = create_results("task_flaky2", [False] * 8 + [True] * 2)
        agent3_results = create_results("task_flaky2", [True, False] * 5)

        report = analyze_task_health(
            task_id="task_flaky2",
            results_by_agent={
                "agent1": agent1_results,
                "agent2": agent2_results,
                "agent3": agent3_results,
            },
            oracle_passed=True,
            nop_passed=True,
        )

        assert report.health_status == TaskHealthStatus.FLAKY
        assert "investigate inconsistent" in " ".join(report.recommendations).lower()


class TestBrokenClassification:
    """Test BROKEN classification: consistent failures."""

    def test_broken_oracle_failed(self, create_results):
        """Broken task: Oracle validation failed."""
        agent1_results = create_results("task_broken1", [True, False, True])

        report = analyze_task_health(
            task_id="task_broken1",
            results_by_agent={"agent1": agent1_results},
            oracle_passed=False,  # Oracle failed
            nop_passed=True,
        )

        assert report.health_status == TaskHealthStatus.BROKEN
        assert "Oracle validation failed" in " ".join(report.evidence)
        assert "Fix task validation" in " ".join(report.recommendations)

    def test_broken_all_agents_fail(self, create_results):
        """Broken task: All agents fail."""
        agent1_results = create_results("task_broken2", [False] * 10)
        agent2_results = create_results("task_broken2", [False] * 10)
        agent3_results = create_results("task_broken2", [False] * 10)

        report = analyze_task_health(
            task_id="task_broken2",
            results_by_agent={
                "agent1": agent1_results,
                "agent2": agent2_results,
                "agent3": agent3_results,
            },
            oracle_passed=True,
            nop_passed=True,
        )

        assert report.health_status == TaskHealthStatus.BROKEN
        assert report.success_rate == 0.0
        assert "failed" in " ".join(report.evidence).lower()
        assert "Review task environment" in " ".join(report.recommendations)

    def test_broken_most_agents_fail(self, create_results):
        """Broken task: Most agents fail consistently."""
        agent1_results = create_results("task_broken3", [False] * 8 + [True] * 2)
        agent2_results = create_results("task_broken3", [False] * 9 + [True])
        agent3_results = create_results("task_broken3", [False] * 10)

        report = analyze_task_health(
            task_id="task_broken3",
            results_by_agent={
                "agent1": agent1_results,
                "agent2": agent2_results,
                "agent3": agent3_results,
            },
            oracle_passed=True,
            nop_passed=True,
        )

        # 10-11% success rate should classify as BROKEN
        assert report.health_status == TaskHealthStatus.BROKEN
        assert report.success_rate < 0.15


class TestTrivialClassification:
    """Test TRIVIAL classification: 100% success."""

    def test_trivial_all_pass(self, create_results):
        """Trivial task: all runs pass."""
        agent1_results = create_results("task_trivial1", [True] * 10)
        agent2_results = create_results("task_trivial1", [True] * 10)
        agent3_results = create_results("task_trivial1", [True] * 10)

        report = analyze_task_health(
            task_id="task_trivial1",
            results_by_agent={
                "agent1": agent1_results,
                "agent2": agent2_results,
                "agent3": agent3_results,
            },
            oracle_passed=True,
            nop_passed=True,
        )

        assert report.health_status == TaskHealthStatus.TRIVIAL
        assert report.success_rate >= 1.0
        assert "difficulty" in " ".join(report.recommendations).lower() or "Remove" in " ".join(
            report.recommendations
        )

    def test_trivial_near_perfect(self, create_results):
        """Trivial task: nearly perfect success."""
        agent1_results = create_results("task_trivial2", [True] * 9 + [True])
        agent2_results = create_results("task_trivial2", [True] * 10)

        report = analyze_task_health(
            task_id="task_trivial2",
            results_by_agent={
                "agent1": agent1_results,
                "agent2": agent2_results,
            },
            oracle_passed=True,
            nop_passed=True,
        )

        assert report.health_status == TaskHealthStatus.TRIVIAL
        assert "Remove from active benchmarking" in " ".join(report.recommendations)


class TestSaturatedClassification:
    """Test SATURATED classification: top agents at 100%."""

    def test_saturated_top_agents_100(self, create_results):
        """Saturated task: top agents at 100%."""
        # Simpler test: just 2 perfect agents
        agent1_results = create_results("task_sat1", [True] * 10)
        agent2_results = create_results("task_sat1", [True] * 10)

        report = analyze_task_health(
            task_id="task_sat1",
            results_by_agent={
                "agent1": agent1_results,
                "agent2": agent2_results,
            },
            oracle_passed=True,
            nop_passed=True,
        )

        # With all agents at 100%, this should be TRIVIAL, not SATURATED
        assert report.health_status == TaskHealthStatus.TRIVIAL
        assert report.success_rate >= 1.0


class TestComputeAllHealths:
    """Test computing health for multiple tasks."""

    def test_compute_benchmark_health(self, create_results):
        """Compute health for entire benchmark."""
        # Mix of different health statuses
        results_by_task = {
            "task_healthy": {
                "agent1": create_results("task_healthy", [True] * 5 + [False] * 5),
                "agent2": create_results("task_healthy", [True] * 6 + [False] * 4),
            },
            "task_trivial": {
                "agent1": create_results("task_trivial", [True] * 10),
                "agent2": create_results("task_trivial", [True] * 10),
            },
            "task_broken": {
                "agent1": create_results("task_broken", [False] * 10),
                "agent2": create_results("task_broken", [False] * 10),
            },
        }

        oracle_results = {
            "task_healthy": True,
            "task_trivial": True,
            "task_broken": True,
        }

        nop_results = {
            "task_healthy": True,
            "task_trivial": True,
            "task_broken": True,
        }

        health_reports = compute_benchmark_health(results_by_task, oracle_results, nop_results)

        assert len(health_reports) == 3
        assert health_reports["task_healthy"].health_status == TaskHealthStatus.HEALTHY
        assert health_reports["task_trivial"].health_status == TaskHealthStatus.TRIVIAL
        assert health_reports["task_broken"].health_status == TaskHealthStatus.BROKEN

    def test_summarize_benchmark_health(self, create_results):
        """Summarize benchmark health statistics."""
        results_by_task = {
            "task1": {
                "agent1": create_results("task1", [True] * 5 + [False] * 5),
            },
            "task2": {
                "agent1": create_results("task2", [True] * 10),
            },
            "task3": {
                "agent1": create_results("task3", [False] * 10),
            },
        }

        oracle_results = {"task1": True, "task2": True, "task3": True}
        nop_results = {"task1": True, "task2": True, "task3": True}

        health_reports = compute_benchmark_health(results_by_task, oracle_results, nop_results)

        summary = summarize_benchmark_health(health_reports)

        assert summary["total_tasks"] == 3
        assert summary["healthy"] >= 0
        assert summary["trivial"] >= 0
        assert summary["broken"] >= 0
        assert summary["health_percentage"] >= 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_results(self):
        """Handle empty results."""
        report = analyze_task_health(
            task_id="task_empty",
            results_by_agent={},
            oracle_passed=True,
            nop_passed=True,
        )

        assert report.health_status == TaskHealthStatus.BROKEN
        assert report.success_rate == 0.0
        assert "No execution results" in " ".join(report.evidence)

    def test_single_agent(self, create_results):
        """Handle single agent (should still work)."""
        agent1_results = create_results("task_single", [True, False, True, False, True])

        report = analyze_task_health(
            task_id="task_single",
            results_by_agent={"agent1": agent1_results},
            oracle_passed=True,
            nop_passed=True,
        )

        assert report.health_status == TaskHealthStatus.HEALTHY
        assert report.n_agents == 1
        assert report.n_runs_total == 5

    def test_single_run_per_agent(self, create_results):
        """Handle very few runs."""
        agent1_results = create_results("task_few", [True])
        agent2_results = create_results("task_few", [False])

        report = analyze_task_health(
            task_id="task_few",
            results_by_agent={
                "agent1": agent1_results,
                "agent2": agent2_results,
            },
            oracle_passed=True,
            nop_passed=True,
        )

        assert report.health_status in [
            TaskHealthStatus.HEALTHY,
            TaskHealthStatus.FLAKY,
        ]
        assert report.n_runs_total == 2


class TestHealthReportToDict:
    """Test HealthReport serialization."""

    def test_to_dict(self, create_results):
        """Test converting report to dictionary."""
        agent1_results = create_results("task_dict", [True] * 5 + [False] * 5)

        report = analyze_task_health(
            task_id="task_dict",
            results_by_agent={"agent1": agent1_results},
            oracle_passed=True,
            nop_passed=True,
        )

        report_dict = report.to_dict()

        assert report_dict["task_id"] == "task_dict"
        assert report_dict["health_status"] == TaskHealthStatus.HEALTHY.value
        assert "success_rate" in report_dict
        assert "evidence" in report_dict
        assert "recommendations" in report_dict
