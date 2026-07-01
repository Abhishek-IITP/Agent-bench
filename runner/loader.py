"""
Task loader and discovery.

Handles finding, parsing, and loading benchmark tasks from the filesystem.
"""

from pathlib import Path
from typing import Optional

import tomllib

from runner.logging import get_logger
from runner.models import TaskConfig, TaskMetadata


logger = get_logger(__name__)


class TaskLoader:
    """Loads and manages benchmark tasks."""
    
    def __init__(self, tasks_dir: Path):
        """
        Initialize the task loader.
        
        Args:
            tasks_dir: Root directory containing all tasks
        """
        self.tasks_dir = Path(tasks_dir)
        if not self.tasks_dir.exists():
            raise ValueError(f"Tasks directory not found: {self.tasks_dir}")
        
        logger.info("TaskLoader initialized", tasks_dir=str(self.tasks_dir))
    
    def discover_tasks(self) -> list[str]:
        """
        Discover all task IDs by scanning the tasks directory.
        
        A valid task is a directory with task.toml.
        
        Returns:
            List of task IDs found
        """
        task_ids = []
        
        for task_dir in self.tasks_dir.iterdir():
            if not task_dir.is_dir():
                continue
            
            task_toml = task_dir / "task.toml"
            if task_toml.exists():
                # Use directory name as task ID if not in TOML
                task_id = task_dir.name
                task_ids.append(task_id)
                logger.debug("Task discovered", task_id=task_id, path=str(task_dir))
        
        logger.info("Tasks discovered", count=len(task_ids), task_ids=task_ids)
        return sorted(task_ids)
    
    def load_task(self, task_id: str) -> TaskConfig:
        """
        Load a task's configuration.
        
        Args:
            task_id: The task identifier
            
        Returns:
            Parsed TaskConfig
            
        Raises:
            ValueError: If task not found or invalid
        """
        task_dir = self.tasks_dir / task_id
        task_toml = task_dir / "task.toml"
        
        if not task_toml.exists():
            raise ValueError(f"Task not found: {task_id}")
        
        try:
            with open(task_toml, "rb") as f:
                data = tomllib.load(f)
            
            # Ensure id matches directory name
            data["id"] = task_id
            
            config = TaskConfig(**data)
            logger.info("Task loaded", task_id=task_id, name=config.name)
            return config
        
        except Exception as e:
            logger.error("Failed to load task", task_id=task_id, error=str(e))
            raise ValueError(f"Failed to load task {task_id}: {e}") from e
    
    def get_task_path(self, task_id: str) -> Path:
        """Get the filesystem path for a task."""
        return self.tasks_dir / task_id
    
    def validate_task_structure(self, task_id: str) -> TaskMetadata:
        """
        Validate that a task has all required components.
        
        A valid task must have:
        - task.toml (configuration)
        - instruction.md (visible instructions)
        - environment/ (directory)
        - solution/ (directory with reference solution)
        - tests/ (directory with evaluation tests)
        
        Args:
            task_id: The task identifier
            
        Returns:
            TaskMetadata with validation results
        """
        task_dir = self.tasks_dir / task_id
        errors = []
        
        # Load config
        try:
            config = self.load_task(task_id)
        except Exception as e:
            errors.append(f"Invalid task.toml: {e}")
            config = None
        
        # Check for required files/dirs
        has_instruction = (task_dir / "instruction.md").exists()
        has_solution = (task_dir / "solution").is_dir()
        has_tests = (task_dir / "tests").is_dir()
        has_environment = (task_dir / "environment").is_dir()
        
        if not has_instruction:
            errors.append("Missing instruction.md")
        if not has_solution:
            errors.append("Missing solution/ directory")
        if not has_tests:
            errors.append("Missing tests/ directory")
        if not has_environment:
            errors.append("Missing environment/ directory")
        
        is_valid = len(errors) == 0 and config is not None
        
        if is_valid:
            logger.info("Task validated successfully", task_id=task_id)
        else:
            logger.warning("Task validation failed", task_id=task_id, errors=errors)
        
        return TaskMetadata(
            path=task_dir,
            config=config or TaskConfig(id=task_id, name=task_id, category="filesystem"),
            has_instruction=has_instruction,
            has_solution=has_solution,
            has_tests=has_tests,
            has_environment=has_environment,
            is_valid=is_valid,
            validation_errors=errors,
        )
