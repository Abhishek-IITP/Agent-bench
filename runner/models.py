"""
Core data models for AgentBench.

Defines the schema for tasks, execution results, and evaluation metrics.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator
# pydantic is like zod for ts

class DifficultyLevel(str, Enum):
    """Task difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class TaskCategory(str, Enum):
    """Task categories for organization."""
    FILESYSTEM = "filesystem"
    DATA_PROCESSING = "data-processing"
    DEBUGGING = "debugging"
    SECURITY = "security"
    DEVOPS = "devops"
    CODE_GENERATION = "code-generation"
    SYSTEM_ADMIN = "system-admin"


class TaskHealthStatus(str, Enum):
    """Health status of a task in the benchmark."""
    HEALTHY = "healthy"
    FLAKY = "flaky"
    BROKEN = "broken"
    TRIVIAL = "trivial"
    SATURATED = "saturated"


class TaskConfig(BaseModel):
    """Configuration for a benchmark task."""
    
    id: str = Field(..., description="Unique task identifier")
    name: str = Field(..., description="Human-readable task name")
    category: TaskCategory = Field(..., description="Task category")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.EASY, description="Task difficulty")
    version: str = Field(default="1.0.0", description="Task version")
    timeout: int = Field(default=300, description="Execution timeout in seconds")
    description: Optional[str] = Field(default=None, description="Task description")
    docker_image: str = Field(default="ubuntu:22.04", description="Base Docker image")
    expected_output_files: list[str] = Field(
        default_factory=list,
        description="Expected output files from task"
    )
    
    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate task ID format."""
        if not v or not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Task ID must be alphanumeric with hyphens/underscores")
        return v.lower()
    
    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        """Validate timeout is positive.""" 
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v


class ExecutionResult(BaseModel):
    """Result of a single task execution."""
    
    task_id: str
    success: bool
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    duration: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    output_files: dict[str, str] = Field(default_factory=dict)  # path -> content
    error_message: Optional[str] = None


class EvaluationResult(BaseModel):
    """Result of evaluating a task execution."""
    
    task_id: str
    passed: bool
    score: float = 0.0  # 0.0 to 1.0
    test_output: str = ""
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration: float = 0.0


class MultiRunResult(BaseModel):
    """Aggregated results from multiple runs of the same task."""
    
    task_id: str
    agent_name: str
    num_runs: int
    passes: int
    failures: int
    success_rate: float
    mean_duration: float
    std_duration: float
    min_duration: float
    max_duration: float
    results: list[EvaluationResult] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def reliability_score(self) -> float:
        """
        Simple reliability score.
        
        Combines success rate with consistency.
        High variance even with good success rate lowers score.
        """
        if self.num_runs == 0:
            return 0.0
        
        # Base: success rate
        base_score = self.success_rate
        
        # Penalty for high variance: if std is high, consistency is low
        # Normalize std by mean to get coefficient of variation
        if self.mean_duration > 0:
            cv = self.std_duration / self.mean_duration
            # Penalize if CV > 0.5 (more than 50% variation)
            consistency_penalty = max(0, (cv - 0.5) * 0.2) if cv > 0.5 else 0
            return max(0, base_score - consistency_penalty)
        
        return base_score


class TaskMetadata(BaseModel):
    """Metadata about a task directory."""
    
    path: Path
    config: TaskConfig
    has_instruction: bool = False
    has_solution: bool = False
    has_tests: bool = False
    has_environment: bool = False
    is_valid: bool = False
    validation_errors: list[str] = Field(default_factory=list)
