"""
Command-line interface for AgentBench.

Provides CLI commands for:
- Listing tasks
- Getting task information
- Validating tasks (Oracle and NOP patterns)
- Running tasks in Docker containers
- Running benchmarks with multiple runs
"""

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

try:
    import typer
    from typing_extensions import Annotated
except ImportError:
    print("Error: typer not installed. Install with: pip install typer")
    sys.exit(1)

from runner.executor import TaskExecutor
from runner.loader import TaskLoader
from runner.logging import get_logger
from runner.validator import TaskValidator

if TYPE_CHECKING:
    from runner.storage import Storage

logger = get_logger(__name__)
app = typer.Typer(help="AgentBench - Reliability-First Benchmark for AI Agents")


def get_storage() -> "Storage":
    """
    Get configured Storage instance from environment variables.

    Reads database connection parameters from:
    - DB_HOST: Database hostname (default: localhost)
    - DB_PORT: Database port (default: 5432)
    - DB_NAME: Database name (default: agentbench)
    - DB_USER: Database username (default: postgres)
    - DB_PASSWORD: Database password (default: postgres)

    Returns:
        Storage instance configured with environment variables
    """
    from runner.storage import Storage

    return Storage(
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_name=os.getenv("DB_NAME", "agentbench"),
        db_user=os.getenv("DB_USER", "postgres"),
        db_password=os.getenv("DB_PASSWORD", "postgres"),
    )


@app.command()
def list(
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Show detailed info")] = False,
):
    """List all available tasks."""
    try:
        loader = TaskLoader("tasks")
        tasks = loader.discover_tasks()

        if not tasks:
            typer.echo("No tasks found.")
            return

        typer.echo(f"Found {len(tasks)} tasks:\n")

        for task_id in sorted(tasks):
            try:
                metadata = loader.validate_task_structure(task_id)
                config = metadata.config
                status = "✓" if metadata.is_valid else "✗"

                typer.echo(f"{status} {task_id}")

                if verbose:
                    typer.echo(f"  Name: {config.name}")
                    typer.echo(f"  Category: {config.category}")
                    typer.echo(f"  Difficulty: {config.difficulty}")
                    if config.description:
                        typer.echo(f"  Description: {config.description}")
            except Exception as e:
                typer.echo(f"✗ {task_id}: {e}")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)


@app.command()
def info(task_id: str):
    """Show detailed information about a task."""
    try:
        loader = TaskLoader("tasks")
        metadata = loader.validate_task_structure(task_id)
        config = metadata.config

        typer.echo(f"\nTask: {task_id}")
        typer.echo(f"Name: {config.name}")
        typer.echo(f"Description: {config.description}")
        typer.echo(f"Category: {config.category}")
        typer.echo(f"Difficulty: {config.difficulty}")
        typer.echo(f"Version: {config.version}")
        typer.echo(f"Timeout: {config.timeout}s")
        typer.echo(f"Docker Image: {config.docker_image}")
        typer.echo(f"Expected Output: {', '.join(config.expected_output_files)}")

        if metadata.validation_errors:
            typer.echo("\nValidation Errors:")
            for error in metadata.validation_errors:
                typer.echo(f"  - {error}")
        else:
            typer.echo("\nStatus: Valid ✓")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)


@app.command()
def validate(
    task_id: Annotated[str, typer.Argument(help="Task ID to validate")] = None,
    all_tasks: Annotated[bool, typer.Option("--all", help="Validate all tasks")] = False,
):
    """Validate task(s) using Oracle and NOP patterns."""
    try:
        validator = TaskValidator("tasks")

        if all_tasks:
            typer.echo("Validating all tasks...\n")
            results = validator.validate_all()
        else:
            if not task_id:
                typer.echo("Error: Specify task_id or use --all", err=True)
                sys.exit(1)

            typer.echo(f"Validating task: {task_id}\n")
            results = validator.validate_all([task_id])

        # Display results
        for tid, result in sorted(results.items()):
            status = "PASS" if result["valid"] else "FAIL"
            typer.echo(f"[{status}] {tid}")

            oracle_status = "PASS" if result["oracle"][0] else "FAIL"
            nop_status = "PASS" if result["nop"][0] else "FAIL"

            typer.echo(f"  Oracle: {oracle_status}")
            if not result["oracle"][0]:
                typer.echo(f"    {result['oracle'][1]}")

            typer.echo(f"  NOP: {nop_status}")
            if not result["nop"][0]:
                typer.echo(f"    {result['nop'][1]}")

            typer.echo()

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)


@app.command()
def run(
    task_id: Annotated[str, typer.Argument(help="Task ID to run")],
    agent_output: Annotated[
        str, typer.Option("--agent-output", "-o", help="Path to agent output files")
    ] = None,
    timeout: Annotated[
        int, typer.Option("--timeout", "-t", help="Execution timeout in seconds")
    ] = None,
):
    """Run a task in Docker container."""
    try:
        executor = TaskExecutor()

        typer.echo(f"Running task: {task_id}")

        agent_output_path = None
        if agent_output:
            agent_output_path = Path(agent_output)
            if not agent_output_path.exists():
                typer.echo(f"Error: Agent output path not found: {agent_output}", err=True)
                sys.exit(1)

        result = executor.execute_task(
            task_id, agent_output_path=agent_output_path, timeout=timeout
        )

        typer.echo()
        typer.echo("=" * 60)
        typer.echo(f"Task: {result.task_id}")
        typer.echo(f"Status: {'PASSED ✓' if result.passed else 'FAILED ✗'}")
        typer.echo(f"Score: {result.score:.1%}")
        typer.echo("=" * 60)
        typer.echo("\nTest Output:")
        typer.echo(result.test_output)

        if result.details:
            typer.echo("\nDetails:")
            for key, value in result.details.items():
                if key != "test_results":
                    typer.echo(f"  {key}: {value}")

        sys.exit(0 if result.passed else 1)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)


@app.command()
def agent_run(
    task_id: Annotated[str, typer.Argument(help="Task ID to solve")],
    agent_type: Annotated[
        str, typer.Option("--agent", "-a", help="Agent type (openai, ollama)")
    ] = "openai",
    model: Annotated[str, typer.Option("--model", "-m", help="Model name")] = "gpt-4",
    api_key: Annotated[str, typer.Option("--api-key", help="API key")] = None,
    timeout: Annotated[int, typer.Option("--timeout", "-t", help="Timeout in seconds")] = 300,
):
    """Run a task using an AI agent."""
    import asyncio
    from runner.agents.base import AgentConfig, AgentType
    from runner.agents.openai_agent import OpenAIAgent
    from runner.agents.ollama_agent import OllamaAgent
    from runner.loader import TaskLoader

    try:
        # Initialize storage from environment
        storage = get_storage()

        # Load task
        loader = TaskLoader("tasks")
        metadata = loader.validate_task_structure(task_id)

        if not metadata.is_valid:
            typer.echo(f"Error: Task {task_id} is not valid", err=True)
            for error in metadata.validation_errors:
                typer.echo(f"  - {error}", err=True)
            sys.exit(1)

        # Store task metadata in database
        try:
            logger.info("Storing task metadata", task_id=task_id)
            storage.store_task(metadata.config)
            typer.echo("✓ Task metadata stored")
        except Exception as e:
            logger.warning("Failed to store task metadata", error=str(e))

        # Load task files
        task_dir = loader.get_task_path(task_id)
        instruction_file = task_dir / "instruction.md"

        if not instruction_file.exists():
            typer.echo(f"Error: No instruction.md for {task_id}", err=True)
            sys.exit(1)

        instruction = instruction_file.read_text()

        # Load environment files
        environment_files = {}
        env_dir = task_dir / "environment"
        if env_dir.exists():
            for file_path in env_dir.glob("**/*"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(env_dir)
                    environment_files[str(rel_path)] = file_path.read_text()

        # Create agent
        agent_type_enum = AgentType(agent_type.lower())
        config = AgentConfig(
            agent_type=agent_type_enum, model=model, api_key=api_key or None, timeout=timeout
        )

        if agent_type_enum == AgentType.OPENAI:
            if not config.api_key:
                typer.echo("Error: --api-key required for OpenAI agent", err=True)
                sys.exit(1)
            agent = OpenAIAgent(config)
        elif agent_type_enum == AgentType.OLLAMA:
            agent = OllamaAgent(config)
        else:
            typer.echo(f"Error: Unknown agent type {agent_type}", err=True)
            sys.exit(1)

        # Store agent metadata in database
        agent_db_id = storage.store_agent(
            agent_id=f"{agent_type}-{model}",
            agent_name=f"{agent_type}-{model}",
            agent_type=agent_type_enum.value,
            model=model,
            config={"timeout": timeout},
        )

        if agent_db_id:
            logger.info("Agent stored in database", agent_db_id=agent_db_id)
            typer.echo(f"✓ Agent registered (ID: {agent_db_id})")
        else:
            logger.warning("Failed to store agent in database")

        typer.echo()
        typer.echo(f"Running {task_id} with {agent_type}/{model}...")
        typer.echo()

        # Start run in database
        run_id = None
        if agent_db_id and storage.db_connected:
            run_id = storage.start_run(task_id, agent_db_id)
            logger.info("Run started in database", run_id=run_id)

        # Run agent
        result = asyncio.run(
            agent.solve(
                task_id=task_id,
                instruction=instruction,
                environment_files=environment_files,
                timeout=timeout,
            )
        )

        # Store result and complete run in database
        if run_id and storage.db_connected:
            try:
                # Create EvaluationResult for storage
                from runner.models import EvaluationResult

                eval_result = EvaluationResult(
                    task_id=task_id,
                    passed=result.success,
                    score=1.0 if result.success else 0.0,
                    test_output=result.error_message or "Agent execution completed",
                    details={
                        "commands_executed": result.commands_executed,
                        "files_created": result.files_created,
                        "token_usage": result.token_usage or 0,
                        "cost": result.cost or 0.0,
                    },
                )

                storage.store_result(run_id, eval_result)
                storage.complete_run(run_id, result.success, result.duration)

                # Store execution metrics
                storage.store_execution_metrics(
                    run_id=run_id,
                    commands_executed=result.commands_executed,
                    files_created=result.files_created,
                    files_modified=0,
                    tokens_used=result.token_usage or 0,
                    cost=result.cost or 0.0,
                )

                logger.info("Run completed and stored in database", run_id=run_id)
            except Exception as e:
                logger.warning("Failed to store run results", error=str(e))

        # Display results
        typer.echo()
        typer.echo("=" * 60)
        typer.echo(f"Agent: {result.agent_name} ({result.agent_type.value})")
        typer.echo(f"Task: {result.task_id}")
        typer.echo(f"Status: {'SUCCESS ✓' if result.success else 'FAILED ✗'}")
        typer.echo(f"Duration: {result.duration:.1f}s")
        typer.echo(f"Commands: {result.commands_executed}")
        typer.echo(f"Files Created: {result.files_created}")

        if result.token_usage:
            typer.echo(f"Tokens: {result.token_usage}")
            typer.echo(f"Cost: ${result.cost:.4f}")

        if result.error_message:
            typer.echo(f"Error: {result.error_message}")

        typer.echo("=" * 60)

        if run_id and storage.db_connected:
            typer.echo()
            typer.echo(f"✓ Results stored in database (Run ID: {run_id})")

        sys.exit(0 if result.success else 1)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)


@app.command()
def bench(
    task_id: Annotated[str, typer.Argument(help="Task ID to benchmark")],
    agent: Annotated[str, typer.Option("--agent", "-a", help="Agent name")] = "openai",
    runs: Annotated[int, typer.Option("--runs", "-r", help="Number of runs")] = 10,
    timeout: Annotated[
        int, typer.Option("--timeout", "-t", help="Timeout per run (seconds)")
    ] = None,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Verbose output")] = False,
):
    """Run multi-run benchmark and compute reliability score."""
    try:
        from runner.multi_run import MultiRunExecutor
        from runner.agents.base import BaseAgent, AgentConfig, AgentType

        typer.echo(f"Benchmarking task: {task_id}")
        typer.echo(f"Agent: {agent}")
        typer.echo(f"Runs: {runs}")
        typer.echo()

        # Initialize storage from environment
        storage = get_storage()

        # Load task configuration and store in database
        loader = TaskLoader("tasks")
        try:
            task_metadata = loader.validate_task_structure(task_id)
            if task_metadata.is_valid:
                logger.info("Storing task metadata", task_id=task_id)
                storage.store_task(task_metadata.config)
                typer.echo("✓ Task metadata stored in database")
            else:
                logger.warning("Task validation failed", errors=task_metadata.validation_errors)
        except Exception as e:
            logger.warning("Failed to store task metadata", error=str(e))

        # Create a mock agent config
        # In real usage, this would be loaded from configuration
        agent_config = AgentConfig(
            agent_type=AgentType.OPENAI if agent.lower() == "openai" else AgentType.OLLAMA,
            model="gpt-4" if agent.lower() == "openai" else "llama2",
            name=agent,
        )

        # Store agent metadata in database
        agent_db_id = storage.store_agent(
            agent_id=f"{agent}-{agent_config.model}",
            agent_name=f"{agent}-{agent_config.model}",
            agent_type=agent_config.agent_type.value,
            model=agent_config.model,
            config={},
        )

        if agent_db_id:
            logger.info("Agent stored in database", agent_db_id=agent_db_id)
            typer.echo(f"✓ Agent registered in database (ID: {agent_db_id})")
        else:
            logger.warning("Failed to store agent in database")
            typer.echo("⚠ Using file-based storage fallback")

        typer.echo()

        # Create a basic agent wrapper
        class SimpleAgent(BaseAgent):
            async def solve(self, task_id, instruction, environment_files, timeout):
                pass

        agent_obj = SimpleAgent(agent_config)

        # Create executor and execute multi-run with storage
        executor = MultiRunExecutor(max_concurrent=3)

        # Use progress callback
        def progress_callback(completed: int, total: int):
            pct = (completed / total) * 100
            typer.echo(f"  Progress: {completed}/{total} ({pct:.0f}%)", nl=False)
            typer.echo("\r", nl=False)

        result = executor.execute_multi_run(
            task_id=task_id,
            agent=agent_obj,
            n_runs=runs,
            timeout=timeout,
            use_parallelization=False,
            progress_callback=progress_callback,
            storage=storage,
        )

        typer.echo()
        typer.echo()
        typer.echo("=" * 70)
        typer.echo(f"Benchmark Results: {task_id}")
        typer.echo("=" * 70)
        typer.echo(f"Agent: {result.agent_name}")
        typer.echo(f"Total Runs: {result.n_runs}")
        typer.echo(f"Passed: {result.success_count}")
        typer.echo(f"Failed: {result.failure_count}")
        typer.echo(f"Success Rate: {result.success_rate:.1%}")
        typer.echo(f"Reliability Score: {result.reliability_score:.2f}/100")
        typer.echo(f"Mean Runtime: {result.mean_runtime:.2f}s")

        if result.mean_cost > 0:
            typer.echo(f"Mean Cost: ${result.mean_cost:.4f}")

        if verbose:
            typer.echo()
            typer.echo("Detailed Results:")
            for i, run_result in enumerate(result.runs, 1):
                status = "✓" if run_result.passed else "✗"
                typer.echo(f"  Run {i}: {status} (score: {run_result.score:.1%})")

        typer.echo("=" * 70)

        if storage.db_connected:
            typer.echo()
            typer.echo("✓ Results stored in PostgreSQL database")
        else:
            typer.echo()
            typer.echo("⚠ Results stored in file-based storage (database unavailable)")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


@app.command()
def health(
    task_id: Annotated[
        str, typer.Option("--task", "-t", help="Task ID (optional, defaults to all)")
    ] = None,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Verbose output")] = False,
):
    """Analyze task health classifications."""
    try:
        from runner.storage import Storage

        storage = Storage()

        if task_id:
            # Analyze single task
            health_report = storage.get_task_health(task_id)

            if not health_report:
                typer.echo(f"No health data found for {task_id}", err=True)
                typer.echo("Run benchmark first with 'agentbench bench'", err=True)
                sys.exit(1)

            typer.echo()
            typer.echo("=" * 70)
            typer.echo(f"Task Health: {task_id}")
            typer.echo("=" * 70)
            typer.echo(f"Status: {health_report['health_status'].upper()}")
            typer.echo(f"Success Rate: {health_report['success_rate']:.1%}")
            typer.echo(f"Variance: {health_report['variance']:.3f}")
            typer.echo(f"Agents Tested: {health_report['n_agents']}")
            typer.echo(f"Total Runs: {health_report['n_runs_total']}")

            typer.echo()
            typer.echo("Evidence:")
            for evidence in health_report["evidence"]:
                typer.echo(f"  • {evidence}")

            typer.echo()
            typer.echo("Recommendations:")
            for rec in health_report["recommendations"]:
                typer.echo(f"  • {rec}")

            typer.echo("=" * 70)

        else:
            # Analyze all tasks
            all_health = storage.get_all_task_health()

            if not all_health:
                typer.echo("No health data found. Run benchmarks first.", err=True)
                sys.exit(1)

            # Group by status
            by_status = {}
            for report in all_health:
                status = report["health_status"]
                if status not in by_status:
                    by_status[status] = []
                by_status[status].append(report)

            typer.echo()
            typer.echo("=" * 70)
            typer.echo("Benchmark Health Summary")
            typer.echo("=" * 70)

            for status in ["healthy", "flaky", "broken", "trivial", "saturated"]:
                tasks = by_status.get(status, [])
                count = len(tasks)

                icon = {
                    "healthy": "✓",
                    "flaky": "⚠",
                    "broken": "✗",
                    "trivial": "○",
                    "saturated": "⬆",
                }[status]

                typer.echo(f"{icon} {status.upper():12} {count:3} tasks")

                if verbose and tasks:
                    for task in tasks[:3]:  # Show top 3
                        typer.echo(f"    • {task['task_id']} ({task['success_rate']:.1%})")

            typer.echo("=" * 70)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


@app.command()
def calibrate(
    task_id: Annotated[
        str, typer.Option("--task", "-t", help="Task ID (optional, defaults to all)")
    ] = None,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Verbose output")] = False,
):
    """Analyze difficulty calibrations."""
    try:
        from runner.storage import Storage

        storage = Storage()

        if task_id:
            # Analyze single task
            calibration = storage.get_task_difficulty_calibration(task_id)

            if not calibration:
                typer.echo(f"No calibration data found for {task_id}", err=True)
                sys.exit(1)

            typer.echo()
            typer.echo("=" * 70)
            typer.echo(f"Difficulty Calibration: {task_id}")
            typer.echo("=" * 70)

            if calibration["author_difficulty"]:
                typer.echo(f"Author Difficulty: {calibration['author_difficulty'].upper()}")
            else:
                typer.echo("Author Difficulty: NOT SET")

            typer.echo(f"Empirical Difficulty: {calibration['empirical_difficulty'].upper()}")
            typer.echo(f"Mean Success Rate: {calibration['mean_success_rate']:.1%}")
            typer.echo(f"Agents Tested: {calibration['n_agents']}")
            typer.echo(f"Confidence: {calibration['confidence']:.1%}")

            match_str = "✓ MATCH" if calibration["match"] else "✗ MISMATCH"
            typer.echo(f"Status: {match_str}")

            if calibration["recommendation"]:
                typer.echo()
                typer.echo("Recommendation:")
                typer.echo(f"  {calibration['recommendation']}")

            typer.echo("=" * 70)

        else:
            # Analyze all tasks
            mismatches = storage.get_mismatched_calibrations()
            all_calibrations = (
                storage.db.execute("SELECT COUNT(*) FROM task_difficulty_calibration", fetch=True)
                if storage.db_connected
                else [(0,)]
            )

            total_count = all_calibrations[0][0] if all_calibrations else 0
            matched_count = total_count - len(mismatches) if total_count > 0 else 0

            typer.echo()
            typer.echo("=" * 70)
            typer.echo("Difficulty Calibration Summary")
            typer.echo("=" * 70)
            typer.echo(f"Total Tasks: {total_count}")
            typer.echo(f"Matched: {matched_count}")
            typer.echo(f"Mismatched: {len(mismatches)}")

            if matched_count > 0:
                match_rate = (matched_count / total_count) * 100
                typer.echo(f"Match Rate: {match_rate:.1f}%")

            if mismatches:
                typer.echo()
                typer.echo("Mismatched Tasks (need re-rating):")
                for mismatch in mismatches[:10]:  # Show top 10
                    author = mismatch["author_difficulty"] or "?"
                    empirical = mismatch["empirical_difficulty"]
                    sr = mismatch["mean_success_rate"]
                    typer.echo(
                        f"  • {mismatch['task_id']:30} "
                        f"author={author:8} empirical={empirical:8} "
                        f"(success={sr:.1%})"
                    )

            typer.echo("=" * 70)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


@app.command()
def results(
    task_id: Annotated[str, typer.Argument(help="Task ID to get results for")],
):
    """Show results and statistics for a task."""
    try:
        from runner.storage import Storage

        storage = Storage()
        stats = storage.get_task_stats(task_id)

        typer.echo(f"\nTask: {task_id}")
        typer.echo("=" * 60)

        if "error" in stats:
            typer.echo(f"Error: {stats['error']}")
        else:
            typer.echo(f"Total Runs: {stats.get('total_runs', 0)}")
            typer.echo(f"Passed: {stats.get('passes', 0)}")
            typer.echo(f"Failed: {stats.get('failures', 0)}")
            typer.echo(f"Pass Rate: {stats.get('pass_rate', 0):.1%}")
            typer.echo(f"Avg Duration: {stats.get('avg_duration', 0):.2f}s")
            typer.echo(f"Std Dev: {stats.get('std_duration', 0):.2f}s")

        typer.echo("=" * 60)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)


@app.command()
def replay(
    run_id: Annotated[str, typer.Argument(help="Run ID to replay")],
):
    """Show execution replay trace."""
    try:
        from runner.replay import ReplayStorage

        storage = ReplayStorage("results")
        trace = storage.load_trace(run_id)

        if not trace:
            typer.echo(f"Error: Replay not found for run {run_id}", err=True)
            sys.exit(1)

        typer.echo(f"\nExecution Replay: {run_id}")
        typer.echo("=" * 80)
        typer.echo(f"Task: {trace.task_id}")
        typer.echo(f"Agent: {trace.agent_name} ({trace.agent_type})")
        typer.echo(f"Duration: {trace.duration:.1f}s")
        typer.echo(f"Status: {'SUCCESS ✓' if trace.success else 'FAILED ✗'}")

        if trace.error_message:
            typer.echo(f"Error: {trace.error_message}")

        typer.echo("\nEvents:")
        typer.echo("-" * 80)

        for event in trace.events:
            timestamp_offset = event.timestamp - trace.events[0].timestamp if trace.events else 0
            typer.echo(f"[{timestamp_offset:6.2f}s] {event.type.value:20} | {event.content[:60]}")

        typer.echo("=" * 80)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    app()
