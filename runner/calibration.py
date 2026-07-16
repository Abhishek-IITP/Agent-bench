"""
Difficulty Calibration System.

Estimates task difficulty from agent performance and compares to author assignment.

The system maps success rates to difficulty levels:
- ≥80% success → EASY
- 50-80% → MEDIUM
- 20-50% → HARD
- <20% → EXPERT

Mismatches between author difficulty and empirical difficulty are flagged
with recommendations for adjustment.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from runner.logging import get_logger
from runner.metrics import success_rate

logger = get_logger(__name__)


class DifficultyLevel(str, Enum):
    """Difficulty levels for tasks."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


@dataclass
class CalibrationReport:
    """Difficulty calibration report for a task."""

    task_id: str
    author_difficulty: Optional[DifficultyLevel]
    empirical_difficulty: DifficultyLevel
    mean_success_rate: float  # 0.0 to 1.0
    median_success_rate: float  # 0.0 to 1.0
    n_agents: int  # Number of agents tested
    match: bool  # Whether author and empirical match
    recommendation: str = ""
    confidence: float = 0.5  # 0.0 to 1.0 based on number of agents

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "task_id": self.task_id,
            "author_difficulty": self.author_difficulty.value if self.author_difficulty else None,
            "empirical_difficulty": self.empirical_difficulty.value,
            "mean_success_rate": self.mean_success_rate,
            "median_success_rate": self.median_success_rate,
            "n_agents": self.n_agents,
            "match": self.match,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
        }


def estimate_difficulty(mean_success_rate: float) -> DifficultyLevel:
    """
    Estimate task difficulty from success rate.

    Mapping:
    - ≥80% success → EASY (almost always passes)
    - 50-80% → MEDIUM (majority passes)
    - 20-50% → HARD (majority fails)
    - <20% → EXPERT (almost always fails)

    Args:
        mean_success_rate: Mean success rate across agents (0.0 to 1.0)

    Returns:
        DifficultyLevel
    """
    if mean_success_rate >= 0.80:
        return DifficultyLevel.EASY
    elif mean_success_rate >= 0.50:
        return DifficultyLevel.MEDIUM
    elif mean_success_rate >= 0.20:
        return DifficultyLevel.HARD
    else:
        return DifficultyLevel.EXPERT


def calibrate_difficulty(
    task_id: str,
    results_by_agent: dict[str, list],
    author_difficulty: Optional[DifficultyLevel] = None,
) -> CalibrationReport:
    """
    Calibrate task difficulty from agent performance.

    Analyzes success rates across all agents to estimate empirical difficulty,
    then compares to author-assigned difficulty (if available).

    Args:
        task_id: Task identifier
        results_by_agent: Dict mapping agent_name -> list of EvaluationResult objects
        author_difficulty: Author-assigned difficulty (optional)

    Returns:
        CalibrationReport with estimated difficulty and comparison
    """
    if not results_by_agent:
        logger.warning("No results for calibration", task_id=task_id)
        return CalibrationReport(
            task_id=task_id,
            author_difficulty=author_difficulty,
            empirical_difficulty=DifficultyLevel.MEDIUM,
            mean_success_rate=0.0,
            median_success_rate=0.0,
            n_agents=0,
            match=False,
            recommendation="Cannot calibrate without execution results",
            confidence=0.0,
        )

    # Compute success rates per agent
    agent_success_rates = []

    for agent_name, results in results_by_agent.items():
        if results:
            sr = success_rate(results)
            agent_success_rates.append(sr)

    if not agent_success_rates:
        logger.warning("No valid results for calibration", task_id=task_id)
        return CalibrationReport(
            task_id=task_id,
            author_difficulty=author_difficulty,
            empirical_difficulty=DifficultyLevel.MEDIUM,
            mean_success_rate=0.0,
            median_success_rate=0.0,
            n_agents=0,
            match=False,
            recommendation="No valid execution results for any agent",
            confidence=0.0,
        )

    # Compute statistics
    import statistics

    mean_sr = statistics.mean(agent_success_rates)
    median_sr = statistics.median(agent_success_rates)
    n_agents = len(agent_success_rates)

    # Estimate empirical difficulty
    empirical_difficulty = estimate_difficulty(mean_sr)

    # Compute confidence based on number of agents
    # More agents = higher confidence
    confidence = min(1.0, n_agents / 3.0)  # Full confidence at 3+ agents

    # Compare with author difficulty
    match = True
    recommendation = ""

    if author_difficulty:
        match = empirical_difficulty == author_difficulty

        if not match:
            # Generate recommendation
            if empirical_difficulty.value > author_difficulty.value:
                # Task is harder than expected
                recommendation = (
                    f"Task is empirically {empirical_difficulty.value.upper()} "
                    f"but marked as {author_difficulty.value.upper()}. "
                    f"Success rate: {mean_sr:.1%}. "
                    f"Consider re-rating task difficulty."
                )
            else:
                # Task is easier than expected
                recommendation = (
                    f"Task is empirically {empirical_difficulty.value.upper()} "
                    f"but marked as {author_difficulty.value.upper()}. "
                    f"Success rate: {mean_sr:.1%}. "
                    f"Consider increasing difficulty or re-rating."
                )
    else:
        recommendation = (
            f"Empirical difficulty: {empirical_difficulty.value.upper()} "
            f"(success rate: {mean_sr:.1%} across {n_agents} agents). "
            f"No author difficulty to compare."
        )

    return CalibrationReport(
        task_id=task_id,
        author_difficulty=author_difficulty,
        empirical_difficulty=empirical_difficulty,
        mean_success_rate=mean_sr,
        median_success_rate=median_sr,
        n_agents=n_agents,
        match=match,
        recommendation=recommendation,
        confidence=confidence,
    )


def compute_all_calibrations(
    results_by_task: dict[str, dict[str, list]],
    author_difficulties: dict[str, DifficultyLevel],
) -> dict[str, CalibrationReport]:
    """
    Compute difficulty calibration for all tasks.

    Args:
        results_by_task: Dict mapping task_id -> (agent_name -> list of results)
        author_difficulties: Dict mapping task_id -> DifficultyLevel

    Returns:
        Dict mapping task_id -> CalibrationReport
    """
    calibrations = {}

    for task_id, results_by_agent in results_by_task.items():
        author_difficulty = author_difficulties.get(task_id)

        report = calibrate_difficulty(
            task_id=task_id,
            results_by_agent=results_by_agent,
            author_difficulty=author_difficulty,
        )

        calibrations[task_id] = report

        logger.info(
            "Task difficulty calibrated",
            task_id=task_id,
            author_difficulty=report.author_difficulty.value if report.author_difficulty else None,
            empirical_difficulty=report.empirical_difficulty.value,
            match=report.match,
            success_rate=report.mean_success_rate,
        )

    return calibrations


def summarize_calibrations(
    calibrations: dict[str, CalibrationReport],
) -> dict:
    """
    Summarize overall calibration results.

    Args:
        calibrations: Dict mapping task_id -> CalibrationReport

    Returns:
        Summary statistics
    """
    if not calibrations:
        return {
            "total_tasks": 0,
            "matched": 0,
            "mismatched": 0,
            "match_rate": 0.0,
            "average_confidence": 0.0,
            "difficulty_distribution": {},
        }

    total_tasks = len(calibrations)
    matched = sum(1 for r in calibrations.values() if r.match)
    mismatched = total_tasks - matched

    # Distribution of empirical difficulties
    difficulty_counts = {level.value: 0 for level in DifficultyLevel}
    for report in calibrations.values():
        difficulty_counts[report.empirical_difficulty.value] += 1

    # Average confidence
    avg_confidence = (
        sum(r.confidence for r in calibrations.values()) / total_tasks if total_tasks > 0 else 0.0
    )

    return {
        "total_tasks": total_tasks,
        "matched": matched,
        "mismatched": mismatched,
        "match_rate": (matched / total_tasks) if total_tasks > 0 else 0.0,
        "average_confidence": avg_confidence,
        "difficulty_distribution": difficulty_counts,
        "mismatched_tasks": [
            task_id for task_id, report in calibrations.items() if not report.match
        ],
    }
