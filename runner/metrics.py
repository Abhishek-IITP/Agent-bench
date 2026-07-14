"""
Statistical Metrics Engine for AgentBench.

Computes statistical metrics from multi-run execution results:
- Success rate
- Confidence intervals (Wilson score method)
- Variance and standard deviation
- Mean runtime, cost, and token usage

References:
- Wilson Score Interval: https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval
- Confidence level z=1.96 for 95% confidence
"""

from dataclasses import dataclass
from typing import List, Tuple
import math

import numpy as np
from scipy import stats

from runner.models import EvaluationResult


@dataclass
class TokenStats:
    """Container for token usage statistics."""

    mean: int
    median: int
    p95: int


@dataclass
class MetricsResult:
    """Container for all computed metrics."""

    success_rate: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    variance: float
    mean_runtime: float
    mean_cost: float
    token_stats: TokenStats
    n_runs: int


def success_rate(results: List[EvaluationResult]) -> float:
    """
    Compute success rate from evaluation results.

    Success rate = number of passed evaluations / total evaluations

    Args:
        results: List of EvaluationResult objects

    Returns:
        Success rate as float (0.0 to 1.0)

    Raises:
        ValueError: If results list is empty
    """
    if not results:
        raise ValueError("Cannot compute success_rate from empty results list")

    passed = sum(1 for r in results if r.passed)
    return passed / len(results)


def confidence_interval(
    results: List[EvaluationResult], confidence: float = 0.95
) -> Tuple[float, float]:
    """
    Compute Wilson score confidence interval for binomial proportion.

    The Wilson score interval is more accurate than the normal approximation,
    especially for small sample sizes or extreme proportions.

    Formula:
        Let p = success_rate, n = number of trials, z = z-score for confidence level

        lower = (p + z²/(2n) - z*sqrt(p(1-p)/n + z²/(4n²))) / (1 + z²/n)
        upper = (p + z²/(2n) + z*sqrt(p(1-p)/n + z²/(4n²))) / (1 + z²/n)

    Args:
        results: List of EvaluationResult objects
        confidence: Confidence level (default 0.95 for 95% CI)

    Returns:
        Tuple of (lower_bound, upper_bound)

    Raises:
        ValueError: If results list is empty or confidence not in (0, 1)

    References:
        Wilson, E. B. (1927). "Probable Inference, the Law of Succession, and
        Statistical Inference". Journal of the American Statistical Association, 22(158), 209-212.
    """
    if not results:
        raise ValueError("Cannot compute confidence_interval from empty results list")

    if not (0 < confidence < 1):
        raise ValueError(f"Confidence must be in (0, 1), got {confidence}")

    n = len(results)
    p = success_rate(results)

    # Get z-score for the given confidence level
    # confidence=0.95 → alpha=0.05 → alpha/2=0.025 → z=1.96
    alpha = 1 - confidence
    z = stats.norm.ppf(1 - alpha / 2)

    # Wilson score formula components
    z_sq = z**2
    p_1_minus_p = p * (1 - p)

    # Denominator
    denom = 1 + z_sq / n

    # Center
    center = (p + z_sq / (2 * n)) / denom

    # Margin of error
    margin = (z * math.sqrt(p_1_minus_p / n + z_sq / (4 * n * n))) / denom

    lower = center - margin
    upper = center + margin

    # Clamp to [0, 1]
    lower = max(0.0, lower)
    upper = min(1.0, upper)

    return (lower, upper)


def variance(results: List[EvaluationResult]) -> float:
    """
    Compute variance (standard deviation) of outcomes.

    For binary outcomes (pass/fail), this is the standard deviation
    of a Bernoulli distribution.

    Formula:
        variance = sqrt(p * (1 - p))
        where p = success_rate

    Args:
        results: List of EvaluationResult objects

    Returns:
        Standard deviation of outcomes (0.0 to 0.5 for binary)

    Raises:
        ValueError: If results list is empty
    """
    if not results:
        raise ValueError("Cannot compute variance from empty results list")

    p = success_rate(results)

    # For binary outcome, variance = p(1-p), so std_dev = sqrt(p(1-p))
    return math.sqrt(p * (1 - p))


def mean_runtime(results: List[EvaluationResult]) -> float:
    """
    Compute mean (average) runtime across results.

    Args:
        results: List of EvaluationResult objects

    Returns:
        Mean runtime in seconds

    Raises:
        ValueError: If results list is empty
    """
    if not results:
        raise ValueError("Cannot compute mean_runtime from empty results list")

    return float(np.mean([r.duration for r in results]))


def mean_cost(results: List[EvaluationResult]) -> float:
    """
    Compute mean (average) cost across results.

    Cost is extracted from the details dict if available.
    If no cost data is available, returns 0.0.

    Args:
        results: List of EvaluationResult objects

    Returns:
        Mean cost (typically in USD)
    """
    if not results:
        return 0.0

    costs = []
    for r in results:
        # Try to extract cost from details dict
        cost = r.details.get("cost", 0.0)
        costs.append(float(cost) if cost is not None else 0.0)

    if not costs:
        return 0.0

    return float(np.mean(costs))


def token_stats(results: List[EvaluationResult]) -> TokenStats:
    """
    Compute token usage statistics (mean, median, p95).

    Token counts are extracted from the details dict if available.

    Args:
        results: List of EvaluationResult objects

    Returns:
        TokenStats with mean, median, and 95th percentile

    Raises:
        ValueError: If results list is empty or no token data found
    """
    if not results:
        raise ValueError("Cannot compute token_stats from empty results list")

    tokens = []
    for r in results:
        # Try to extract token count from details dict
        token_count = r.details.get("tokens", r.details.get("token_count", None))
        if token_count is not None:
            tokens.append(int(token_count))

    if not tokens:
        # If no token data, return zeros
        return TokenStats(mean=0, median=0, p95=0)

    return TokenStats(
        mean=int(np.mean(tokens)), median=int(np.median(tokens)), p95=int(np.percentile(tokens, 95))
    )


def compute_all_metrics(results: List[EvaluationResult]) -> MetricsResult:
    """
    Compute all metrics from a list of evaluation results.

    This is a convenience function that computes all metrics at once.

    Args:
        results: List of EvaluationResult objects

    Returns:
        MetricsResult containing all computed metrics

    Raises:
        ValueError: If results list is empty
    """
    if not results:
        raise ValueError("Cannot compute metrics from empty results list")

    sr = success_rate(results)
    ci_lower, ci_upper = confidence_interval(results)
    var = variance(results)
    mrt = mean_runtime(results)
    mc = mean_cost(results)
    ts = token_stats(results)

    return MetricsResult(
        success_rate=sr,
        confidence_interval_lower=ci_lower,
        confidence_interval_upper=ci_upper,
        variance=var,
        mean_runtime=mrt,
        mean_cost=mc,
        token_stats=ts,
        n_runs=len(results),
    )
