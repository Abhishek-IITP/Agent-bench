"""
Reliability Scoring Engine for AgentBench.

Computes a single reliability score (0-100) that combines success rate and consistency.

The reliability score reflects how trustworthy an agent is on a given task:
- Success rate (70% weight): The proportion of runs that pass
- Consistency (30% weight): How stable performance is across runs

Formula:
    reliability_score = (success_rate_component * 100) + (consistency_component * 100)

    Where:
        success_rate_component = success_rate * 0.7
        consistency_component = (1 - normalized_variance) * success_rate * 0.3
        normalized_variance = min(variance / 0.5, 1.0)  # Normalize to max of 0.5

    Final score is clamped to [0, 100].

Key Insight:
    Consistency bonus is scaled by success_rate. This means:
    - If success_rate = 0, consistency doesn't contribute (no bonus for failing consistently)
    - If success_rate = 1, consistency gives full 30 points (high success + stability = best)
    - If success_rate = 0.5, consistency gives at most 15 points

Example Scenarios:
    - 100% success, 0 variance → success=70 + (1.0)*1.0*30 = 100
    - 50% success, 0 variance → success=35 + (1.0)*0.5*30 = 50
    - 100% success, high variance → success=70 + (0.0)*1.0*30 = 70
    - 50% success, high variance → success=35 + (0.0)*0.5*30 = 35
    - 0% success (any variance) → success=0 + anything*0*30 = 0

The formula penalizes high variance even with good success rates, reflecting that
inconsistent performance is less reliable than consistent performance.
"""

from dataclasses import dataclass
from typing import List, Optional

from runner.models import EvaluationResult
from runner.metrics import success_rate, variance


@dataclass
class ReliabilityScore:
    """Container for reliability score and its components."""

    total_score: float  # 0-100
    success_component: float  # 0-70
    consistency_component: float  # 0-30
    success_rate: float  # 0-1
    variance: float  # 0-0.5 typically
    n_runs: int


def compute_reliability_score(
    results: List[EvaluationResult],
    weights: Optional[dict] = None,
) -> float:
    """
    Compute a single reliability score combining success rate and consistency.

    The reliability score is a number from 0 to 100 that reflects how reliable
    an agent is on a task. Higher scores indicate more reliable performance.

    The score combines two components:
    1. Success Rate Component (70% weight): success_rate * 0.7 * 100
    2. Consistency Component (30% weight): consistency * success_rate * 0.3 * 100

    Where consistency = 1 - min(variance / 0.5, 1.0)

    The key insight: consistency only matters when success_rate is high.
    A perfect failure record (0% success) has 0 variance but 0 reliability.
    The consistency bonus only applies to the success portion of the score.

    Args:
        results: List of EvaluationResult objects from multiple runs
        weights: Optional dict with keys "success" and "consistency" to override defaults.
                 Default: {"success": 0.7, "consistency": 0.3}
                 Must sum to 1.0.

    Returns:
        Reliability score as float between 0.0 and 100.0

    Raises:
        ValueError: If results list is empty or weights don't sum to 1.0

    Examples:
        >>> results = [EvaluationResult(task_id="test", passed=True) for _ in range(10)]
        >>> score = compute_reliability_score(results)
        >>> assert score == 100.0  # All passed, high consistency

        >>> results = [EvaluationResult(task_id="test", passed=i % 2 == 0) for i in range(10)]
        >>> score = compute_reliability_score(results)
        >>> assert 0 <= score <= 100  # Valid range
    """
    if not results:
        raise ValueError("Cannot compute reliability_score from empty results list")

    # Set default weights if not provided
    if weights is None:
        weights = {"success": 0.7, "consistency": 0.3}

    # Validate weights
    if not isinstance(weights, dict):
        raise ValueError(f"weights must be a dict, got {type(weights)}")

    if "success" not in weights or "consistency" not in weights:
        required = "'success' and 'consistency'"
        raise ValueError(f"weights must have {required} keys, got {weights.keys()}")

    weight_sum = weights["success"] + weights["consistency"]
    if not (0.99 < weight_sum < 1.01):  # Allow small floating point errors
        raise ValueError(f"weights must sum to 1.0, got {weight_sum}")

    # Compute components
    success_rate_val = success_rate(results)
    variance_val = variance(results)

    # Success component: normalized to [0, 70]
    success_component = success_rate_val * weights["success"] * 100

    # Consistency component: normalized variance to [0, 30]
    # Variance for binary outcomes is in [0, 0.5] (max at p=0.5)
    # Normalize: if variance = 0, consistency = 1; if variance = 0.5, consistency = 0
    # BUT: only award consistency bonus if we have reasonable success rate
    # This prevents all-failures from getting consistency credit
    max_variance = 0.5
    normalized_variance = min(variance_val / max_variance, 1.0)
    consistency = 1.0 - normalized_variance

    # Scale consistency bonus by success rate: only applicable to successful runs
    consistency_component = consistency * success_rate_val * weights["consistency"] * 100

    # Total score
    total_score = success_component + consistency_component

    # Clamp to [0, 100]
    total_score = max(0.0, min(100.0, total_score))

    return total_score


def compute_reliability_score_with_breakdown(
    results: List[EvaluationResult],
    weights: Optional[dict] = None,
) -> ReliabilityScore:
    """
    Compute reliability score and return detailed breakdown.

    Same as compute_reliability_score() but returns a ReliabilityScore object
    with detailed component breakdown for inspection and debugging.

    Args:
        results: List of EvaluationResult objects from multiple runs
        weights: Optional dict with keys "success" and "consistency" to override defaults.

    Returns:
        ReliabilityScore dataclass with total_score and components

    Raises:
        ValueError: If results list is empty or weights don't sum to 1.0
    """
    if not results:
        raise ValueError("Cannot compute reliability_score from empty results list")

    # Set default weights
    if weights is None:
        weights = {"success": 0.7, "consistency": 0.3}

    # Compute components
    success_rate_val = success_rate(results)
    variance_val = variance(results)

    # Success component: [0, 70]
    success_component = success_rate_val * weights["success"] * 100

    # Consistency component: [0, 30]
    max_variance = 0.5
    normalized_variance = min(variance_val / max_variance, 1.0)
    consistency = 1.0 - normalized_variance
    consistency_component = consistency * success_rate_val * weights["consistency"] * 100

    # Total score
    total_score = success_component + consistency_component
    total_score = max(0.0, min(100.0, total_score))

    return ReliabilityScore(
        total_score=total_score,
        success_component=success_component,
        consistency_component=consistency_component,
        success_rate=success_rate_val,
        variance=variance_val,
        n_runs=len(results),
    )
