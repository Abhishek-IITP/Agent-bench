"""
Result and run storage with PostgreSQL backend.

Stores tasks, runs, results, and replay data.
Provides fallback to file-based storage if database is unavailable.
"""

import json
import uuid
from pathlib import Path
from typing import Any, Optional

from runner.db.connection import DatabaseConnection
from runner.logging import get_logger
from runner.models import EvaluationResult, TaskConfig

# Import health and calibration modules to avoid circular imports at module level
# We'll do conditional imports in methods that use them


logger = get_logger(__name__)


class Storage:
    """Manages storage of tasks, runs, and results."""

    def __init__(
        self,
        db_host: str = "localhost",
        db_port: int = 5432,
        db_name: str = "agentbench",
        db_user: str = "postgres",
        db_password: str = "postgres",
        fallback_dir: str = "results",
    ):
        """
        Initialize storage.

        Args:
            db_host: PostgreSQL host
            db_port: PostgreSQL port
            db_name: Database name
            db_user: Database user
            db_password: Database password
            fallback_dir: Directory for file-based fallback
        """
        self.db_connected = False
        self.fallback_dir = Path(fallback_dir)
        self.fallback_dir.mkdir(parents=True, exist_ok=True)

        try:
            self.db = DatabaseConnection.get_instance(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password,
            )

            # Test connection
            self.db.execute("SELECT 1")
            self.db_connected = True
            logger.info("Database storage initialized", db_host=db_host, db_name=db_name)

        except Exception as e:
            logger.warning(
                "Failed to connect to database, using file-based storage",
                error=str(e),
                fallback_dir=str(self.fallback_dir),
            )
            self.db = None

    def store_task(self, task_config: TaskConfig) -> bool:
        """
        Store task metadata.

        Args:
            task_config: Task configuration

        Returns:
            True if successful
        """
        if not self.db_connected:
            return self._store_task_fallback(task_config)

        try:
            query = """
                INSERT INTO tasks
                (id, name, category, difficulty, version, description, timeout, docker_image)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET updated_at = CURRENT_TIMESTAMP
            """

            self.db.execute(
                query,
                (
                    task_config.id,
                    task_config.name,
                    task_config.category.value,
                    task_config.difficulty.value,
                    task_config.version,
                    task_config.description,
                    task_config.timeout,
                    task_config.docker_image,
                ),
            )

            logger.debug("Task stored", task_id=task_config.id)
            return True

        except Exception as e:
            logger.warning("Failed to store task in database", task=task_config.id, error=str(e))
            return self._store_task_fallback(task_config)

    def _store_task_fallback(self, task_config: TaskConfig) -> bool:
        """Fallback file-based task storage."""
        try:
            task_dir = self.fallback_dir / "tasks" / task_config.id
            task_dir.mkdir(parents=True, exist_ok=True)

            with open(task_dir / "metadata.json", "w") as f:
                json.dump(
                    {
                        "id": task_config.id,
                        "name": task_config.name,
                        "category": task_config.category.value,
                        "difficulty": task_config.difficulty.value,
                    },
                    f,
                )

            return True
        except Exception as e:
            logger.error("Fallback task storage failed", error=str(e))
            return False

    def store_agent(
        self,
        agent_id: str,
        agent_name: str,
        agent_type: str,
        model: str,
        config: dict[str, Any],
    ) -> Optional[int]:
        """
        Store agent metadata.

        Args:
            agent_id: Agent identifier
            agent_name: Human-readable agent name
            agent_type: Type of agent (openai, ollama, etc.)
            model: Model name
            config: Agent configuration as dict

        Returns:
            Agent database ID or None if failed
        """
        if not self.db_connected:
            return None

        try:
            query = """
                INSERT INTO agents (name, type, model, config)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name) DO NOTHING
                RETURNING id
            """

            result = self.db.execute(
                query, (agent_name, agent_type, model, json.dumps(config)), fetch=True
            )

            if result:
                return result[0][0]

            # If already exists, get existing ID
            query = "SELECT id FROM agents WHERE name = %s"
            result = self.db.execute(query, (agent_name,), fetch=True)
            return result[0][0] if result else None

        except Exception as e:
            logger.warning("Failed to store agent", agent=agent_name, error=str(e))
            return None

    def start_run(self, task_id: str, agent_id: int) -> str:
        """
        Start a new run record.

        Args:
            task_id: Task being run
            agent_id: Agent running the task

        Returns:
            Run ID
        """
        run_id = str(uuid.uuid4())

        if not self.db_connected:
            return run_id

        try:
            query = """
                INSERT INTO runs (id, task_id, agent_id, started_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            """

            self.db.execute(query, (run_id, task_id, agent_id))
            logger.debug("Run started", run_id=run_id, task=task_id)

        except Exception as e:
            logger.warning("Failed to start run in database", run_id=run_id, error=str(e))

        return run_id

    def store_result(
        self,
        run_id: str,
        result: EvaluationResult,
    ) -> bool:
        """
        Store evaluation result.

        Args:
            run_id: Run ID
            result: Evaluation result

        Returns:
            True if successful
        """
        if not self.db_connected:
            return self._store_result_fallback(run_id, result)

        try:
            query = """
                INSERT INTO results (run_id, passed, score, test_output, test_details)
                VALUES (%s, %s, %s, %s, %s)
            """

            self.db.execute(
                query,
                (
                    run_id,
                    result.passed,
                    result.score,
                    result.test_output,
                    json.dumps(result.details),
                ),
            )

            logger.debug("Result stored", run_id=run_id, passed=result.passed)
            return True

        except Exception as e:
            logger.warning("Failed to store result in database", run_id=run_id, error=str(e))
            return self._store_result_fallback(run_id, result)

    def _store_result_fallback(self, run_id: str, result: EvaluationResult) -> bool:
        """Fallback file-based result storage."""
        try:
            result_dir = self.fallback_dir / run_id
            result_dir.mkdir(parents=True, exist_ok=True)

            with open(result_dir / "result.json", "w") as f:
                json.dump(result.model_dump(), f, default=str)

            return True
        except Exception as e:
            logger.error("Fallback result storage failed", error=str(e))
            return False

    def store_replay(
        self,
        run_id: str,
        replay_data: dict[str, Any],
    ) -> bool:
        """
        Store execution replay trace.

        Args:
            run_id: Run ID
            replay_data: Replay trace as dictionary

        Returns:
            True if successful
        """
        if not self.db_connected:
            return self._store_replay_fallback(run_id, replay_data)

        try:
            query = """
                INSERT INTO replays (run_id, data)
                VALUES (%s, %s)
            """

            self.db.execute(query, (run_id, json.dumps(replay_data)))
            logger.debug("Replay stored", run_id=run_id)
            return True

        except Exception as e:
            logger.warning("Failed to store replay in database", run_id=run_id, error=str(e))
            return self._store_replay_fallback(run_id, replay_data)

    def _store_replay_fallback(self, run_id: str, replay_data: dict[str, Any]) -> bool:
        """Fallback file-based replay storage."""
        try:
            replay_dir = self.fallback_dir / run_id
            replay_dir.mkdir(parents=True, exist_ok=True)

            with open(replay_dir / "replay.json", "w") as f:
                json.dump(replay_data, f, default=str, indent=2)

            return True
        except Exception as e:
            logger.error("Fallback replay storage failed", error=str(e))
            return False

    def store_execution_metrics(
        self,
        run_id: str,
        commands_executed: int,
        files_created: int,
        files_modified: int,
        tokens_used: int = 0,
        cost: float = 0.0,
        memory_peak_mb: Optional[float] = None,
    ) -> bool:
        """
        Store execution metrics.

        Args:
            run_id: Run ID
            commands_executed: Number of commands executed
            files_created: Number of files created
            files_modified: Number of files modified
            tokens_used: Total tokens used
            cost: Estimated cost
            memory_peak_mb: Peak memory usage

        Returns:
            True if successful
        """
        if not self.db_connected:
            return False

        try:
            query = """
                INSERT INTO execution_metrics
                (run_id, commands_executed, files_created,
                 files_modified, tokens_used, cost, memory_peak_mb)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            self.db.execute(
                query,
                (
                    run_id,
                    commands_executed,
                    files_created,
                    files_modified,
                    tokens_used,
                    cost,
                    memory_peak_mb,
                ),
            )

            return True

        except Exception as e:
            logger.warning("Failed to store metrics", run_id=run_id, error=str(e))
            return False

    def complete_run(self, run_id: str, success: bool, duration: float) -> bool:
        """
        Mark a run as complete.

        Args:
            run_id: Run ID
            success: Whether run succeeded
            duration: Execution duration in seconds

        Returns:
            True if successful
        """
        if not self.db_connected:
            return False

        try:
            query = """
                UPDATE runs
                SET ended_at = CURRENT_TIMESTAMP, success = %s, duration = %s
                WHERE id = %s
            """

            self.db.execute(query, (success, duration, run_id))
            return True

        except Exception as e:
            logger.warning("Failed to complete run", run_id=run_id, error=str(e))
            return False

    def get_task_stats(self, task_id: str) -> dict[str, Any]:
        """
        Get statistics for a task.

        Args:
            task_id: Task ID

        Returns:
            Statistics dictionary
        """
        if not self.db_connected:
            return {
                "total_runs": 0,
                "pass_rate": 0.0,
                "avg_duration": 0.0,
                "error": "Database not connected",
            }

        try:
            query = """
                SELECT
                    COUNT(*) as total_runs,
                    SUM(CASE WHEN r.success THEN 1 ELSE 0 END) as passes,
                    AVG(r.duration) as avg_duration,
                    STDDEV(r.duration) as std_duration
                FROM runs r
                WHERE r.task_id = %s
            """

            result = self.db.execute(query, (task_id,), fetch=True)

            if result and result[0]:
                row = result[0]
                total_runs = row[0] or 0
                passes = row[1] or 0
                avg_duration = row[2] or 0.0
                std_duration = row[3] or 0.0

                return {
                    "total_runs": total_runs,
                    "passes": passes,
                    "failures": total_runs - passes,
                    "pass_rate": (passes / total_runs) if total_runs > 0 else 0.0,
                    "avg_duration": avg_duration,
                    "std_duration": std_duration,
                }

        except Exception as e:
            logger.warning("Failed to get task stats", task_id=task_id, error=str(e))

        return {"error": "Failed to retrieve stats"}

    def get_agent_stats(self, agent_id: int) -> dict[str, Any]:
        """
        Get statistics for an agent.

        Args:
            agent_id: Agent ID

        Returns:
            Statistics dictionary
        """
        if not self.db_connected:
            return {
                "total_runs": 0,
                "pass_rate": 0.0,
                "total_cost": 0.0,
                "error": "Database not connected",
            }

        try:
            query = """
                SELECT
                    COUNT(*) as total_runs,
                    SUM(CASE WHEN r.success THEN 1 ELSE 0 END) as passes,
                    SUM(COALESCE(m.cost, 0)) as total_cost
                FROM runs r
                LEFT JOIN execution_metrics m ON r.id = m.run_id
                WHERE r.agent_id = %s
            """

            result = self.db.execute(query, (agent_id,), fetch=True)

            if result and result[0]:
                row = result[0]
                total_runs = row[0] or 0
                passes = row[1] or 0
                total_cost = row[2] or 0.0

                return {
                    "total_runs": total_runs,
                    "passes": passes,
                    "failures": total_runs - passes,
                    "pass_rate": (passes / total_runs) if total_runs > 0 else 0.0,
                    "total_cost": total_cost,
                    "avg_cost": (total_cost / total_runs) if total_runs > 0 else 0.0,
                }

        except Exception as e:
            logger.warning("Failed to get agent stats", agent_id=agent_id, error=str(e))

        return {"error": "Failed to retrieve stats"}

    def get_runs(
        self,
        task_id: Optional[str] = None,
        agent_id: Optional[int] = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Get list of runs.

        Args:
            task_id: Filter by task (optional)
            agent_id: Filter by agent (optional)
            limit: Maximum number of results

        Returns:
            List of run records
        """
        if not self.db_connected:
            return []

        try:
            query = (
                "SELECT id, task_id, agent_id, started_at, "
                "ended_at, success, duration FROM runs WHERE 1=1"
            )
            params = []

            if task_id:
                query += " AND task_id = %s"
                params.append(task_id)

            if agent_id:
                query += " AND agent_id = %s"
                params.append(agent_id)

            query += " ORDER BY started_at DESC LIMIT %s"
            params.append(limit)

            result = self.db.execute(query, tuple(params), fetch=True)

            if not result:
                return []

            runs = []
            for row in result:
                runs.append(
                    {
                        "id": row[0],
                        "task_id": row[1],
                        "agent_id": row[2],
                        "started_at": row[3].isoformat() if row[3] else None,
                        "ended_at": row[4].isoformat() if row[4] else None,
                        "success": row[5],
                        "duration": row[6],
                    }
                )

            return runs

        except Exception as e:
            logger.warning("Failed to get runs", error=str(e))
            return []

    def store_multi_run_metrics(
        self,
        task_id: str,
        agent_name: str,
        n_runs: int,
        success_rate: float,
        confidence_interval_lower: float,
        confidence_interval_upper: float,
        variance: float,
        mean_runtime: float,
        mean_tokens: int = 0,
        mean_cost: float = 0.0,
        reliability_score: float = 0.0,
    ) -> bool:
        """
        Store multi-run metrics for a task/agent combination.

        Args:
            task_id: Task identifier
            agent_name: Agent name
            n_runs: Number of runs
            success_rate: Success rate (0-1)
            confidence_interval_lower: Lower bound of CI
            confidence_interval_upper: Upper bound of CI
            variance: Variance of outcomes
            mean_runtime: Mean runtime
            mean_tokens: Mean token usage
            mean_cost: Mean cost
            reliability_score: Reliability score (0-100)

        Returns:
            True if successful
        """
        if not self.db_connected:
            return False

        try:
            query = """
                INSERT INTO multi_run_metrics
                (task_id, agent_name, n_runs, success_rate,
                 confidence_interval_lower, confidence_interval_upper,
                 variance, mean_runtime, mean_tokens, mean_cost, reliability_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (task_id, agent_name) DO UPDATE SET
                    n_runs = EXCLUDED.n_runs,
                    success_rate = EXCLUDED.success_rate,
                    confidence_interval_lower = EXCLUDED.confidence_interval_lower,
                    confidence_interval_upper = EXCLUDED.confidence_interval_upper,
                    variance = EXCLUDED.variance,
                    mean_runtime = EXCLUDED.mean_runtime,
                    mean_tokens = EXCLUDED.mean_tokens,
                    mean_cost = EXCLUDED.mean_cost,
                    reliability_score = EXCLUDED.reliability_score,
                    computed_at = CURRENT_TIMESTAMP
            """

            self.db.execute(
                query,
                (
                    task_id,
                    agent_name,
                    n_runs,
                    success_rate,
                    confidence_interval_lower,
                    confidence_interval_upper,
                    variance,
                    mean_runtime,
                    mean_tokens,
                    mean_cost,
                    reliability_score,
                ),
            )

            logger.debug(
                "Multi-run metrics stored",
                task_id=task_id,
                agent_name=agent_name,
                success_rate=success_rate,
            )
            return True

        except Exception as e:
            logger.warning("Failed to store multi-run metrics", error=str(e))
            return False

    def store_task_health(
        self,
        task_id: str,
        health_status: str,
        success_rate: float,
        variance: float,
        n_agents: int,
        n_runs_total: int,
        evidence: list[str],
        recommendations: list[str],
    ) -> bool:
        """
        Store task health analysis.

        Args:
            task_id: Task identifier
            health_status: Health status (healthy/flaky/broken/trivial/saturated)
            success_rate: Overall success rate
            variance: Variance across agents
            n_agents: Number of agents tested
            n_runs_total: Total runs across all agents
            evidence: List of evidence strings
            recommendations: List of recommendation strings

        Returns:
            True if successful
        """
        if not self.db_connected:
            return False

        try:
            evidence_str = " | ".join(evidence) if evidence else ""
            recommendations_str = " | ".join(recommendations) if recommendations else ""

            query = """
                INSERT INTO task_health
                (task_id, health_status, success_rate, variance,
                 n_agents, n_runs_total, evidence, recommendations)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (task_id) DO UPDATE SET
                    health_status = EXCLUDED.health_status,
                    success_rate = EXCLUDED.success_rate,
                    variance = EXCLUDED.variance,
                    n_agents = EXCLUDED.n_agents,
                    n_runs_total = EXCLUDED.n_runs_total,
                    evidence = EXCLUDED.evidence,
                    recommendations = EXCLUDED.recommendations,
                    analyzed_at = CURRENT_TIMESTAMP
            """

            self.db.execute(
                query,
                (
                    task_id,
                    health_status,
                    success_rate,
                    variance,
                    n_agents,
                    n_runs_total,
                    evidence_str,
                    recommendations_str,
                ),
            )

            logger.debug(
                "Task health stored",
                task_id=task_id,
                health_status=health_status,
            )
            return True

        except Exception as e:
            logger.warning("Failed to store task health", task_id=task_id, error=str(e))
            return False

    def store_task_difficulty_calibration(
        self,
        task_id: str,
        author_difficulty: Optional[str],
        empirical_difficulty: str,
        mean_success_rate: float,
        median_success_rate: float,
        n_agents: int,
        match: bool,
        recommendation: str,
        confidence: float,
    ) -> bool:
        """
        Store difficulty calibration analysis.

        Args:
            task_id: Task identifier
            author_difficulty: Author-assigned difficulty
            empirical_difficulty: Empirically estimated difficulty
            mean_success_rate: Mean success rate
            median_success_rate: Median success rate
            n_agents: Number of agents
            match: Whether author and empirical match
            recommendation: Recommendation string
            confidence: Confidence in calibration

        Returns:
            True if successful
        """
        if not self.db_connected:
            return False

        try:
            query = """
                INSERT INTO task_difficulty_calibration
                (task_id, author_difficulty, empirical_difficulty,
                 mean_success_rate, median_success_rate, n_agents,
                 match, recommendation, confidence)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (task_id) DO UPDATE SET
                    author_difficulty = EXCLUDED.author_difficulty,
                    empirical_difficulty = EXCLUDED.empirical_difficulty,
                    mean_success_rate = EXCLUDED.mean_success_rate,
                    median_success_rate = EXCLUDED.median_success_rate,
                    n_agents = EXCLUDED.n_agents,
                    match = EXCLUDED.match,
                    recommendation = EXCLUDED.recommendation,
                    confidence = EXCLUDED.confidence,
                    calibrated_at = CURRENT_TIMESTAMP
            """

            self.db.execute(
                query,
                (
                    task_id,
                    author_difficulty,
                    empirical_difficulty,
                    mean_success_rate,
                    median_success_rate,
                    n_agents,
                    match,
                    recommendation,
                    confidence,
                ),
            )

            logger.debug(
                "Task difficulty calibration stored",
                task_id=task_id,
                empirical_difficulty=empirical_difficulty,
            )
            return True

        except Exception as e:
            logger.warning("Failed to store difficulty calibration", task_id=task_id, error=str(e))
            return False

    def get_task_health(self, task_id: str) -> Optional[dict]:
        """
        Retrieve task health report.

        Args:
            task_id: Task identifier

        Returns:
            Health report dict or None
        """
        if not self.db_connected:
            return None

        try:
            query = """
                SELECT task_id, health_status, success_rate, variance,
                       n_agents, n_runs_total, evidence, recommendations, analyzed_at
                FROM task_health
                WHERE task_id = %s
            """

            result = self.db.execute(query, (task_id,), fetch=True)

            if not result:
                return None

            row = result[0]
            return {
                "task_id": row[0],
                "health_status": row[1],
                "success_rate": row[2],
                "variance": row[3],
                "n_agents": row[4],
                "n_runs_total": row[5],
                "evidence": row[6].split(" | ") if row[6] else [],
                "recommendations": row[7].split(" | ") if row[7] else [],
                "analyzed_at": row[8].isoformat() if row[8] else None,
            }

        except Exception as e:
            logger.warning("Failed to get task health", task_id=task_id, error=str(e))
            return None

    def get_all_task_health(self) -> list[dict]:
        """
        Retrieve all task health reports.

        Returns:
            List of health report dicts
        """
        if not self.db_connected:
            return []

        try:
            query = """
                SELECT task_id, health_status, success_rate, variance,
                       n_agents, n_runs_total, evidence, recommendations, analyzed_at
                FROM task_health
                ORDER BY health_status, task_id
            """

            result = self.db.execute(query, fetch=True)

            if not result:
                return []

            reports = []
            for row in result:
                reports.append(
                    {
                        "task_id": row[0],
                        "health_status": row[1],
                        "success_rate": row[2],
                        "variance": row[3],
                        "n_agents": row[4],
                        "n_runs_total": row[5],
                        "evidence": row[6].split(" | ") if row[6] else [],
                        "recommendations": row[7].split(" | ") if row[7] else [],
                        "analyzed_at": row[8].isoformat() if row[8] else None,
                    }
                )

            return reports

        except Exception as e:
            logger.warning("Failed to get all task health", error=str(e))
            return []

    def get_task_difficulty_calibration(self, task_id: str) -> Optional[dict]:
        """
        Retrieve difficulty calibration report.

        Args:
            task_id: Task identifier

        Returns:
            Calibration report dict or None
        """
        if not self.db_connected:
            return None

        try:
            query = """
                SELECT task_id, author_difficulty, empirical_difficulty,
                       mean_success_rate, median_success_rate, n_agents,
                       match, recommendation, confidence, calibrated_at
                FROM task_difficulty_calibration
                WHERE task_id = %s
            """

            result = self.db.execute(query, (task_id,), fetch=True)

            if not result:
                return None

            row = result[0]
            return {
                "task_id": row[0],
                "author_difficulty": row[1],
                "empirical_difficulty": row[2],
                "mean_success_rate": row[3],
                "median_success_rate": row[4],
                "n_agents": row[5],
                "match": row[6],
                "recommendation": row[7],
                "confidence": row[8],
                "calibrated_at": row[9].isoformat() if row[9] else None,
            }

        except Exception as e:
            logger.warning("Failed to get difficulty calibration", task_id=task_id, error=str(e))
            return None

    def get_mismatched_calibrations(self) -> list[dict]:
        """
        Get all difficulty calibrations with author/empirical mismatches.

        Returns:
            List of calibration dicts where match=False
        """
        if not self.db_connected:
            return []

        try:
            query = """
                SELECT task_id, author_difficulty, empirical_difficulty,
                       mean_success_rate, recommendation
                FROM task_difficulty_calibration
                WHERE match = FALSE
                ORDER BY task_id
            """

            result = self.db.execute(query, fetch=True)

            if not result:
                return []

            mismatches = []
            for row in result:
                mismatches.append(
                    {
                        "task_id": row[0],
                        "author_difficulty": row[1],
                        "empirical_difficulty": row[2],
                        "mean_success_rate": row[3],
                        "recommendation": row[4],
                    }
                )

            return mismatches

        except Exception as e:
            logger.warning("Failed to get mismatched calibrations", error=str(e))
            return []
