"""
Multi-run executor for running tasks multiple times and aggregating results.

Implements sequential and parallel execution of the same task multiple times with automatic
failure handling and result aggregation for statistical analysis.
"""

import asyncio
import statistics
from datetime import datetime
from typing import TYPE_CHECKING, Callable, Optional

from pydantic import BaseModel, Field, model_validator

from runner.agents.base import BaseAgent
from runner.executor import TaskExecutor
from runner.logging import get_logger
from runner.models import EvaluationResult
from runner.scoring import compute_reliability_score

if TYPE_CHECKING:
    from runner.storage import Storage

logger = get_logger(__name__)


class MultiRunResult(BaseModel):
    """Aggregated results from multiple runs of the same task."""

    task_id: str = Field(..., description="Unique task identifier")
    agent_name: str = Field(..., description="Name of the agent used")
    n_runs: int = Field(..., description="Total number of runs requested")
    runs: list[EvaluationResult] = Field(
        default_factory=list, description="List of individual run results"
    )
    success_count: int = Field(default=0, description="Number of successful runs")
    success_rate: float = Field(
        default=0.0, description="Proportion of successful runs (0.0 to 1.0)"
    )
    mean_runtime: float = Field(
        default=0.0, description="Mean execution time across runs (seconds)"
    )
    mean_tokens: float = Field(default=0.0, description="Mean token usage across runs")
    mean_cost: float = Field(default=0.0, description="Mean cost across runs (USD)")
    reliability_score: float = Field(
        default=0.0, description="Combined score reflecting success rate and consistency"
    )
    aggregated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp when results were aggregated"
    )

    @model_validator(mode="after")
    def compute_reliability_score(self):
        """Automatically compute reliability score after model creation."""
        if self.n_runs == 0:
            self.reliability_score = 0.0
        else:
            # Base score is simply the success rate
            self.reliability_score = self.success_rate
        return self

    @property
    def failure_count(self) -> int:
        """Get the number of failed runs."""
        return len(self.runs) - self.success_count

    def _compute_reliability_score(self) -> float:
        """
        Compute reliability score based on success rate and consistency.

        Returns:
            Float between 0.0 and 1.0
        """
        if self.n_runs == 0:
            return 0.0

        # Base score is simply the success rate
        return self.success_rate


class MultiRunExecutor:
    """Executes the same task multiple times sequentially or in parallel and aggregates results."""

    def __init__(self, executor: Optional[TaskExecutor] = None, max_concurrent: int = 5):
        """
        Initialize the multi-run executor.

        Args:
            executor: TaskExecutor instance for running individual tasks.
                     If None, creates a new TaskExecutor.
            max_concurrent: Maximum number of concurrent runs (default 5).
                          Set to 1 for sequential execution.
        """
        self.executor = executor or TaskExecutor()
        self.logger = logger
        self.max_concurrent = max_concurrent
        self._progress_callback: Optional[Callable[[int, int], None]] = None

    def execute_multi_run(
        self,
        task_id: str,
        agent: BaseAgent,
        n_runs: int,
        timeout: Optional[int] = None,
        use_parallelization: bool = False,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        storage: Optional["Storage"] = None,
    ) -> MultiRunResult:
        """
        Execute a task multiple times sequentially or in parallel.

        Runs the task n_runs times, collecting results even if individual
        runs fail. This allows statistical analysis of agent performance.

        Args:
            task_id: ID of the task to execute
            agent: Agent instance to solve the task
            n_runs: Number of times to run the task
            timeout: Execution timeout per run in seconds (optional)
            use_parallelization: If True, use parallel execution with asyncio.
                               If False, execute sequentially (default).
            progress_callback: Optional callback function(completed: int, total: int)
                             called after each run completes.
            storage: Optional Storage instance to persist results to database

        Returns:
            MultiRunResult with aggregated results from all runs
        """
        self.logger.info(
            "Starting multi-run execution",
            task_id=task_id,
            agent_name=agent.config.name,
            n_runs=n_runs,
            use_parallelization=use_parallelization,
            max_concurrent=self.max_concurrent if use_parallelization else "N/A",
        )

        self._progress_callback = progress_callback

        if use_parallelization:
            # Use asyncio for parallel execution
            runs = asyncio.run(
                self._execute_parallel(
                    task_id=task_id,
                    agent=agent,
                    n_runs=n_runs,
                    timeout=timeout,
                )
            )
        else:
            # Sequential execution
            runs = self._execute_sequential(
                task_id=task_id,
                agent=agent,
                n_runs=n_runs,
                timeout=timeout,
            )

        # Aggregate results
        multi_result = self._aggregate_results(
            task_id=task_id,
            agent=agent,
            runs=runs,
            n_runs=n_runs,
        )

        # Store results in database if storage provided
        if storage:
            try:
                from runner.metrics import compute_all_metrics

                metrics = compute_all_metrics(runs)

                storage.store_multi_run_metrics(
                    task_id=task_id,
                    agent_name=agent.config.name,
                    n_runs=len(runs),
                    success_rate=multi_result.success_rate,
                    confidence_interval_lower=metrics.confidence_interval_lower,
                    confidence_interval_upper=metrics.confidence_interval_upper,
                    variance=metrics.variance,
                    mean_runtime=metrics.mean_runtime,
                    mean_tokens=metrics.token_stats.mean,
                    mean_cost=metrics.mean_cost,
                    reliability_score=multi_result.reliability_score,
                )
                self.logger.debug(
                    "Multi-run results stored in database",
                    task_id=task_id,
                    agent_name=agent.config.name,
                )
            except Exception as e:
                self.logger.warning(
                    "Failed to store multi-run results in database",
                    error=str(e),
                )

        return multi_result

    def _execute_sequential(
        self,
        task_id: str,
        agent: BaseAgent,
        n_runs: int,
        timeout: Optional[int] = None,
    ) -> list[EvaluationResult]:
        """
        Execute runs sequentially, one after another.

        Args:
            task_id: Task ID
            agent: Agent instance
            n_runs: Number of runs
            timeout: Execution timeout per run

        Returns:
            List of EvaluationResult objects
        """
        runs = []

        for run_num in range(1, n_runs + 1):
            self.logger.debug(
                "Executing run (sequential)",
                task_id=task_id,
                run=f"{run_num}/{n_runs}",
                agent_name=agent.config.name,
            )

            result = self._run_single(
                task_id=task_id,
                agent=agent,
                run_num=run_num,
                timeout=timeout,
            )

            runs.append(result)

            # Call progress callback if provided
            if self._progress_callback:
                self._progress_callback(len(runs), n_runs)

        return runs

    async def _execute_parallel(
        self,
        task_id: str,
        agent: BaseAgent,
        n_runs: int,
        timeout: Optional[int] = None,
    ) -> list[EvaluationResult]:
        """
        Execute runs in parallel using asyncio with semaphore for concurrency control.

        Uses a semaphore to limit the number of concurrent runs to max_concurrent.
        Individual run failures are caught and logged without failing the entire batch.

        Args:
            task_id: Task ID
            agent: Agent instance
            n_runs: Number of runs
            timeout: Execution timeout per run

        Returns:
            List of EvaluationResult objects
        """
        self.logger.info(
            "Using parallel execution",
            task_id=task_id,
            max_concurrent=self.max_concurrent,
            n_runs=n_runs,
        )

        # Create a semaphore to limit concurrent execution
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def run_with_limit(run_num: int) -> EvaluationResult:
            """Execute a single run with semaphore limit."""
            async with semaphore:
                self.logger.debug(
                    "Executing run (parallel)",
                    task_id=task_id,
                    run=f"{run_num}/{n_runs}",
                    agent_name=agent.config.name,
                    max_concurrent=self.max_concurrent,
                )

                # Run in thread pool to not block the event loop
                # (executor.execute_task is synchronous)
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self._run_single,
                    task_id,
                    agent,
                    run_num,
                    timeout,
                )

                # Call progress callback if provided
                if self._progress_callback:
                    self._progress_callback(run_num, n_runs)

                return result

        # Create tasks for all runs
        tasks = [run_with_limit(run_num) for run_num in range(1, n_runs + 1)]

        # Gather all results, with return_exceptions=True to prevent
        # one failure from crashing the entire batch
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out any exceptions and log them
        runs = []
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                self.logger.error(
                    "Run failed with exception during parallel execution",
                    task_id=task_id,
                    run_num=i,
                    agent_name=agent.config.name,
                    error=str(result),
                    exc_info=False,
                )
                # Create a failed result for this run
                failed_result = EvaluationResult(
                    task_id=task_id,
                    passed=False,
                    score=0.0,
                    test_output=f"Exception during parallel execution: {str(result)}",
                    details={
                        "error": str(result),
                        "exception_type": type(result).__name__,
                    },
                )
                runs.append(failed_result)
            else:
                runs.append(result)

        return runs

    def _run_single(
        self,
        task_id: str,
        agent: BaseAgent,
        run_num: int,
        timeout: Optional[int] = None,
    ) -> EvaluationResult:
        """
        Execute a single run of a task.

        Wraps the execution in error handling to ensure failures in one run
        don't prevent execution of subsequent runs.

        Args:
            task_id: ID of the task
            agent: Agent instance
            run_num: Run number (for logging)
            timeout: Execution timeout in seconds

        Returns:
            EvaluationResult for this run
        """
        try:
            # Execute the task using the executor
            result = self.executor.execute_task(
                task_id=task_id,
                timeout=timeout,
            )

            self.logger.debug(
                "Run completed",
                task_id=task_id,
                run_num=run_num,
                passed=result.passed,
                duration=result.duration,
            )

            return result

        except Exception as e:
            # Log the error but don't crash the batch
            self.logger.error(
                "Run failed with exception",
                task_id=task_id,
                run_num=run_num,
                agent_name=agent.config.name,
                error=str(e),
                exc_info=True,
            )

            # Return a failed result instead of crashing
            return EvaluationResult(
                task_id=task_id,
                passed=False,
                score=0.0,
                test_output=f"Exception during execution: {str(e)}",
                details={"error": str(e), "exception_type": type(e).__name__},
            )

    def _aggregate_results(
        self,
        task_id: str,
        agent: BaseAgent,
        runs: list[EvaluationResult],
        n_runs: int,
    ) -> MultiRunResult:
        """
        Aggregate individual run results into a MultiRunResult.

        Uses the reliability scoring formula to compute a combined score
        reflecting both success rate and consistency.

        Args:
            task_id: Task ID
            agent: Agent instance
            runs: List of individual run results
            n_runs: Total number of runs

        Returns:
            Aggregated MultiRunResult
        """
        if not runs:
            self.logger.warning("No runs completed", task_id=task_id)
            return MultiRunResult(
                task_id=task_id,
                agent_name=agent.config.name,
                n_runs=n_runs,
                runs=[],
                success_count=0,
                success_rate=0.0,
                mean_runtime=0.0,
                mean_tokens=0.0,
                mean_cost=0.0,
                reliability_score=0.0,
            )

        # Count successes
        success_count = sum(1 for run in runs if run.passed)
        success_rate = success_count / len(runs) if runs else 0.0

        # Calculate mean runtime
        runtimes = [run.duration for run in runs]
        mean_runtime = statistics.mean(runtimes) if runtimes else 0.0

        # For now, mean_tokens and mean_cost are 0 since EvaluationResult
        # doesn't track these yet. This is prepared for future enhancement.
        mean_tokens = 0.0
        mean_cost = 0.0

        # Compute reliability score using the scoring module
        # This combines success_rate (70%) and consistency (30%)
        reliability_score = compute_reliability_score(runs) / 100.0  # Normalize to 0-1

        # Create result
        multi_result = MultiRunResult(
            task_id=task_id,
            agent_name=agent.config.name,
            n_runs=n_runs,
            runs=runs,
            success_count=success_count,
            success_rate=success_rate,
            mean_runtime=mean_runtime,
            mean_tokens=mean_tokens,
            mean_cost=mean_cost,
            reliability_score=reliability_score,
        )

        self.logger.info(
            "Multi-run execution complete",
            task_id=task_id,
            agent_name=agent.config.name,
            n_runs=len(runs),
            success_count=success_count,
            success_rate=success_rate,
            mean_runtime=mean_runtime,
            reliability_score=reliability_score,
        )

        return multi_result
