"""
Pytest configuration and fixtures.
"""

from pathlib import Path

import pytest


@pytest.fixture
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def tasks_dir(project_root: Path) -> Path:
    """Get the tasks directory."""
    return project_root / "tasks"


@pytest.fixture
def temp_task_dir(tmp_path: Path) -> Path:
    """Create a temporary task directory for testing."""
    task_dir = tmp_path / "test_task"
    task_dir.mkdir()
    
    # Create minimal task structure
    (task_dir / "task.toml").write_text(
        'name = "test"\ncategory = "filesystem"\ndifficulty = "easy"\n'
    )
    (task_dir / "instruction.md").write_text("# Test Task\n")
    (task_dir / "solution").mkdir()
    (task_dir / "tests").mkdir()
    (task_dir / "environment").mkdir()
    
    return task_dir
