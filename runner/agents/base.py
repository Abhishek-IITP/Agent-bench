"""
Base agent interface for solving benchmark tasks.

Defines the abstract BaseAgent class and data models for agent execution.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class AgentType(str, Enum):
    """Supported agent implementations."""

    OPENAI = "openai"
    OLLAMA = "ollama"
    LOCAL = "local"


@dataclass
class AgentResult:
    """Result of an agent's attempt to solve a task."""

    task_id: str
    agent_name: str
    agent_type: AgentType

    # Execution metrics
    success: bool = False
    commands_executed: int = 0
    files_created: int = 0
    files_modified: int = 0

    # Resource usage
    token_usage: int = 0  # For LLM-based agents
    cost: float = 0.0  # Estimated cost in USD
    duration: float = 0.0  # Execution time in seconds

    # Execution trace
    stdout: str = ""
    stderr: str = ""
    error_message: Optional[str] = None
    execution_trace: list[dict[str, Any]] = field(default_factory=list)

    # Timestamps
    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type.value,
            "success": self.success,
            "commands_executed": self.commands_executed,
            "files_created": self.files_created,
            "files_modified": self.files_modified,
            "token_usage": self.token_usage,
            "cost": self.cost,
            "duration": self.duration,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "error_message": self.error_message,
            "execution_trace": self.execution_trace,
        }


@dataclass
class AgentConfig:
    """Configuration for agent initialization."""

    agent_type: AgentType
    model: str
    name: str = ""

    # API configuration
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None

    # Generation parameters
    temperature: float = 0.7
    max_tokens: int = 4096

    # Execution parameters
    max_iterations: int = 10
    timeout: int = 300  # seconds

    # Docker configuration
    docker_image: str = "ubuntu:22.04"
    docker_memory: str = "512m"

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "agent_type": self.agent_type.value,
            "model": self.model,
            "name": self.name,
            "api_endpoint": self.api_endpoint,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "max_iterations": self.max_iterations,
            "timeout": self.timeout,
            "docker_image": self.docker_image,
            "docker_memory": self.docker_memory,
        }


class BaseAgent(ABC):
    """Abstract base class for agents solving tasks."""

    def __init__(self, config: AgentConfig):
        """
        Initialize the agent.

        Args:
            config: Agent configuration
        """
        self.config = config
        self.logger = None  # Will be set by subclasses

    @abstractmethod
    async def solve(
        self,
        task_id: str,
        instruction: str,
        environment_files: dict[str, str],
        timeout: Optional[int] = None,
    ) -> AgentResult:
        """
        Solve a task.

        Args:
            task_id: Unique task identifier
            instruction: Task instructions
            environment_files: Dictionary of filename -> file content
            timeout: Execution timeout in seconds

        Returns:
            AgentResult with execution details
        """
        pass

    def _add_trace_event(
        self,
        trace: list[dict[str, Any]],
        event_type: str,
        content: str,
        timestamp: Optional[float] = None,
    ) -> None:
        """
        Add an event to the execution trace.

        Args:
            trace: Execution trace list
            event_type: Type of event (e.g., 'command_start', 'agent_message')
            content: Event content
            timestamp: Unix timestamp (auto-generated if None)
        """
        if timestamp is None:
            timestamp = time.time()

        trace.append(
            {
                "timestamp": timestamp,
                "type": event_type,
                "content": content,
            }
        )

    def _create_result(
        self,
        task_id: str,
        success: bool = False,
        error: Optional[str] = None,
    ) -> AgentResult:
        """
        Create an AgentResult with common fields.

        Args:
            task_id: Task identifier
            success: Whether execution succeeded
            error: Error message if execution failed

        Returns:
            AgentResult object
        """
        now = datetime.utcnow()

        result = AgentResult(
            task_id=task_id,
            agent_name=self.config.name or self.config.model,
            agent_type=self.config.agent_type,
            success=success,
            error_message=error,
            ended_at=now,
        )

        # Calculate duration
        result.duration = (now - result.started_at).total_seconds()

        return result
