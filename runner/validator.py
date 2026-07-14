"""
Task validation system.

Implements Oracle (reference solution must pass) and NOP (empty output must fail) validation.
Uses Docker executor for consistent execution environment when available.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional

from runner.logging import get_logger
from runner.loader import TaskLoader

logger = get_logger(__name__)


class TaskValidator:
    """Validates task correctness using Oracle and NOP patterns."""

    def __init__(self, tasks_dir: Path, use_docker: bool = False):
        """
        Initialize the validator.

        Args:
            tasks_dir: Root directory containing all tasks
            use_docker: Whether to use Docker executor for validation (requires Docker running)
        """
        self.loader = TaskLoader(tasks_dir)
        self.tasks_dir = Path(tasks_dir)
        self.use_docker = use_docker

        # Lazy import Docker executor to avoid requiring Docker
        self._executor = None

        if use_docker:
            try:
                from runner.executor import TaskExecutor

                self._executor = TaskExecutor()
                logger.info("Initialized TaskExecutor for Docker-based validation")
            except Exception as e:
                logger.warning(
                    "Could not initialize Docker executor, " "falling back to subprocess",
                    error=str(e),
                )
                self.use_docker = False

    def validate_oracle(self, task_id: str, timeout: int = 60) -> tuple[bool, str]:
        """
        Oracle validation: run reference solution, must PASS.

        The reference solution should be a script in solution/ that produces correct output.
        It will be executed with the environment/ directory as the working directory.

        Args:
            task_id: The task identifier
            timeout: Execution timeout in seconds

        Returns:
            (success: bool, message: str) - True if oracle passes, False otherwise
        """
        logger.info("Running Oracle validation", task_id=task_id)

        task_dir = self.loader.get_task_path(task_id)
        solution_dir = task_dir / "solution"
        environment_dir = task_dir / "environment"
        tests_dir = task_dir / "tests"

        # Check prerequisites
        if not solution_dir.exists():
            msg = f"Solution directory not found for {task_id}"
            logger.error(msg)
            return False, msg

        if not environment_dir.exists():
            msg = f"Environment directory not found for {task_id}"
            logger.error(msg)
            return False, msg

        if not tests_dir.exists():
            msg = f"Tests directory not found for {task_id}"
            logger.error(msg)
            return False, msg

        # Find and execute the solution script
        solution_scripts = [
            f for f in solution_dir.iterdir() if f.is_file() and f.suffix in [".py", ".sh"]
        ]

        if not solution_scripts:
            msg = f"No solution script found in {solution_dir}"
            logger.error(msg)
            return False, msg

        solution_script = solution_scripts[0]
        logger.debug("Found solution script", path=str(solution_script))

        return self._validate_oracle_subprocess(task_id, solution_script, timeout)

    def _validate_oracle_subprocess(
        self, task_id: str, solution_script: Path, timeout: int
    ) -> tuple[bool, str]:
        """
        Oracle validation using subprocess.

        Args:
            task_id: The task identifier
            solution_script: Path to solution script
            timeout: Execution timeout in seconds

        Returns:
            (success: bool, message: str)
        """
        task_dir = self.loader.get_task_path(task_id)
        environment_dir = task_dir / "environment"

        import shutil

        work_dir = environment_dir
        solution_copy = work_dir / solution_script.name

        try:
            # Copy solution script to work directory
            shutil.copy(solution_script, solution_copy)

            # Execute solution script
            try:
                if solution_script.suffix == ".py":
                    result = subprocess.run(
                        [sys.executable, solution_script.name],
                        cwd=work_dir,
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                    )
                else:  # .sh or other
                    result = subprocess.run(
                        ["bash", solution_script.name],
                        cwd=work_dir,
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                    )

                if result.returncode != 0:
                    msg = f"Solution script failed with exit code {result.returncode}"
                    logger.error(msg, stdout=result.stdout, stderr=result.stderr)
                    return False, msg

                # Now run the tests
                logger.debug("Solution executed successfully, running tests")
                test_result = self._run_tests(task_id, work_dir, timeout)

                if test_result[0]:
                    logger.info("Oracle validation PASSED", task_id=task_id)
                    return True, "Oracle validation passed"
                else:
                    logger.error("Oracle validation FAILED", task_id=task_id, reason=test_result[1])
                    return False, test_result[1]

            except subprocess.TimeoutExpired:
                msg = f"Solution execution timed out after {timeout}s"
                logger.error(msg)
                return False, msg

            except FileNotFoundError as e:
                msg = f"Failed to execute solution: {e}"
                logger.error(msg)
                return False, msg

        finally:
            # Clean up solution copy
            if solution_copy.exists():
                solution_copy.unlink()

    def validate_nop(self, task_id: str, timeout: int = 60) -> tuple[bool, str]:
        """
        NOP validation: run tests on empty workspace, must FAIL.

        This ensures the tests are not trivial (they actually fail when no work is done).

        Args:
            task_id: The task identifier
            timeout: Execution timeout in seconds

        Returns:
            (success: bool, message: str) - True if tests fail (as expected), False if tests pass
        """
        logger.info("Running NOP validation", task_id=task_id)

        task_dir = self.loader.get_task_path(task_id)
        environment_dir = task_dir / "environment"
        tests_dir = task_dir / "tests"

        if not environment_dir.exists():
            msg = f"Environment directory not found for {task_id}"
            logger.error(msg)
            return False, msg

        if not tests_dir.exists():
            msg = f"Tests directory not found for {task_id}"
            logger.error(msg)
            return False, msg

        # Run tests on empty environment (NOP)
        test_result = self._run_tests(task_id, environment_dir, timeout)

        if not test_result[0]:
            # Tests failed as expected (NOP validation success)
            logger.info("NOP validation PASSED (tests correctly failed on empty workspace)")
            return True, "NOP validation passed - tests correctly failed"
        else:
            # Tests passed when they shouldn't have (NOP validation failure)
            msg = "NOP validation FAILED - tests passed on empty workspace (tests are trivial)"
            logger.error(msg)
            return False, msg

    def _run_tests(self, task_id: str, work_dir: Path, timeout: int = 60) -> tuple[bool, str]:
        """
        Execute test scripts in the tests/ directory.

        Tests are Python files that return exit code 0 (pass) or 1 (fail).

        Args:
            task_id: The task identifier
            work_dir: Working directory for test execution
            timeout: Execution timeout in seconds

        Returns:
            (success: bool, message: str) - True if all tests pass
        """
        task_dir = self.loader.get_task_path(task_id)
        tests_dir = task_dir / "tests"

        test_files = sorted([f for f in tests_dir.iterdir() if f.suffix == ".py"])

        if not test_files:
            msg = "No test files found"
            logger.warning(msg, task_id=task_id)
            return True, msg  # Pass by default if no tests

        for test_file in test_files:
            logger.debug("Running test", test_file=test_file.name)

            try:
                result = subprocess.run(
                    [sys.executable, str(test_file)],
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )

                if result.returncode != 0:
                    msg = (
                        f"Test {test_file.name} failed\n"
                        f"stdout: {result.stdout}\n"
                        f"stderr: {result.stderr}"
                    )
                    logger.debug(msg)
                    return False, msg

                logger.debug("Test passed", test_file=test_file.name)

            except subprocess.TimeoutExpired:
                msg = f"Test {test_file.name} timed out after {timeout}s"
                logger.error(msg)
                return False, msg

            except Exception as e:
                msg = f"Test {test_file.name} execution error: {e}"
                logger.error(msg)
                return False, msg

        return True, "All tests passed"

    def validate_all(self, task_ids: Optional[list[str]] = None) -> dict[str, dict]:
        """
        Validate all tasks (or specified tasks) using both Oracle and NOP.

        Args:
            task_ids: List of task IDs to validate. If None, validates all.

        Returns:
            Dictionary mapping task_id -> {oracle: (bool, str), nop: (bool, str)}
        """
        if task_ids is None:
            task_ids = self.loader.discover_tasks()

        results = {}

        for task_id in task_ids:
            logger.info("Validating task", task_id=task_id)

            oracle_result = self.validate_oracle(task_id)
            nop_result = self.validate_nop(task_id)

            results[task_id] = {
                "oracle": oracle_result,
                "nop": nop_result,
                "valid": oracle_result[0] and nop_result[0],
            }

            status = "OK" if results[task_id]["valid"] else "FAIL"
            logger.info(f"Task validation complete: {status}", task_id=task_id)

        return results
