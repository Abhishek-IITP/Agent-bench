"""
Unit tests for the Reliability Scoring Engine.

Tests all aspects of reliability score computation:
- Score bounds (0-100)
- Test scenarios from design spec
- Component breakdown
- Edge cases
- Error handling

Formula:
    reliability_score = success_component + consistency_component
    success_component = success_rate * 0.7 * 100
    consistency_component = consistency * success_rate * 0.3 * 100
    consistency = 1 - min(variance / 0.5, 1.0)

Key insight: Consistency bonus is scaled by success_rate, so it only applies
to the successful portion of runs. All-failures get 0 score regardless of variance.
"""

import pytest

from runner.models import EvaluationResult
from runner.scoring import (
    compute_reliability_score,
    compute_reliability_score_with_breakdown,
)

# Test Fixtures


@pytest.fixture
def single_pass_result():
    """Single passing evaluation result."""
    return EvaluationResult(
        task_id="test-task",
        passed=True,
        score=1.0,
        duration=5.0,
    )


@pytest.fixture
def single_fail_result():
    """Single failing evaluation result."""
    return EvaluationResult(
        task_id="test-task",
        passed=False,
        score=0.0,
        duration=5.0,
    )


def create_results(task_id: str, n_pass: int, n_fail: int = 0) -> list[EvaluationResult]:
    """Helper to create evaluation results with specified pass/fail counts."""
    results = []

    # Create passing results
    for i in range(n_pass):
        results.append(
            EvaluationResult(
                task_id=task_id,
                passed=True,
                score=1.0,
                duration=5.0,
            )
        )

    # Create failing results
    for i in range(n_fail):
        results.append(
            EvaluationResult(
                task_id=task_id,
                passed=False,
                score=0.0,
                duration=5.0,
            )
        )

    return results


# Core Tests - Design Spec Scenarios


class TestDesignScenarios:
    """Test the four design spec scenarios."""

    def test_100_percent_success_zero_variance(self):
        """
        Scenario 1: 100% success, 0 variance → 100

        success = 1.0, variance = 0
        success_component = 1.0 * 0.7 * 100 = 70
        consistency = 1 - (0 / 0.5) = 1.0
        consistency_component = 1.0 * 1.0 * 0.3 * 100 = 30
        Expected: 70 + 30 = 100
        """
        results = create_results("test", n_pass=10)
        score = compute_reliability_score(results)
        assert score == 100.0, f"Expected 100.0, got {score}"

    def test_50_percent_success_zero_variance(self):
        """
        Scenario 2: 50% success, 0 variance → 35

        At p=0.5: success = 0.5, variance = sqrt(0.5 * 0.5) = 0.5 (max variance)
        success_component = 0.5 * 0.7 * 100 = 35
        consistency = 1 - (0.5 / 0.5) = 0
        consistency_component = 0 * 0.5 * 0.3 * 100 = 0
        Expected: 35 + 0 = 35
        """
        results = create_results("test", n_pass=5, n_fail=5)
        score = compute_reliability_score(results)
        assert score == 35.0, f"Expected 35.0, got {score}"

    def test_100_percent_success_high_variance(self):
        """
        Scenario 3: 100% success (no variance possible)

        All runs pass → variance = 0, not possible to have high variance.
        This scenario name is misleading for binary outcomes.
        For 100% success: score = 100 regardless.
        """
        results = create_results("test", n_pass=10)
        score = compute_reliability_score(results)
        assert score == 100.0

    def test_50_percent_success_high_variance(self):
        """
        Scenario 4: 50% success, high variance (at max)

        At p=0.5: variance = 0.5 (maximum for binary)
        success_component = 0.5 * 0.7 * 100 = 35
        consistency = 1 - (0.5 / 0.5) = 0
        consistency_component = 0 * 0.5 * 0.3 * 100 = 0
        Expected: 35
        """
        results = create_results("test", n_pass=5, n_fail=5)
        score = compute_reliability_score(results)
        assert score == 35.0


# Score Bounds Tests


class TestScoreBounds:
    """Test that reliability score always stays in [0, 100]."""

    def test_minimum_score_all_failures(self):
        """All failures should give score of 0."""
        results = create_results("test", n_pass=0, n_fail=10)
        score = compute_reliability_score(results)
        assert score == 0.0

    def test_maximum_score_all_successes(self):
        """All successes should give score of 100."""
        results = create_results("test", n_pass=20)
        score = compute_reliability_score(results)
        assert score == 100.0

    def test_mixed_results_in_bounds(self):
        """Any mix of pass/fail should stay in [0, 100]."""
        for n_pass in range(0, 11):
            results = create_results("test", n_pass=n_pass, n_fail=10 - n_pass)
            score = compute_reliability_score(results)
            assert (
                0.0 <= score <= 100.0
            ), f"Score {score} out of bounds for {n_pass} passes, {10-n_pass} fails"


# Component Breakdown Tests


class TestComponentBreakdown:
    """Test detailed breakdown of score components."""

    def test_breakdown_100_percent_success(self):
        """100% success should max out both components."""
        results = create_results("test", n_pass=10)
        breakdown = compute_reliability_score_with_breakdown(results)

        assert breakdown.total_score == 100.0
        assert breakdown.success_component == 70.0
        assert breakdown.consistency_component == 30.0
        assert breakdown.success_rate == 1.0
        assert breakdown.variance == 0.0
        assert breakdown.n_runs == 10

    def test_breakdown_50_percent_success(self):
        """50% success should give specific component values."""
        results = create_results("test", n_pass=5, n_fail=5)
        breakdown = compute_reliability_score_with_breakdown(results)

        assert breakdown.total_score == 35.0
        assert breakdown.success_component == 35.0
        assert breakdown.consistency_component == 0.0  # Max variance = 0 consistency
        assert breakdown.success_rate == 0.5
        assert breakdown.variance == 0.5  # Max variance for binary
        assert breakdown.n_runs == 10

    def test_breakdown_0_percent_success(self):
        """0% success should give 0 score regardless of consistency."""
        results = create_results("test", n_pass=0, n_fail=10)
        breakdown = compute_reliability_score_with_breakdown(results)

        assert breakdown.total_score == 0.0
        assert breakdown.success_component == 0.0
        assert breakdown.consistency_component == 0.0  # No bonus for consistent failure
        assert breakdown.success_rate == 0.0
        assert breakdown.n_runs == 10

    def test_breakdown_1_pass_1_fail(self):
        """Single pass and fail should have 50% success."""
        results = create_results("test", n_pass=1, n_fail=1)
        breakdown = compute_reliability_score_with_breakdown(results)

        assert breakdown.success_rate == 0.5
        assert breakdown.success_component == 35.0
        assert breakdown.total_score == 35.0


# Edge Cases


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_pass(self):
        """Single passing result should score 100."""
        results = create_results("test", n_pass=1)
        score = compute_reliability_score(results)
        assert score == 100.0

    def test_single_fail(self):
        """Single failing result should score 0."""
        results = create_results("test", n_pass=0, n_fail=1)
        score = compute_reliability_score(results)
        assert score == 0.0

    def test_many_runs_all_pass(self):
        """Many passing runs should still score 100."""
        results = create_results("test", n_pass=100)
        score = compute_reliability_score(results)
        assert score == 100.0

    def test_many_runs_all_fail(self):
        """Many failing runs should still score 0."""
        results = create_results("test", n_pass=0, n_fail=100)
        score = compute_reliability_score(results)
        assert score == 0.0

    def test_large_even_split(self):
        """Large even split of pass/fail."""
        results = create_results("test", n_pass=50, n_fail=50)
        score = compute_reliability_score(results)
        assert score == 35.0


# Custom Weights Tests


class TestCustomWeights:
    """Test with custom weight configurations."""

    def test_equal_weights(self):
        """Test with equal weights (0.5, 0.5)."""
        results = create_results("test", n_pass=10)
        weights = {"success": 0.5, "consistency": 0.5}
        score = compute_reliability_score(results, weights=weights)
        # success: 1.0 * 0.5 * 100 = 50
        # consistency: 1.0 * 1.0 * 0.5 * 100 = 50
        # total = 100
        assert score == 100.0

    def test_success_only_weight(self):
        """Test with success weight = 1.0, consistency = 0."""
        results = create_results("test", n_pass=5, n_fail=5)
        weights = {"success": 1.0, "consistency": 0.0}
        score = compute_reliability_score(results, weights=weights)
        # 0.5 * 1.0 * 100 + 0 = 50
        assert score == 50.0

    def test_consistency_only_weight(self):
        """Test with consistency weight = 1.0, success = 0."""
        results = create_results("test", n_pass=5, n_fail=5)
        weights = {"success": 0.0, "consistency": 1.0}
        score = compute_reliability_score(results, weights=weights)
        # 0 + 0 * 0.5 * 1.0 * 100 = 0
        assert score == 0.0

    def test_custom_weights_sum_to_one(self):
        """Verify that custom weights must sum to 1.0."""
        results = create_results("test", n_pass=5, n_fail=5)

        # Valid: sum = 1.0
        weights_valid = {"success": 0.6, "consistency": 0.4}
        score = compute_reliability_score(results, weights=weights_valid)
        assert 0.0 <= score <= 100.0

    def test_invalid_weights_sum(self):
        """Verify error when weights don't sum to 1.0."""
        results = create_results("test", n_pass=5, n_fail=5)

        # Invalid: sum = 1.5
        weights_invalid = {"success": 0.8, "consistency": 0.7}
        with pytest.raises(ValueError, match="weights must sum to 1.0"):
            compute_reliability_score(results, weights=weights_invalid)


# Error Handling


class TestErrorHandling:
    """Test error handling and validation."""

    def test_empty_results_raises_error(self):
        """Empty results list should raise ValueError."""
        with pytest.raises(ValueError, match="empty results list"):
            compute_reliability_score([])

    def test_empty_results_breakdown_raises_error(self):
        """Empty results list should raise ValueError in breakdown version."""
        with pytest.raises(ValueError, match="empty results list"):
            compute_reliability_score_with_breakdown([])

    def test_invalid_weights_type_raises_error(self):
        """Non-dict weights should raise ValueError."""
        results = create_results("test", n_pass=5)

        with pytest.raises(ValueError, match="weights must be a dict"):
            compute_reliability_score(results, weights="invalid")

    def test_missing_weight_keys_raises_error(self):
        """Missing 'success' or 'consistency' key should raise ValueError."""
        results = create_results("test", n_pass=5)

        weights_missing_success = {"consistency": 0.5}
        with pytest.raises(ValueError, match="'success' and 'consistency'"):
            compute_reliability_score(results, weights=weights_missing_success)

        weights_missing_consistency = {"success": 0.5}
        with pytest.raises(ValueError, match="'success' and 'consistency'"):
            compute_reliability_score(results, weights=weights_missing_consistency)


# Consistency Tests


class TestConsistency:
    """Test scoring consistency across multiple calls."""

    def test_same_results_same_score(self):
        """Same results should always produce same score."""
        results = create_results("test", n_pass=7, n_fail=3)

        score1 = compute_reliability_score(results)
        score2 = compute_reliability_score(results)
        score3 = compute_reliability_score(results)

        assert score1 == score2 == score3

    def test_different_order_same_score(self):
        """Score should be independent of result order."""
        results_a = create_results("test", n_pass=7, n_fail=3)
        results_b = list(reversed(results_a))

        score_a = compute_reliability_score(results_a)
        score_b = compute_reliability_score(results_b)

        assert score_a == score_b


# Boundary Condition Tests


class TestBoundarConditions:
    """Test scores at various boundary conditions."""

    def test_scores_form_expected_pattern(self):
        """Scores should increase monotonically with success rate."""
        scores = []
        for n_pass in range(0, 11):  # 0 to 10 passes out of 10
            results = create_results("test", n_pass=n_pass, n_fail=10 - n_pass)
            score = compute_reliability_score(results)
            scores.append(score)

        # Scores should be monotonically non-decreasing
        for i in range(len(scores) - 1):
            assert scores[i] <= scores[i + 1], f"Scores not monotonic: {scores[i]} > {scores[i+1]}"

    def test_score_progression(self):
        """Verify expected score progression.

        Formula for p successes out of 10:
            success_rate = p / 10
            variance = sqrt((p/10) * (1 - p/10))
            normalized_var = min(variance / 0.5, 1.0)
            consistency = 1 - normalized_var
            success_component = (p/10) * 0.7 * 100
            consistency_component = consistency * (p/10) * 0.3 * 100
            score = success_component + consistency_component
        """
        # Calculate expected scores programmatically
        expected_scores = {}
        for n_pass in range(0, 11):
            sr = n_pass / 10.0
            # variance for binary
            var = (sr * (1 - sr)) ** 0.5
            # normalized variance (max is 0.5)
            norm_var = min(var / 0.5, 1.0)
            consistency = 1.0 - norm_var
            # components
            success_comp = sr * 0.7 * 100
            consistency_comp = consistency * sr * 0.3 * 100
            expected_scores[n_pass] = success_comp + consistency_comp

        for n_pass, expected in expected_scores.items():
            results = create_results("test", n_pass=n_pass, n_fail=10 - n_pass)
            actual = compute_reliability_score(results)
            assert (
                abs(actual - expected) < 0.001
            ), f"n_pass={n_pass}: expected {expected}, got {actual}"
