"""
Task Health Classification System.

Classifies tasks based on their execution characteristics:
- HEALTHY: Normal task, functioning as expected
- FLAKY: Inconsistent results, high variance across agents
- BROKEN: Consistently fails, likely has issues
- TRIVIAL: All agents pass 100%, not useful for benchmarking
- SATURATED: Top agents achieve 100%, task is saturated

This module provides health analysis for individual tasks and the entire benchmark.
"""

import statistics
from dataclasses import dataclass, field
from enum import Enum

from runner.logging import get_logger
from runner.metrics import success_rate, variance

logger = get_logger(__name__)


class TaskHealthStatus(str, Enum):
    """Health status categories for tasks."""

    HEALTHY = "healthy"
    FLAKY = "flaky"
    BROKEN = "broken"
    TRIVIAL = "trivial"
    SATURATED = "saturated"


@dataclass
class HealthReport:
    """Health analysis report for a task."""

    task_id: str
    health_status: TaskHealthStatus
    success_rate: float  # 0.0 to 1.0
    variance: float  # 0.0 to 0.5 typically
    n_agents: int  # Number of agents tested
    n_runs_total: int  # Total runs across all agents
    evidence: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "task_id": self.task_id,
            "health_status": self.health_status.value,
            "success_rate": self.success_rate,
            "variance": self.variance,
            "n_agents": self.n_agents,
            "n_runs_total": self.n_runs_total,
            "evidence": self.evidence,
            "recommendations": self.recommendations,
        }


def analyze_task_health(
    task_id: str,
    results_by_agent: dict[str, list],
    oracle_passed: bool,
    nop_passed: bool,
) -> HealthReport:
    """
    Classify task health based on execution results.

    Classification logic:
    1. If Oracle fails → BROKEN (task validation broken)
    2. If all agents fail → BROKEN (likely task issue)
    3. If variance > 0.3 → FLAKY (inconsistent across agents)
    4. If success_rate == 1.0 → TRIVIAL (too easy)
    5. If all top agents == 1.0 → SATURATED (agents saturated)
    6. Else → HEALTHY (normal performance)

    Args:
        task_id: Task identifier
        results_by_agent: Dict mapping agent_name -> list of EvaluationResult objects
        oracle_passed: Whether Oracle validation passed
        nop_passed: Whether NOP validation passed

    Returns:
        HealthReport with classification and analysis
    """
    evidence = []
    recommendations = []

    # Collect all results
    all_results = []
    n_agents = len(results_by_agent)

    for agent_name, results in results_by_agent.items():
        all_results.extend(results)

    if not all_results:
        logger.warning("No results found for health analysis", task_id=task_id)
        return HealthReport(
            task_id=task_id,
            health_status=TaskHealthStatus.BROKEN,
            success_rate=0.0,
            variance=0.0,
            n_agents=n_agents,
            n_runs_total=0,
            evidence=["No execution results available"],
            recommendations=["Check if task is properly configured"],
        )

    # Compute metrics
    sr = success_rate(all_results)
    var = variance(all_results)

    # For better detection of flakiness, compute variance per-agent first
    # and then analyze cross-agent variance
    agent_success_rates = {}
    for agent_name, results in results_by_agent.items():
        if results:
            agent_success_rates[agent_name] = success_rate(results)

    # Calculate variance in agent success rates (inter-agent variance)
    # This detects when agents perform very differently (flakiness)
    if len(agent_success_rates) > 1:
        inter_agent_variance = statistics.variance(agent_success_rates.values())
    else:
        inter_agent_variance = 0.0

    # Check Oracle validation
    if not oracle_passed:
        evidence.append("Oracle validation failed - task validation is broken")
        recommendations.append("Fix task validation - Oracle pattern is failing")
        return HealthReport(
            task_id=task_id,
            health_status=TaskHealthStatus.BROKEN,
            success_rate=sr,
            variance=var,
            n_agents=n_agents,
            n_runs_total=len(all_results),
            evidence=evidence,
            recommendations=recommendations,
        )

    # Check if all agents fail
    if sr == 0.0:
        evidence.append(f"All {n_agents} agents failed on this task")
        evidence.append(f"NOP validation passed: {nop_passed}")
        recommendations.extend(
            [
                "Review task environment and constraints",
                "Verify task is solvable",
                "Check if agents have necessary capabilities",
            ]
        )
        return HealthReport(
            task_id=task_id,
            health_status=TaskHealthStatus.BROKEN,
            success_rate=sr,
            variance=var,
            n_agents=n_agents,
            n_runs_total=len(all_results),
            evidence=evidence,
            recommendations=recommendations,
        )

    # Check for very low success rate (< 15%) - likely broken
    # But don't trigger if it's just a few agents failing
    if sr < 0.15 and sr > 0.0:
        # Only flag as broken if most agents are struggling
        if len(agent_success_rates) > 1:
            # Check if majority of agents have low success
            low_performing_agents = sum(1 for s in agent_success_rates.values() if s < 0.5)
            if low_performing_agents >= len(agent_success_rates) * 0.5:  # 50% of agents low
                evidence.append(f"Very low success rate: {sr:.1%}")
                low_count = low_performing_agents
                total_agents = len(agent_success_rates)
                evidence.append(f"Majority of agents struggling: {low_count}/{total_agents}")
                recommendations.extend(
                    [
                        "Review task environment and constraints",
                        "Verify task is solvable",
                        "Check if agents have necessary capabilities",
                    ]
                )
                return HealthReport(
                    task_id=task_id,
                    health_status=TaskHealthStatus.BROKEN,
                    success_rate=sr,
                    variance=var,
                    n_agents=n_agents,
                    n_runs_total=len(all_results),
                    evidence=evidence,
                    recommendations=recommendations,
                )
        else:
            # Single agent with very low success
            evidence.append(f"Very low success rate: {sr:.1%}")
            evidence.append("Agent struggling on this task")
            recommendations.extend(
                [
                    "Review task environment and constraints",
                    "Verify task is solvable",
                    "Check if agents have necessary capabilities",
                ]
            )
            return HealthReport(
                task_id=task_id,
                health_status=TaskHealthStatus.BROKEN,
                success_rate=sr,
                variance=var,
                n_agents=n_agents,
                n_runs_total=len(all_results),
                evidence=evidence,
                recommendations=recommendations,
            )

    # Check for saturation (top agents at 100%, but not everyone)
    # This should be checked BEFORE flakiness since saturation is more specific
    agent_success_rates_sorted = sorted(
        agent_success_rates.items(), key=lambda x: x[1], reverse=True
    )
    top_agents = agent_success_rates_sorted[: min(3, len(agent_success_rates_sorted))]
    top_success_rates = [sr_agent for _, sr_agent in top_agents]

    # Saturated = top agents at 100%, but overall not at 100%
    # This means best agents have mastered it, but it still challenges others
    if (
        len(top_success_rates) >= 2
        and all(sr_agent >= 1.0 for sr_agent in top_success_rates)
        and sr < 1.0
    ):  # NOT everyone at 100%
        evidence.append(f"Top {len(top_agents)} agents achieved 100% success")
        evidence.append("Task may be saturated for these agents")
        recommendations.extend(
            [
                "Consider increasing task complexity",
                "Add adversarial test cases",
                "Archive this task once all agents saturate",
            ]
        )
        return HealthReport(
            task_id=task_id,
            health_status=TaskHealthStatus.SATURATED,
            success_rate=sr,
            variance=var,
            n_agents=n_agents,
            n_runs_total=len(all_results),
            evidence=evidence,
            recommendations=recommendations,
        )

    # Check for flakiness (high inter-agent variance)
    # If agents perform very differently on the same task, it's flaky
    if inter_agent_variance > 0.05:  # Variance in agent success rates > 5%
        msg = f"High variance across agents (inter-agent variance: {inter_agent_variance:.3f})"
        evidence.append(msg)
        evidence.append(f"Agent success rates vary widely: {agent_success_rates}")
        recommendations.extend(
            [
                "Investigate inconsistent performance across agents",
                "Check for environmental factors",
                "Consider increasing isolation/stability",
                "Review task specification for ambiguity",
            ]
        )
        return HealthReport(
            task_id=task_id,
            health_status=TaskHealthStatus.FLAKY,
            success_rate=sr,
            variance=var,
            n_agents=n_agents,
            n_runs_total=len(all_results),
            evidence=evidence,
            recommendations=recommendations,
        )

    # Check for triviality (100% success overall)
    if sr >= 1.0:
        evidence.append("All runs passed across all agents")
        evidence.append("Task difficulty may be too low for effective benchmarking")
        recommendations.extend(
            [
                "Consider increasing task difficulty",
                "Add more complex requirements",
                "Remove from active benchmarking set",
            ]
        )
        return HealthReport(
            task_id=task_id,
            health_status=TaskHealthStatus.TRIVIAL,
            success_rate=sr,
            variance=var,
            n_agents=n_agents,
            n_runs_total=len(all_results),
            evidence=evidence,
            recommendations=recommendations,
        )

    # Otherwise: HEALTHY
    evidence.append(f"Success rate: {sr:.1%} (moderate difficulty)")
    evidence.append(f"Consistency: good (variance {var:.3f})")
    evidence.append(f"Performance across {n_agents} agents is stable")
    recommendations.extend(
        [
            "Continue using in active benchmarking",
            "Monitor for performance degradation",
            "Consider as a baseline task",
        ]
    )

    return HealthReport(
        task_id=task_id,
        health_status=TaskHealthStatus.HEALTHY,
        success_rate=sr,
        variance=var,
        n_agents=n_agents,
        n_runs_total=len(all_results),
        evidence=evidence,
        recommendations=recommendations,
    )


def compute_benchmark_health(
    results_by_task: dict[str, dict[str, list]],
    oracle_results: dict[str, bool],
    nop_results: dict[str, bool],
) -> dict[str, HealthReport]:
    """
    Compute health analysis for all tasks in the benchmark.

    Args:
        results_by_task: Dict mapping task_id -> (agent_name -> list of results)
        oracle_results: Dict mapping task_id -> oracle_passed bool
        nop_results: Dict mapping task_id -> nop_passed bool

    Returns:
        Dict mapping task_id -> HealthReport
    """
    health_reports = {}

    for task_id, results_by_agent in results_by_task.items():
        oracle_passed = oracle_results.get(task_id, False)
        nop_passed = nop_results.get(task_id, False)

        report = analyze_task_health(
            task_id=task_id,
            results_by_agent=results_by_agent,
            oracle_passed=oracle_passed,
            nop_passed=nop_passed,
        )

        health_reports[task_id] = report

        logger.info(
            "Task health analyzed",
            task_id=task_id,
            health_status=report.health_status.value,
            success_rate=report.success_rate,
            variance=report.variance,
        )

    return health_reports


def summarize_benchmark_health(health_reports: dict[str, HealthReport]) -> dict:
    """
    Summarize overall benchmark health.

    Args:
        health_reports: Dict mapping task_id -> HealthReport

    Returns:
        Summary statistics
    """
    if not health_reports:
        return {
            "total_tasks": 0,
            "healthy": 0,
            "flaky": 0,
            "broken": 0,
            "trivial": 0,
            "saturated": 0,
        }

    status_counts = {status: 0 for status in TaskHealthStatus}

    for report in health_reports.values():
        status_counts[report.health_status] += 1

    return {
        "total_tasks": len(health_reports),
        "healthy": status_counts[TaskHealthStatus.HEALTHY],
        "flaky": status_counts[TaskHealthStatus.FLAKY],
        "broken": status_counts[TaskHealthStatus.BROKEN],
        "trivial": status_counts[TaskHealthStatus.TRIVIAL],
        "saturated": status_counts[TaskHealthStatus.SATURATED],
        "health_percentage": (
            (status_counts[TaskHealthStatus.HEALTHY] / len(health_reports)) * 100
            if health_reports
            else 0
        ),
    }
