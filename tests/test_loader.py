"""
Tests for task loader.
"""

from pathlib import Path

import pytest

from runner.loader import TaskLoader
from runner.models import TaskConfig


class TestTaskLoader:
    """Test TaskLoader functionality."""
    
    def test_init_with_valid_directory(self, tasks_dir: Path):
        """Test initializing loader with valid directory."""
        loader = TaskLoader(tasks_dir)
        assert loader.tasks_dir == tasks_dir
    
    def test_init_with_invalid_directory(self):
        """Test initializing loader with non-existent directory."""
        with pytest.raises(ValueError):
            TaskLoader(Path("/nonexistent/path"))
    
    def test_discover_tasks(self, tasks_dir: Path):
        """Test discovering tasks in directory."""
        loader = TaskLoader(tasks_dir)
        task_ids = loader.discover_tasks()
        
        # Should find at least the find-database-files task
        assert "find-database-files" in task_ids
        assert isinstance(task_ids, list)
        assert all(isinstance(tid, str) for tid in task_ids)
    
    def test_load_task_config(self, tasks_dir: Path):
        """Test loading a task configuration."""
        loader = TaskLoader(tasks_dir)
        config = loader.load_task("find-database-files")
        
        assert isinstance(config, TaskConfig)
        assert config.id == "find-database-files"
        assert config.name == "Find Database Files"
        assert config.timeout == 60
    
    def test_load_nonexistent_task_raises_error(self, tasks_dir: Path):
        """Test loading non-existent task raises error."""
        loader = TaskLoader(tasks_dir)
        
        with pytest.raises(ValueError):
            loader.load_task("nonexistent-task")
    
    def test_get_task_path(self, tasks_dir: Path):
        """Test getting task directory path."""
        loader = TaskLoader(tasks_dir)
        path = loader.get_task_path("find-database-files")
        
        assert path.is_dir()
        assert path.name == "find-database-files"
    
    def test_validate_task_structure(self, tasks_dir: Path):
        """Test validating task structure."""
        loader = TaskLoader(tasks_dir)
        metadata = loader.validate_task_structure("find-database-files")
        
        assert metadata.has_instruction
        assert metadata.has_solution
        assert metadata.has_tests
        assert metadata.has_environment
        # Note: existing task might not have all components
        # This is a real task from the project
    
    def test_validate_incomplete_task(self, tmp_path: Path):
        """Test validating task with missing components."""
        # Create incomplete task
        task_dir = tmp_path / "incomplete_task"
        task_dir.mkdir()
        
        (task_dir / "task.toml").write_text('name = "test"\ncategory = "filesystem"\n')
        # Missing: instruction.md, solution/, tests/
        
        loader = TaskLoader(tmp_path)
        metadata = loader.validate_task_structure("incomplete_task")
        
        assert not metadata.is_valid
        assert len(metadata.validation_errors) > 0
        assert metadata.has_instruction is False
