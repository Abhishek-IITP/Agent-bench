"""
Task executor for running tasks in Docker containers.

Implements the full execution lifecycle:
1. Create container from base image
2. Copy environment/ into container
3. Copy agent output into container
4. Run tests inside container
5. Collect results
6. Destroy container
"""

from pathlib import Path
from typing import Optional

from runner.docker_client import DockerClient
from runner.loader import TaskLoader
from runner.logging import get_logger
from runner.models import EvaluationResult

logger = get_logger(__name__)


class TaskExecutor:
    """Executes tasks inside Docker containers."""

    def __init__(
        self,
        dockerfile_path: str = "Dockerfile",
        base_image: str = "agentbench-base:latest",
    ):
        """
        Initialize the executor.

        Args:
            dockerfile_path: Path to Dockerfile for building base image
            base_image: Name of base image (must be built first)
        """
        self.docker_client = DockerClient()
        self.dockerfile_path = dockerfile_path
        self.base_image = base_image
        self.loader = TaskLoader("tasks")

    def build_base_image(self) -> str:
        """
        Build the base Docker image.

        Returns:
            Image ID
        """
        logger.info("Building base Docker image", dockerfile=self.dockerfile_path)
        return self.docker_client.build_image(
            dockerfile_path=self.dockerfile_path,
            image_name="agentbench-base",
            tag="latest",
        )

    def execute_task(
        self,
        task_id: str,
        agent_output_path: Optional[Path] = None,
        timeout: Optional[int] = None,
    ) -> EvaluationResult:
        """
        Execute a task in a Docker container.

        Full lifecycle:
        1. Create container from base image
        2. Copy task environment into container
        3. Copy agent output (if provided)
        4. Run tests
        5. Destroy container

        Args:
            task_id: Task identifier
            agent_output_path: Optional path to agent's output files
            timeout: Execution timeout in seconds

        Returns:
            EvaluationResult with pass/fail and details
        """
        logger.info("Executing task", task_id=task_id, timeout=timeout)

        container_id = None

        try:
            # Load task configuration
            task_dir = self.loader.get_task_path(task_id)
            task_metadata = self.loader.validate_task_structure(task_id)
            task_config = task_metadata.config

            if not task_metadata.is_valid:
                return EvaluationResult(
                    task_id=task_id,
                    passed=False,
                    score=0.0,
                    test_output="Task structure invalid",
                    details={"errors": task_metadata.validation_errors},
                )

            # Use task timeout if not specified
            if timeout is None:
                timeout = task_config.timeout

            # Create container with resource limits
            container_id = self.docker_client.create_container(
                image_name=self.base_image,
                memory_limit="512m",
            )
            logger.debug("Container created", container_id=container_id)

            # Copy environment into container
            environment_dir = task_dir / "environment"
            if environment_dir.exists():
                self.docker_client.copy_to_container(
                    container_id,
                    environment_dir,
                    "/workspace",
                )
                # Move files from environment subdirectory to workspace root
                exit_code, _, stderr = self.docker_client.run_command(
                    container_id,
                    "mv /workspace/environment/* /workspace/ 2>/dev/null || true",
                    timeout=10,
                )
                if exit_code != 0:
                    logger.warning("Failed to move environment files", stderr=stderr)

            # Copy agent output if provided
            if agent_output_path and agent_output_path.exists():
                self.docker_client.copy_to_container(
                    container_id,
                    agent_output_path,
                    "/workspace",
                )
                logger.debug("Agent output copied to container")
                code, stdout, _ = self.docker_client.run_command(container_id, "ls -la /workspace")
                logger.info("WORKSPACE CONTENTS", stdout=stdout)

            # Run tests
            tests_dir = task_dir / "tests"
            test_results = []

            if not tests_dir.exists():
                return EvaluationResult(
                    task_id=task_id,
                    passed=False,
                    score=0.0,
                    test_output="No tests found",
                    details={"error": "tests/ directory not found"},
                )

            test_files = sorted(tests_dir.glob("*.py"))

            if not test_files:
                return EvaluationResult(
                    task_id=task_id,
                    passed=False,
                    score=0.0,
                    test_output="No test files found",
                    details={"error": "No .py test files in tests/ directory"},
                )

            for test_file in test_files:
                logger.info("Running test", test=test_file.name, container=container_id)

                # Copy test file to container
                self.docker_client.copy_to_container(
                    container_id,
                    test_file,
                    "/workspace",
                )

                # Run the test
                exit_code, stdout, stderr = self.docker_client.run_command(
                    container_id,
                    f"python /workspace/{test_file.name}",
                    timeout=timeout,
                )

                test_results.append(
                    {
                        "test": test_file.name,
                        "exit_code": exit_code,
                        "stdout": stdout,
                        "stderr": stderr,
                    }
                )

                logger.debug(
                    "Test executed",
                    test=test_file.name,
                    exit_code=exit_code,
                )

            # Determine pass/fail
            all_passed = all(result["exit_code"] == 0 for result in test_results)

            # Collect test output with better formatting
            test_output = self._format_test_output(test_results)

            logger.info(
                "Task execution complete",
                task_id=task_id,
                passed=all_passed,
                num_tests=len(test_results),
            )

            return EvaluationResult(
                task_id=task_id,
                passed=all_passed,
                score=1.0 if all_passed else 0.0,
                test_output=test_output,
                details={
                    "test_results": test_results,
                    "num_tests": len(test_results),
                    "passed_tests": sum(1 for r in test_results if r["exit_code"] == 0),
                },
            )

        except Exception as e:
            logger.error("Task execution failed", task_id=task_id, error=str(e), exc_info=True)
            return EvaluationResult(
                task_id=task_id,
                passed=False,
                score=0.0,
                test_output=f"Execution error: {e}",
                details={"error": str(e)},
            )

        finally:
            # Clean up container
            if container_id:
                try:
                    self.docker_client.remove_container(container_id)
                    logger.debug("Container cleaned up", container_id=container_id)
                except Exception as e:
                    logger.error("Failed to clean up container", error=str(e))

    def _format_test_output(self, test_results: list[dict]) -> str:
        """
        Format test results for display.

        Args:
            test_results: List of test result dicts

        Returns:
            Formatted test output string
        """
        lines = []

        for result in test_results:
            status = "✓ PASS" if result["exit_code"] == 0 else "✗ FAIL"
            lines.append(f"{status}: {result['test']}")

            if result["stdout"]:
                lines.append(f"  stdout: {result['stdout'][:200]}")

            if result["stderr"] and result["exit_code"] != 0:
                lines.append(f"  stderr: {result['stderr'][:200]}")

        return "\n".join(lines)
