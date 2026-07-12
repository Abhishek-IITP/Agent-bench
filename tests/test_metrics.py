"""
Unit tests for MetricsEngine (runner/metrics.py).

Tests all statistical computations including:
- Success rate calculation
- Wilson score confidence intervals (validated against scipy)
- Variance computation
- Mean runtime and cost
- Token statistics
- Edge cases
"""

import math

import pytest
from scipy import stats as sp_stats

from runner.metrics import (
    success_rate,
    confidence_interval,
    variance,
    mean_runtime,
    mean_cost,
    token_stats,
    compute_all_metrics,
    TokenStats,
    MetricsResult,
)
from runner.models import EvaluationResult

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def single_pass_result():
    """Single passing result."""
    return EvaluationResult(
        task_id="test-task",
        passed=True,
        score=1.0,
        duration=10.5,
        details={"cost": 0.01, "tokens": 150},
    )


@pytest.fixture
def single_fail_result():
    """Single failing result."""
    return EvaluationResult(
        task_id="test-task",
        passed=False,
        score=0.0,
        duration=5.2,
        details={"cost": 0.005, "tokens": 75},
    )


@pytest.fixture
def mixed_results_5():
    """5 results: 3 pass, 2 fail."""
    return [
        EvaluationResult(
            task_id="test",
            passed=True,
            score=1.0,
            duration=10.0,
            details={"cost": 0.01, "tokens": 100},
        ),
        EvaluationResult(
            task_id="test",
            passed=True,
            score=1.0,
            duration=11.0,
            details={"cost": 0.01, "tokens": 110},
        ),
        EvaluationResult(
            task_id="test",
            passed=False,
            score=0.0,
            duration=5.0,
            details={"cost": 0.005, "tokens": 50},
        ),
        EvaluationResult(
            task_id="test",
            passed=True,
            score=1.0,
            duration=10.5,
            details={"cost": 0.01, "tokens": 105},
        ),
        EvaluationResult(
            task_id="test",
            passed=False,
            score=0.0,
            duration=4.5,
            details={"cost": 0.004, "tokens": 45},
        ),
    ]


@pytest.fixture
def all_pass_10():
    """10 results: all passing."""
    return [
        EvaluationResult(
            task_id="test",
            passed=True,
            score=1.0,
            duration=10.0 + i,
            details={"cost": 0.01, "tokens": 100 + i * 5},
        )
        for i in range(10)
    ]


@pytest.fixture
def all_fail_10():
    """10 results: all failing."""
    return [
        EvaluationResult(
            task_id="test",
            passed=False,
            score=0.0,
            duration=5.0 + i * 0.5,
            details={"cost": 0.005, "tokens": 50 + i * 2},
        )
        for i in range(10)
    ]


# ============================================================================
# Tests: success_rate()
# ============================================================================


class TestSuccessRate:
    """Tests for success_rate() function."""

    def test_single_pass(self, single_pass_result):
        """Single passing result should give 1.0."""
        sr = success_rate([single_pass_result])
        assert sr == 1.0

    def test_single_fail(self, single_fail_result):
        """Single failing result should give 0.0."""
        sr = success_rate([single_fail_result])
        assert sr == 0.0

    def test_mixed_5(self, mixed_results_5):
        """3 pass, 2 fail = 0.6 success rate."""
        sr = success_rate(mixed_results_5)
        assert sr == pytest.approx(0.6)

    def test_all_pass(self, all_pass_10):
        """All passing = 1.0."""
        sr = success_rate(all_pass_10)
        assert sr == 1.0

    def test_all_fail(self, all_fail_10):
        """All failing = 0.0."""
        sr = success_rate(all_fail_10)
        assert sr == 0.0

    def test_empty_raises(self):
        """Empty list should raise ValueError."""
        with pytest.raises(ValueError):
            success_rate([])


# ============================================================================
# Tests: confidence_interval()
# ============================================================================


class TestConfidenceInterval:
    """Tests for confidence_interval() using Wilson score formula."""

    def test_single_pass_wilson(self, single_pass_result):
        """Single pass: Wilson CI should be conservative but bounded."""
        lower, upper = confidence_interval([single_pass_result])
        assert 0 <= lower <= upper <= 1
        assert upper == 1.0
        # With n=1, p=1, Wilson score is conservative: lower ≈ 0.207
        assert lower > 0

    def test_single_fail_wilson(self, single_fail_result):
        """Single fail: Wilson CI should be conservative but bounded."""
        lower, upper = confidence_interval([single_fail_result])
        assert 0 <= lower <= upper <= 1
        assert lower == 0.0
        # With n=1, p=0, Wilson score is conservative: upper ≈ 0.793
        assert upper < 1.0

    def test_mixed_5_wilson(self, mixed_results_5):
        """Mixed results: CI should contain 0.6."""
        lower, upper = confidence_interval(mixed_results_5)
        assert 0 <= lower <= upper <= 1
        assert lower < 0.6 < upper

    def test_all_pass_100_wilson(self, all_pass_10):
        """All pass: upper should be very close to 1.0."""
        lower, upper = confidence_interval(all_pass_10)
        assert 0 <= lower <= upper <= 1
        assert upper > 0.999  # Very close to 1.0
        # With p=1, lower should be fairly high (>0.7 for n=10)
        assert lower > 0.7

    def test_all_fail_100_wilson(self, all_fail_10):
        """All fail: lower should be 0.0."""
        lower, upper = confidence_interval(all_fail_10)
        assert 0 <= lower <= upper <= 1
        assert lower == 0.0
        # With p=0, upper should be fairly low (<0.3 for n=10)
        assert upper < 0.3

    def test_confidence_levels(self, mixed_results_5):
        """Higher confidence should give wider interval."""
        lower_90, upper_90 = confidence_interval(mixed_results_5, confidence=0.90)
        lower_95, upper_95 = confidence_interval(mixed_results_5, confidence=0.95)
        lower_99, upper_99 = confidence_interval(mixed_results_5, confidence=0.99)

        # 99% CI should be wider than 95% which should be wider than 90%
        width_90 = upper_90 - lower_90
        width_95 = upper_95 - lower_95
        width_99 = upper_99 - lower_99

        assert width_90 < width_95 < width_99

    def test_vs_scipy_binomial(self):
        """Validate against scipy.stats.binom for medium sample size."""
        # 6 passes out of 10
        results = [
            EvaluationResult(task_id="test", passed=(i < 6), score=float(i < 6), duration=10.0)
            for i in range(10)
        ]

        lower, upper = confidence_interval(results, confidence=0.95)

        # scipy.stats.binom for validation
        n = 10
        k = 6
        p = k / n
        # scipy gives CI in terms of parameter p
        ci_scipy = sp_stats.binom.interval(0.95, n, p)
        # Convert back to proportions
        ci_scipy_prop = (ci_scipy[0] / n, ci_scipy[1] / n)

        # Wilson score and scipy's method may differ, especially at extremes
        # Check they're in the same ballpark (within 0.1)
        assert abs(lower - ci_scipy_prop[0]) < 0.1
        assert abs(upper - ci_scipy_prop[1]) < 0.1

    def test_invalid_confidence(self, mixed_results_5):
        """Invalid confidence level should raise."""
        with pytest.raises(ValueError):
            confidence_interval(mixed_results_5, confidence=0.0)
        with pytest.raises(ValueError):
            confidence_interval(mixed_results_5, confidence=1.0)
        with pytest.raises(ValueError):
            confidence_interval(mixed_results_5, confidence=1.5)

    def test_empty_raises(self):
        """Empty list should raise ValueError."""
        with pytest.raises(ValueError):
            confidence_interval([])


# ============================================================================
# Tests: variance()
# ============================================================================


class TestVariance:
    """Tests for variance() function."""

    def test_single_pass_variance(self, single_pass_result):
        """Single pass (p=1.0) should give variance=0."""
        var = variance([single_pass_result])
        assert var == pytest.approx(0.0)

    def test_single_fail_variance(self, single_fail_result):
        """Single fail (p=0.0) should give variance=0."""
        var = variance([single_fail_result])
        assert var == pytest.approx(0.0)

    def test_50_50_variance(self, mixed_results_5):
        """For binary outcomes, max variance is at p=0.5: sqrt(0.5*0.5)=0.5."""
        # 5 results: 3 pass (p=0.6), variance = sqrt(0.6*0.4) = sqrt(0.24) ≈ 0.49
        var = variance(mixed_results_5)
        expected = math.sqrt(0.6 * 0.4)
        assert var == pytest.approx(expected)

    def test_all_pass_variance(self, all_pass_10):
        """All pass (p=1.0) should give variance=0."""
        var = variance(all_pass_10)
        assert var == pytest.approx(0.0)

    def test_all_fail_variance(self, all_fail_10):
        """All fail (p=0.0) should give variance=0."""
        var = variance(all_fail_10)
        assert var == pytest.approx(0.0)

    def test_empty_raises(self):
        """Empty list should raise ValueError."""
        with pytest.raises(ValueError):
            variance([])


# ============================================================================
# Tests: mean_runtime()
# ============================================================================


class TestMeanRuntime:
    """Tests for mean_runtime() function."""

    def test_single_result(self, single_pass_result):
        """Single result: mean should be that result's duration."""
        mrt = mean_runtime([single_pass_result])
        assert mrt == pytest.approx(10.5)

    def test_mixed_5(self, mixed_results_5):
        """Check mean calculation for 5 results."""
        # Durations: 10.0, 11.0, 5.0, 10.5, 4.5
        # Mean: (10.0 + 11.0 + 5.0 + 10.5 + 4.5) / 5 = 41.0 / 5 = 8.2
        mrt = mean_runtime(mixed_results_5)
        assert mrt == pytest.approx(8.2)

    def test_all_pass(self, all_pass_10):
        """All pass: mean of 10.0, 11.0, ..., 19.0."""
        # Mean should be 14.5
        mrt = mean_runtime(all_pass_10)
        assert mrt == pytest.approx(14.5)

    def test_empty_raises(self):
        """Empty list should raise ValueError."""
        with pytest.raises(ValueError):
            mean_runtime([])


# ============================================================================
# Tests: mean_cost()
# ============================================================================


class TestMeanCost:
    """Tests for mean_cost() function."""

    def test_single_result(self, single_pass_result):
        """Single result: mean should be that result's cost."""
        mc = mean_cost([single_pass_result])
        assert mc == pytest.approx(0.01)

    def test_mixed_5(self, mixed_results_5):
        """Check mean cost calculation."""
        # Costs: 0.01, 0.01, 0.005, 0.01, 0.004
        # Mean: (0.01 + 0.01 + 0.005 + 0.01 + 0.004) / 5 = 0.039 / 5 = 0.0078
        mc = mean_cost(mixed_results_5)
        assert mc == pytest.approx(0.0078)

    def test_no_cost_data(self):
        """Results with no cost data should return 0.0."""
        results = [
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=10.0, details={}),
            EvaluationResult(task_id="test", passed=False, score=0.0, duration=5.0, details={}),
        ]
        mc = mean_cost(results)
        assert mc == pytest.approx(0.0)

    def test_empty_returns_zero(self):
        """Empty list should return 0.0."""
        mc = mean_cost([])
        assert mc == 0.0


# ============================================================================
# Tests: token_stats()
# ============================================================================


class TestTokenStats:
    """Tests for token_stats() function."""

    def test_single_result(self, single_pass_result):
        """Single result with token data."""
        ts = token_stats([single_pass_result])
        assert ts.mean == 150
        assert ts.median == 150
        assert ts.p95 == 150

    def test_mixed_5(self, mixed_results_5):
        """Check token stats for 5 results."""
        # Tokens: 100, 110, 50, 105, 45
        # Sorted: 45, 50, 100, 105, 110
        # Mean: (45 + 50 + 100 + 105 + 110) / 5 = 410 / 5 = 82
        # Median: 100 (middle value)
        # P95: numpy.percentile uses interpolation, result ~109
        ts = token_stats(mixed_results_5)
        assert ts.mean == 82
        assert ts.median == 100
        assert 105 <= ts.p95 <= 110  # Allow for interpolation

    def test_all_pass_tokens(self, all_pass_10):
        """Token stats for 10 passing results."""
        # Tokens: 100, 105, 110, 115, 120, 125, 130, 135, 140, 145
        # Mean: (100+105+110+115+120+125+130+135+140+145)/10 = 1225/10 = 122.5
        # Median: (120+125)/2 = 122.5
        # P95: 95th percentile ≈ 142.5
        ts = token_stats(all_pass_10)
        assert ts.mean == 122  # int(122.5)
        # Median calculation depends on numpy, should be ~122.5
        assert 120 <= ts.median <= 125
        # P95 should be high
        assert ts.p95 >= 140

    def test_no_token_data(self):
        """Results with no token data should return zeros."""
        results = [
            EvaluationResult(task_id="test", passed=True, score=1.0, duration=10.0, details={}),
            EvaluationResult(task_id="test", passed=False, score=0.0, duration=5.0, details={}),
        ]
        ts = token_stats(results)
        assert ts.mean == 0
        assert ts.median == 0
        assert ts.p95 == 0

    def test_empty_raises(self):
        """Empty list should raise ValueError."""
        with pytest.raises(ValueError):
            token_stats([])


# ============================================================================
# Tests: compute_all_metrics()
# ============================================================================


class TestComputeAllMetrics:
    """Tests for compute_all_metrics() convenience function."""

    def test_mixed_results(self, mixed_results_5):
        """Compute all metrics at once."""
        metrics = compute_all_metrics(mixed_results_5)

        assert isinstance(metrics, MetricsResult)
        assert metrics.n_runs == 5
        assert metrics.success_rate == pytest.approx(0.6)
        assert metrics.variance == pytest.approx(math.sqrt(0.6 * 0.4))
        assert metrics.mean_runtime == pytest.approx(8.2)
        assert metrics.mean_cost == pytest.approx(0.0078)
        assert 0 <= metrics.confidence_interval_lower <= metrics.confidence_interval_upper <= 1
        assert metrics.token_stats.mean == 82

    def test_all_pass(self, all_pass_10):
        """All passing results."""
        metrics = compute_all_metrics(all_pass_10)
        assert metrics.n_runs == 10
        assert metrics.success_rate == 1.0
        assert metrics.variance == pytest.approx(0.0)
        assert metrics.confidence_interval_lower > 0.7  # Wilson score is conservative
        assert metrics.confidence_interval_upper > 0.999

    def test_empty_raises(self):
        """Empty list should raise ValueError."""
        with pytest.raises(ValueError):
            compute_all_metrics([])


# ============================================================================
# Tests: Edge Cases
# ============================================================================


class TestEdgeCases:
    """Edge case tests for all metric functions."""

    def test_n_equals_1_all_functions(self, single_pass_result):
        """All functions should handle n=1 gracefully."""
        results = [single_pass_result]

        sr = success_rate(results)
        assert sr == 1.0

        ci_lower, ci_upper = confidence_interval(results)
        assert 0 <= ci_lower <= ci_upper <= 1

        var = variance(results)
        assert var == pytest.approx(0.0)

        mrt = mean_runtime(results)
        assert mrt == single_pass_result.duration

        mc = mean_cost(results)
        assert mc == 0.01

    def test_n_equals_100(self):
        """Test with larger sample size (n=100)."""
        # Create 100 results with ~50% pass rate
        results = [
            EvaluationResult(
                task_id="test",
                passed=(i < 50),
                score=float(i < 50),
                duration=10.0,
                details={"tokens": 100},
            )
            for i in range(100)
        ]

        sr = success_rate(results)
        assert sr == pytest.approx(0.5)

        ci_lower, ci_upper = confidence_interval(results)
        # With n=100, p=0.5, CI should be roughly (0.4, 0.6)
        assert 0.3 < ci_lower < 0.5
        assert 0.5 < ci_upper < 0.7

        var = variance(results)
        assert var == pytest.approx(0.5)

    def test_half_pass_half_fail(self):
        """Exactly 50% pass rate (maximum variance case)."""
        results = [
            EvaluationResult(
                task_id="test", passed=(i % 2 == 0), score=float(i % 2 == 0), duration=10.0
            )
            for i in range(10)
        ]

        sr = success_rate(results)
        assert sr == 0.5

        var = variance(results)
        # sqrt(0.5 * 0.5) = 0.5 (maximum variance for binary)
        assert var == pytest.approx(0.5)


# ============================================================================
# Tests: Dataclass Validation
# ============================================================================


class TestDataClasses:
    """Tests for TokenStats and MetricsResult dataclasses."""

    def test_token_stats_creation(self):
        """Create and validate TokenStats."""
        ts = TokenStats(mean=100, median=95, p95=150)
        assert ts.mean == 100
        assert ts.median == 95
        assert ts.p95 == 150

    def test_metrics_result_creation(self):
        """Create and validate MetricsResult."""
        ts = TokenStats(mean=100, median=95, p95=150)
        mr = MetricsResult(
            success_rate=0.8,
            confidence_interval_lower=0.6,
            confidence_interval_upper=0.95,
            variance=0.16,
            mean_runtime=10.5,
            mean_cost=0.01,
            token_stats=ts,
            n_runs=10,
        )
        assert mr.success_rate == 0.8
        assert mr.n_runs == 10
        assert mr.token_stats.mean == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
