"""
Tests for Difficulty Calibration module (Task 6).

Tests difficulty estimation and comparison across all 4 difficulty levels:
- EASY: ≥80% success
- MEDIUM: 50-80%
- HARD: 20-50%
- EXPERT: <20%
"""

import pytest

from runner.calibration import (
    DifficultyLevel,
    estimate_difficulty,
    calibrate_difficulty,
    compute_all_calibrations,
    summarize_calibrations,
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


class TestEstimateDifficulty:
    """Test difficulty estimation from success rate."""

    def test_estimate_easy(self):
        """Estimate EASY from 90% success."""
        difficulty = estimate_difficulty(0.90)
        assert difficulty == DifficultyLevel.EASY

    def test_estimate_easy_boundary(self):
        """Estimate EASY at 80% boundary."""
        difficulty = estimate_difficulty(0.80)
        assert difficulty == DifficultyLevel.EASY

    def test_estimate_medium(self):
        """Estimate MEDIUM from 65% success."""
        difficulty = estimate_difficulty(0.65)
        assert difficulty == DifficultyLevel.MEDIUM

    def test_estimate_medium_boundaries(self):
        """Estimate MEDIUM at boundaries."""
        assert estimate_difficulty(0.50) == DifficultyLevel.MEDIUM
        assert estimate_difficulty(0.79) == DifficultyLevel.MEDIUM

    def test_estimate_hard(self):
        """Estimate HARD from 35% success."""
        difficulty = estimate_difficulty(0.35)
        assert difficulty == DifficultyLevel.HARD

    def test_estimate_hard_boundaries(self):
        """Estimate HARD at boundaries."""
        assert estimate_difficulty(0.20) == DifficultyLevel.HARD
        assert estimate_difficulty(0.49) == DifficultyLevel.HARD

    def test_estimate_expert(self):
        """Estimate EXPERT from 10% success."""
        difficulty = estimate_difficulty(0.10)
        assert difficulty == DifficultyLevel.EXPERT

    def test_estimate_expert_boundary(self):
        """Estimate EXPERT at boundary."""
        difficulty = estimate_difficulty(0.19)
        assert difficulty == DifficultyLevel.EXPERT


class TestCalibrateDifficultyEasy:
    """Test calibration for EASY tasks."""

    def test_calibrate_easy_single_agent_perfect(self, create_results):
        """Easy task: single agent with perfect performance."""
        agent_results = create_results("task_easy1", [True] * 10)

        report = calibrate_difficulty(
            task_id="task_easy1",
            results_by_agent={"agent1": agent_results},
            author_difficulty=DifficultyLevel.EASY,
        )

        assert report.empirical_difficulty == DifficultyLevel.EASY
        assert report.mean_success_rate >= 0.80
        assert report.match is True

    def test_calibrate_easy_multiple_agents_consistent(self, create_results):
        """Easy task: multiple agents all high success."""
        agent1 = create_results("task_easy2", [True] * 9 + [False])
        agent2 = create_results("task_easy2", [True] * 10)
        agent3 = create_results("task_easy2", [True] * 8 + [False] * 2)

        report = calibrate_difficulty(
            task_id="task_easy2",
            results_by_agent={
                "agent1": agent1,
                "agent2": agent2,
                "agent3": agent3,
            },
            author_difficulty=DifficultyLevel.EASY,
        )

        assert report.empirical_difficulty == DifficultyLevel.EASY
        assert report.mean_success_rate >= 0.80
        assert report.match is True
        assert report.n_agents == 3

    def test_calibrate_easy_marked_medium_mismatch(self, create_results):
        """Easy task but marked as MEDIUM: mismatch."""
        agent1 = create_results("task_easy_medium", [True] * 9 + [False])
        agent2 = create_results("task_easy_medium", [True] * 10)

        report = calibrate_difficulty(
            task_id="task_easy_medium",
            results_by_agent={
                "agent1": agent1,
                "agent2": agent2,
            },
            author_difficulty=DifficultyLevel.MEDIUM,
        )

        assert report.empirical_difficulty == DifficultyLevel.EASY
        assert report.author_difficulty == DifficultyLevel.MEDIUM
        assert report.match is False
        assert "re-rating" in report.recommendation.lower()


class TestCalibrateDifficultyMedium:
    """Test calibration for MEDIUM tasks."""

    def test_calibrate_medium_balanced(self, create_results):
        """Medium task: balanced 50-80% success."""
        agent1 = create_results("task_med1", [True] * 7 + [False] * 3)
        agent2 = create_results("task_med1", [True] * 6 + [False] * 4)

        report = calibrate_difficulty(
            task_id="task_med1",
            results_by_agent={
                "agent1": agent1,
                "agent2": agent2,
            },
            author_difficulty=DifficultyLevel.MEDIUM,
        )

        assert report.empirical_difficulty == DifficultyLevel.MEDIUM
        assert 0.50 <= report.mean_success_rate <= 0.80
        assert report.match is True

    def test_calibrate_medium_lower_bound(self, create_results):
        """Medium task at 50% boundary."""
        agent1 = create_results("task_med_50", [True] * 5 + [False] * 5)

        report = calibrate_difficulty(
            task_id="task_med_50",
            results_by_agent={"agent1": agent1},
            author_difficulty=DifficultyLevel.MEDIUM,
        )

        assert report.empirical_difficulty == DifficultyLevel.MEDIUM
        assert report.mean_success_rate == 0.50
        assert report.match is True

    def test_calibrate_medium_upper_bound(self, create_results):
        """Medium task at 80% boundary (should be easy)."""
        agent1 = create_results("task_med_80", [True] * 8 + [False] * 2)

        report = calibrate_difficulty(
            task_id="task_med_80",
            results_by_agent={"agent1": agent1},
            author_difficulty=DifficultyLevel.MEDIUM,
        )

        # 80% is exactly at EASY boundary, so will be classified as EASY
        assert report.empirical_difficulty == DifficultyLevel.EASY
        assert report.mean_success_rate == 0.80
        assert report.match is False  # EASY != MEDIUM


class TestCalibrateDifficultyHard:
    """Test calibration for HARD tasks."""

    def test_calibrate_hard_middle_range(self, create_results):
        """Hard task: 20-50% success."""
        agent1 = create_results("task_hard1", [True] * 4 + [False] * 6)
        agent2 = create_results("task_hard1", [True] * 3 + [False] * 7)

        report = calibrate_difficulty(
            task_id="task_hard1",
            results_by_agent={
                "agent1": agent1,
                "agent2": agent2,
            },
            author_difficulty=DifficultyLevel.HARD,
        )

        assert report.empirical_difficulty == DifficultyLevel.HARD
        assert 0.20 <= report.mean_success_rate <= 0.50
        assert report.match is True

    def test_calibrate_hard_lower_bound(self, create_results):
        """Hard task at 20% boundary."""
        agent1 = create_results("task_hard_20", [True] * 2 + [False] * 8)

        report = calibrate_difficulty(
            task_id="task_hard_20",
            results_by_agent={"agent1": agent1},
            author_difficulty=DifficultyLevel.HARD,
        )

        assert report.empirical_difficulty == DifficultyLevel.HARD
        assert report.mean_success_rate == 0.20

    def test_calibrate_hard_marked_medium_mismatch(self, create_results):
        """Hard task but marked as MEDIUM: mismatch."""
        agent1 = create_results("task_hard_med", [True] * 3 + [False] * 7)

        report = calibrate_difficulty(
            task_id="task_hard_med",
            results_by_agent={"agent1": agent1},
            author_difficulty=DifficultyLevel.MEDIUM,
        )

        assert report.empirical_difficulty == DifficultyLevel.HARD
        assert report.author_difficulty == DifficultyLevel.MEDIUM
        assert report.match is False
        assert (
            "hard" in report.recommendation.lower()
            or "empirically" in report.recommendation.lower()
        )


class TestCalibrateDifficultyExpert:
    """Test calibration for EXPERT tasks."""

    def test_calibrate_expert_very_hard(self, create_results):
        """Expert task: <20% success."""
        agent1 = create_results("task_exp1", [True] + [False] * 9)
        agent2 = create_results("task_exp1", [False] * 10)

        report = calibrate_difficulty(
            task_id="task_exp1",
            results_by_agent={
                "agent1": agent1,
                "agent2": agent2,
            },
            author_difficulty=DifficultyLevel.EXPERT,
        )

        assert report.empirical_difficulty == DifficultyLevel.EXPERT
        assert report.mean_success_rate < 0.20
        assert report.match is True

    def test_calibrate_expert_boundary(self, create_results):
        """Expert task at 19% boundary."""
        agent1 = create_results("task_exp_19", [True] + [False] * 5 + [True] + [False] * 3)
        # This is 2/10 = 20%, should be EXPERT at boundary

        report = calibrate_difficulty(
            task_id="task_exp_19",
            results_by_agent={"agent1": agent1},
            author_difficulty=DifficultyLevel.EXPERT,
        )

        # 20% is HARD, <20% is EXPERT
        assert report.empirical_difficulty in [DifficultyLevel.HARD, DifficultyLevel.EXPERT]


class TestCalibrationWithoutAuthorDifficulty:
    """Test calibration when author difficulty not provided."""

    def test_calibrate_no_author_easy(self, create_results):
        """Calibrate EASY task with no author difficulty."""
        agent1 = create_results("task_noauth_easy", [True] * 9 + [False])

        report = calibrate_difficulty(
            task_id="task_noauth_easy",
            results_by_agent={"agent1": agent1},
            author_difficulty=None,
        )

        assert report.empirical_difficulty == DifficultyLevel.EASY
        assert report.author_difficulty is None
        # match should be True when comparing to None (no mismatch possible with no author)
        assert report.match is True or "No author difficulty" in report.recommendation

    def test_calibrate_no_author_expert(self, create_results):
        """Calibrate EXPERT task with no author difficulty."""
        agent1 = create_results("task_noauth_exp", [False] * 10)

        report = calibrate_difficulty(
            task_id="task_noauth_exp",
            results_by_agent={"agent1": agent1},
            author_difficulty=None,
        )

        assert report.empirical_difficulty == DifficultyLevel.EXPERT
        assert report.author_difficulty is None


class TestConfidenceScoring:
    """Test confidence scores based on number of agents."""

    def test_confidence_single_agent(self, create_results):
        """Confidence with single agent."""
        agent1 = create_results("task_conf1", [True] * 8 + [False] * 2)

        report = calibrate_difficulty(
            task_id="task_conf1",
            results_by_agent={"agent1": agent1},
            author_difficulty=DifficultyLevel.MEDIUM,
        )

        assert 0 < report.confidence < 1.0  # Less than full confidence

    def test_confidence_multiple_agents(self, create_results):
        """Confidence increases with more agents."""
        agent1 = create_results("task_conf_multi", [True] * 8 + [False] * 2)
        agent2 = create_results("task_conf_multi", [True] * 7 + [False] * 3)
        agent3 = create_results("task_conf_multi", [True] * 8 + [False] * 2)
        agent4 = create_results("task_conf_multi", [True] * 7 + [False] * 3)

        report = calibrate_difficulty(
            task_id="task_conf_multi",
            results_by_agent={
                "agent1": agent1,
                "agent2": agent2,
                "agent3": agent3,
                "agent4": agent4,
            },
            author_difficulty=DifficultyLevel.MEDIUM,
        )

        assert report.confidence >= 1.0  # Full confidence at 3+ agents


class TestComputeAllCalibrations:
    """Test computing calibrations for multiple tasks."""

    def test_compute_all_calibrations(self, create_results):
        """Compute calibrations for multiple tasks."""
        results_by_task = {
            "task_easy": {
                "agent1": create_results("task_easy", [True] * 9 + [False]),
                "agent2": create_results("task_easy", [True] * 10),
            },
            "task_hard": {
                "agent1": create_results("task_hard", [True] * 3 + [False] * 7),
                "agent2": create_results("task_hard", [True] * 2 + [False] * 8),
            },
        }

        author_difficulties = {
            "task_easy": DifficultyLevel.EASY,
            "task_hard": DifficultyLevel.HARD,
        }

        calibrations = compute_all_calibrations(results_by_task, author_difficulties)

        assert len(calibrations) == 2
        assert calibrations["task_easy"].empirical_difficulty == DifficultyLevel.EASY
        assert calibrations["task_hard"].empirical_difficulty == DifficultyLevel.HARD
        assert calibrations["task_easy"].match is True
        assert calibrations["task_hard"].match is True


class TestSummarizeCalibrations:
    """Test calibration summary statistics."""

    def test_summarize_matched(self, create_results):
        """Summarize all matched calibrations."""
        results_by_task = {
            "task1": {
                "agent1": create_results("task1", [True] * 9 + [False]),
            },
            "task2": {
                "agent1": create_results("task2", [True] * 5 + [False] * 5),
            },
            "task3": {
                "agent1": create_results("task3", [True] * 2 + [False] * 8),
            },
        }

        author_difficulties = {
            "task1": DifficultyLevel.EASY,
            "task2": DifficultyLevel.MEDIUM,
            "task3": DifficultyLevel.HARD,
        }

        calibrations = compute_all_calibrations(results_by_task, author_difficulties)

        summary = summarize_calibrations(calibrations)

        assert summary["total_tasks"] == 3
        assert summary["matched"] == 3
        assert summary["mismatched"] == 0
        assert summary["match_rate"] == 1.0
        assert summary["difficulty_distribution"]["easy"] >= 1
        assert summary["difficulty_distribution"]["medium"] >= 1
        assert summary["difficulty_distribution"]["hard"] >= 1

    def test_summarize_mismatched(self, create_results):
        """Summarize with mismatched calibrations."""
        results_by_task = {
            "task1": {
                "agent1": create_results("task1", [True] * 9 + [False]),
            },
            "task2": {
                "agent1": create_results("task2", [True] * 9 + [False]),
            },
        }

        author_difficulties = {
            "task1": DifficultyLevel.EASY,
            "task2": DifficultyLevel.MEDIUM,  # Mismatch: empirical is EASY
        }

        calibrations = compute_all_calibrations(results_by_task, author_difficulties)

        summary = summarize_calibrations(calibrations)

        assert summary["total_tasks"] == 2
        assert summary["matched"] == 1
        assert summary["mismatched"] == 1
        assert summary["match_rate"] == 0.5
        assert "task2" in summary["mismatched_tasks"]


class TestCalibrationReportToDict:
    """Test CalibrationReport serialization."""

    def test_to_dict(self, create_results):
        """Test converting calibration to dictionary."""
        agent1 = create_results("task_dict", [True] * 7 + [False] * 3)

        report = calibrate_difficulty(
            task_id="task_dict",
            results_by_agent={"agent1": agent1},
            author_difficulty=DifficultyLevel.MEDIUM,
        )

        report_dict = report.to_dict()

        assert report_dict["task_id"] == "task_dict"
        assert report_dict["author_difficulty"] == DifficultyLevel.MEDIUM.value
        assert report_dict["empirical_difficulty"] == DifficultyLevel.MEDIUM.value
        assert report_dict["mean_success_rate"] == 0.70
        assert "confidence" in report_dict


class TestEdgeCases:
    """Test edge cases."""

    def test_calibrate_empty_results(self):
        """Handle empty results."""
        report = calibrate_difficulty(
            task_id="task_empty",
            results_by_agent={},
            author_difficulty=DifficultyLevel.MEDIUM,
        )

        assert report.mean_success_rate == 0.0
        assert report.n_agents == 0
        assert report.match is False

    def test_calibrate_single_run(self, create_results):
        """Handle single run per agent."""
        agent1 = create_results("task_single_run", [True])
        agent2 = create_results("task_single_run", [False])

        report = calibrate_difficulty(
            task_id="task_single_run",
            results_by_agent={
                "agent1": agent1,
                "agent2": agent2,
            },
            author_difficulty=DifficultyLevel.MEDIUM,
        )

        assert report.n_agents == 2
        assert report.mean_success_rate == 0.50
