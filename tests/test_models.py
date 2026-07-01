"""
Tests for data models.
"""

from datetime import datetime

import pytest

from runner.models import (
    DifficultyLevel,
    EvaluationResult,
    ExecutionResult,
    MultiRunResult,
    TaskCategory,
    TaskConfig,
)


class TestTaskConfig:
    """Test TaskConfig model."""
    
    def test_create_valid_task_config(self):
        """Test creating a valid TaskConfig."""
        config = TaskConfig(
            id="test-task",
            name="Test Task",
            category=TaskCategory.FILESYSTEM,
            difficulty=DifficultyLevel.EASY,
        )
        
        assert config.id == "test-task"
        assert config.name == "Test Task"
        assert config.category == TaskCategory.FILESYSTEM
        assert config.difficulty == DifficultyLevel.EASY
        assert config.timeout == 300  # default
    
    def test_task_id_normalized_to_lowercase(self):
        """Test that task IDs are normalized to lowercase."""
        config = TaskConfig(
            id="TEST-TASK",
            name="Test",
            category=TaskCategory.FILESYSTEM,
        )
        
        assert config.id == "test-task"
    
    def test_invalid_task_id_raises_error(self):
        """Test that invalid task IDs raise validation error."""
        with pytest.raises(ValueError):
            TaskConfig(
                id="test@task!",
                name="Test",
                category=TaskCategory.FILESYSTEM,
            )
    
    def test_invalid_timeout_raises_error(self):
        """Test that non-positive timeout raises error."""
        with pytest.raises(ValueError):
            TaskConfig(
                id="test-task",
                name="Test",
                category=TaskCategory.FILESYSTEM,
                timeout=-1,
            )
    
    def test_task_config_with_custom_values(self):
        """Test TaskConfig with custom values."""
        config = TaskConfig(
            id="hard-task",
            name="Hard Task",
            category=TaskCategory.DEBUGGING,
            difficulty=DifficultyLevel.HARD,
            timeout=600,
            description="A difficult debugging task",
            expected_output_files=["output.txt", "log.json"],
        )
        
        assert config.difficulty == DifficultyLevel.HARD
        assert config.timeout == 600
        assert len(config.expected_output_files) == 2


class TestExecutionResult:
    """Test ExecutionResult model."""
    
    def test_create_successful_execution(self):
        """Test creating a successful execution result."""
        result = ExecutionResult(
            task_id="test-task",
            success=True,
            exit_code=0,
            stdout="Success",
            duration=1.23,
        )
        
        assert result.task_id == "test-task"
        assert result.success is True
        assert result.exit_code == 0
        assert result.duration == 1.23
    
    def test_create_failed_execution(self):
        """Test creating a failed execution result."""
        result = ExecutionResult(
            task_id="test-task",
            success=False,
            exit_code=1,
            stderr="Error occurred",
            error_message="Task timed out",
        )
        
        assert result.success is False
        assert result.exit_code == 1
        assert result.error_message == "Task timed out"


class TestEvaluationResult:
    """Test EvaluationResult model."""
    
    def test_create_passed_evaluation(self):
        """Test creating a passed evaluation."""
        result = EvaluationResult(
            task_id="test-task",
            passed=True,
            score=1.0,
            test_output="All tests passed",
        )
        
        assert result.task_id == "test-task"
        assert result.passed is True
        assert result.score == 1.0


class TestMultiRunResult:
    """Test MultiRunResult model and reliability score."""
    
    def test_create_multi_run_result(self):
        """Test creating a multi-run result."""
        result = MultiRunResult(
            task_id="test-task",
            agent_name="test-agent",
            num_runs=10,
            passes=8,
            failures=2,
            success_rate=0.8,
            mean_duration=5.0,
            std_duration=0.5,
            min_duration=4.2,
            max_duration=5.8,
        )
        
        assert result.task_id == "test-task"
        assert result.success_rate == 0.8
        assert result.passes == 8
    
    def test_reliability_score_all_passes(self):
        """Test reliability score for all passing runs."""
        result = MultiRunResult(
            task_id="test-task",
            agent_name="test-agent",
            num_runs=10,
            passes=10,
            failures=0,
            success_rate=1.0,
            mean_duration=5.0,
            std_duration=0.1,
            min_duration=4.9,
            max_duration=5.1,
        )
        
        score = result.reliability_score
        assert score == pytest.approx(1.0, abs=0.01)
    
    def test_reliability_score_high_variance_penalty(self):
        """Test that high variance reduces reliability score."""
        result = MultiRunResult(
            task_id="test-task",
            agent_name="test-agent",
            num_runs=10,
            passes=9,
            failures=1,
            success_rate=0.9,
            mean_duration=10.0,
            std_duration=6.0,  # 60% coefficient of variation
            min_duration=2.0,
            max_duration=18.0,
        )
        
        score = result.reliability_score
        # Should be less than 0.9 due to high variance penalty
        assert score < 0.9
    
    def test_reliability_score_empty_runs(self):
        """Test reliability score with no runs."""
        result = MultiRunResult(
            task_id="test-task",
            agent_name="test-agent",
            num_runs=0,
            passes=0,
            failures=0,
            success_rate=0.0,
            mean_duration=0.0,
            std_duration=0.0,
            min_duration=0.0,
            max_duration=0.0,
        )
        
        assert result.reliability_score == 0.0
