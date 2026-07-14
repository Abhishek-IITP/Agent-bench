"""
Execution replay system for capturing and analyzing agent performance.

Records all events during task execution and supports playback and analysis.
"""

import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from runner.logging import get_logger

logger = get_logger(__name__)


class EventType(str, Enum):
    """Types of events that can be recorded."""

    AGENT_MESSAGE = "agent_message"
    COMMAND_START = "command_start"
    COMMAND_OUTPUT = "command_output"
    COMMAND_ERROR = "command_error"
    FILE_WRITTEN = "file_written"
    FILE_READ = "file_read"
    TEST_RESULT = "test_result"
    ERROR = "error"
    ITERATION_START = "iteration_start"
    ITERATION_END = "iteration_end"


@dataclass
class ReplayEvent:
    """A single event in the execution trace."""

    timestamp: float  # Unix timestamp, seconds since epoch
    type: EventType
    content: str
    duration: Optional[float] = None  # How long this event took
    metadata: dict[str, Any] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["type"] = self.type.value
        if self.metadata is None:
            data["metadata"] = {}
        return data


@dataclass
class ReplayTrace:
    """Complete execution trace for a task."""

    task_id: str
    agent_name: str
    agent_type: str
    model: str

    started_at: datetime
    ended_at: Optional[datetime] = None

    events: list[ReplayEvent] = None

    # Result summary
    success: bool = False
    error_message: Optional[str] = None

    # Metrics
    total_iterations: int = 0
    commands_executed: int = 0
    files_created: int = 0
    tokens_used: int = 0
    cost: float = 0.0

    def __post_init__(self):
        if self.events is None:
            self.events = []

    @property
    def duration(self) -> float:
        """Get total duration in seconds."""
        if self.ended_at is None:
            return 0.0
        return (self.ended_at - self.started_at).total_seconds()

    def to_dict(self) -> dict[str, Any]:
        """Convert trace to dictionary for JSON serialization."""
        return {
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "model": self.model,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration": self.duration,
            "success": self.success,
            "error_message": self.error_message,
            "total_iterations": self.total_iterations,
            "commands_executed": self.commands_executed,
            "files_created": self.files_created,
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "events": [e.to_dict() for e in self.events],
        }

    def to_json(self) -> str:
        """Convert trace to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class ReplayRecorder:
    """Records events during task execution."""

    def __init__(
        self,
        task_id: str,
        agent_name: str,
        agent_type: str,
        model: str,
    ):
        """
        Initialize recorder.

        Args:
            task_id: Task being executed
            agent_name: Name of the agent
            agent_type: Type of agent (openai, ollama, etc.)
            model: Model name
        """
        self.trace = ReplayTrace(
            task_id=task_id,
            agent_name=agent_name,
            agent_type=agent_type,
            model=model,
            started_at=datetime.utcnow(),
        )

        self.logger = logger
        self._last_event_time = time.time()

    def record_event(
        self,
        event_type: EventType,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Record an event.

        Args:
            event_type: Type of event
            content: Event description/output
            metadata: Optional additional data
        """
        current_time = time.time()
        duration = current_time - self._last_event_time
        self._last_event_time = current_time

        event = ReplayEvent(
            timestamp=current_time,
            type=event_type,
            content=content[:10000],  # Limit content size
            duration=duration,
            metadata=metadata or {},
        )

        self.trace.events.append(event)

        # Log significant events
        if event_type in (EventType.ERROR, EventType.COMMAND_ERROR):
            self.logger.warning(f"Replay event: {event_type.value}", content=content[:200])
        else:
            self.logger.debug(f"Replay event: {event_type.value}", content=content[:100])

    def record_agent_message(self, message: str) -> None:
        """Record an agent message."""
        self.record_event(EventType.AGENT_MESSAGE, message)

    def record_command_start(self, command: str) -> None:
        """Record command execution start."""
        self.record_event(EventType.COMMAND_START, command, metadata={"command": command})
        self.trace.commands_executed += 1

    def record_command_output(self, output: str) -> None:
        """Record command output."""
        self.record_event(EventType.COMMAND_OUTPUT, output)

    def record_command_error(self, error: str) -> None:
        """Record command error."""
        self.record_event(EventType.COMMAND_ERROR, error)

    def record_file_written(self, path: str, size: int) -> None:
        """Record file write."""
        self.record_event(
            EventType.FILE_WRITTEN, f"Wrote {size} bytes", metadata={"path": path, "size": size}
        )
        self.trace.files_created += 1

    def record_file_read(self, path: str, size: int) -> None:
        """Record file read."""
        self.record_event(
            EventType.FILE_READ, f"Read {size} bytes", metadata={"path": path, "size": size}
        )

    def record_test_result(self, test_name: str, passed: bool) -> None:
        """Record test result."""
        self.record_event(
            EventType.TEST_RESULT,
            f"Test {'passed' if passed else 'failed'}: {test_name}",
            metadata={"test": test_name, "passed": passed},
        )

    def record_error(self, error: str) -> None:
        """Record an error."""
        self.record_event(EventType.ERROR, error)

    def record_iteration_start(self, iteration: int) -> None:
        """Record iteration start."""
        self.record_event(
            EventType.ITERATION_START, f"Iteration {iteration}", metadata={"iteration": iteration}
        )

    def record_iteration_end(self, iteration: int) -> None:
        """Record iteration end."""
        self.record_event(
            EventType.ITERATION_END,
            f"Iteration {iteration} complete",
            metadata={"iteration": iteration},
        )

    def finalize(
        self,
        success: bool,
        error_message: Optional[str] = None,
        tokens_used: int = 0,
        cost: float = 0.0,
    ) -> ReplayTrace:
        """
        Finalize the trace.

        Args:
            success: Whether execution succeeded
            error_message: Error message if failed
            tokens_used: Total tokens used (for LLM agents)
            cost: Estimated cost

        Returns:
            Complete ReplayTrace
        """
        self.trace.ended_at = datetime.utcnow()
        self.trace.success = success
        self.trace.error_message = error_message
        self.trace.tokens_used = tokens_used
        self.trace.cost = cost
        self.trace.total_iterations = len(
            [e for e in self.trace.events if e.type == EventType.ITERATION_START]
        )

        self.logger.info(
            "Replay trace finalized",
            task=self.trace.task_id,
            success=success,
            duration=self.trace.duration,
            events=len(self.trace.events),
        )

        return self.trace


class ReplayStorage:
    """Stores and retrieves replay traces."""

    def __init__(self, storage_dir: str = "results"):
        """
        Initialize storage.

        Args:
            storage_dir: Directory to store replay files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger

    def save_trace(self, trace: ReplayTrace, run_id: str) -> Path:
        """
        Save a trace to disk.

        Args:
            trace: Trace to save
            run_id: Unique run identifier

        Returns:
            Path to saved file
        """
        run_dir = self.storage_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        file_path = run_dir / "replay.json"

        with open(file_path, "w") as f:
            f.write(trace.to_json())

        self.logger.info("Trace saved", path=str(file_path), run_id=run_id)
        return file_path

    def load_trace(self, run_id: str) -> Optional[ReplayTrace]:
        """
        Load a trace from disk.

        Args:
            run_id: Run identifier

        Returns:
            ReplayTrace or None if not found
        """
        file_path = self.storage_dir / run_id / "replay.json"

        if not file_path.exists():
            self.logger.warning("Trace file not found", run_id=run_id, path=str(file_path))
            return None

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            # Reconstruct trace from data
            trace = ReplayTrace(
                task_id=data["task_id"],
                agent_name=data["agent_name"],
                agent_type=data["agent_type"],
                model=data["model"],
                started_at=datetime.fromisoformat(data["started_at"]),
                ended_at=datetime.fromisoformat(data["ended_at"]) if data.get("ended_at") else None,
                success=data["success"],
                error_message=data.get("error_message"),
                total_iterations=data.get("total_iterations", 0),
                commands_executed=data.get("commands_executed", 0),
                files_created=data.get("files_created", 0),
                tokens_used=data.get("tokens_used", 0),
                cost=data.get("cost", 0.0),
            )

            # Reconstruct events
            for event_data in data.get("events", []):
                event = ReplayEvent(
                    timestamp=event_data["timestamp"],
                    type=EventType(event_data["type"]),
                    content=event_data["content"],
                    duration=event_data.get("duration"),
                    metadata=event_data.get("metadata", {}),
                )
                trace.events.append(event)

            self.logger.info("Trace loaded", run_id=run_id, events=len(trace.events))
            return trace

        except Exception as e:
            self.logger.error("Failed to load trace", run_id=run_id, error=str(e))
            return None

    def list_runs(self, task_id: Optional[str] = None) -> list[str]:
        """
        List all saved runs.

        Args:
            task_id: Filter by task ID (optional)

        Returns:
            List of run IDs
        """
        run_ids = []

        for run_dir in self.storage_dir.iterdir():
            if not run_dir.is_dir():
                continue

            trace_file = run_dir / "replay.json"
            if not trace_file.exists():
                continue

            if task_id:
                try:
                    trace = self.load_trace(run_dir.name)
                    if trace and trace.task_id == task_id:
                        run_ids.append(run_dir.name)
                except Exception:
                    continue
            else:
                run_ids.append(run_dir.name)

        return sorted(run_ids)
