"""
Tests for the task validator module.

Note: Full validator tests require bash and shell scripts.
These basic tests verify the validator module structure.
"""

import pytest

from runner.validator import TaskValidator


class TestTaskValidator:
    """Test suite for TaskValidator."""

    @pytest.fixture
    def validator(self, tasks_dir):
        """Create a validator instance."""
        return TaskValidator(tasks_dir)

    def test_init_with_valid_directory(self, tasks_dir):
        """Test initializing validator with valid tasks directory."""
        validator = TaskValidator(tasks_dir)
        assert validator.tasks_dir == tasks_dir
        assert validator.loader is not None

    def test_init_with_invalid_directory(self, tmp_path):
        """Test initializing validator with non-existent directory."""
        with pytest.raises(ValueError):
            TaskValidator(tmp_path / "nonexistent")

    def test_validator_has_methods(self, validator):
        """Test that validator has expected methods."""
        assert hasattr(validator, "validate_oracle")
        assert hasattr(validator, "validate_nop")
        assert hasattr(validator, "validate_all")
        assert hasattr(validator, "_run_tests")
