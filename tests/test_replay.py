"""Tests for replay system."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from runner.replay import (
    EventType,
    ReplayEvent,
    ReplayRecorder,
    ReplayStorage,
    ReplayTrace,
)


class TestReplayEvent:
    """Tests for ReplayEvent."""

    def test_event_creation(self):
        """Test event creation."""
        event = ReplayEvent(
            timestamp=1234567890.0, type=EventType.COMMAND_START, content="find / -name *.db"
        )

        assert event.type == EventType.COMMAND_START
        assert event.content == "find / -name *.db"

    def test_event_to_dict(self):
        """Test event serialization."""
        event = ReplayEvent(
            timestamp=1234567890.0,
            type=EventType.COMMAND_OUTPUT,
            content="output.txt",
            duration=1.5,
            metadata={"lines": 42},
        )

        data = event.to_dict()

        assert data["type"] == "command_output"
        assert data["content"] == "output.txt"
        assert data["duration"] == 1.5
        assert data["metadata"]["lines"] == 42


class TestReplayTrace:
    """Tests for ReplayTrace."""

    def test_trace_creation(self):
        """Test trace creation."""
        now = datetime.utcnow()
        trace = ReplayTrace(
            task_id="find-files",
            agent_name="gpt-4",
            agent_type="openai",
            model="gpt-4",
            started_at=now,
        )

        assert trace.task_id == "find-files"
        assert trace.agent_type == "openai"
        assert len(trace.events) == 0

    def test_trace_duration(self):
        """Test trace duration calculation."""
        now = datetime.utcnow()
        trace = ReplayTrace(
            task_id="test",
            agent_name="agent",
            agent_type="openai",
            model="gpt-4",
            started_at=now,
            ended_at=now + timedelta(seconds=42),
        )

        assert trace.duration == 42.0

    def test_trace_to_dict(self):
        """Test trace serialization."""
        now = datetime.utcnow()
        trace = ReplayTrace(
            task_id="test",
            agent_name="agent",
            agent_type="openai",
            model="gpt-4",
            started_at=now,
            ended_at=now + timedelta(seconds=10),
            success=True,
            commands_executed=5,
        )

        data = trace.to_dict()

        assert data["task_id"] == "test"
        assert data["success"] is True
        assert data["commands_executed"] == 5
        assert "duration" in data


class TestReplayRecorder:
    """Tests for ReplayRecorder."""

    def test_recorder_creation(self):
        """Test recorder creation."""
        recorder = ReplayRecorder(
            task_id="solve-puzzle", agent_name="gpt-4", agent_type="openai", model="gpt-4"
        )

        assert recorder.trace.task_id == "solve-puzzle"
        assert len(recorder.trace.events) == 0

    def test_record_command(self):
        """Test recording command events."""
        recorder = ReplayRecorder(
            task_id="test", agent_name="agent", agent_type="openai", model="gpt-4"
        )

        recorder.record_command_start("ls -la /workspace")
        recorder.record_command_output("total 42\ndrwx...")

        assert len(recorder.trace.events) == 2
        assert recorder.trace.commands_executed == 1
        assert recorder.trace.events[0].type == EventType.COMMAND_START
        assert recorder.trace.events[1].type == EventType.COMMAND_OUTPUT

    def test_record_file_operations(self):
        """Test recording file operations."""
        recorder = ReplayRecorder(
            task_id="test", agent_name="agent", agent_type="openai", model="gpt-4"
        )

        recorder.record_file_written("/workspace/solution.py", 512)
        recorder.record_file_read("/workspace/input.txt", 256)

        assert recorder.trace.files_created == 1
        assert len(recorder.trace.events) == 2

    def test_finalize(self):
        """Test trace finalization."""
        recorder = ReplayRecorder(
            task_id="test", agent_name="agent", agent_type="openai", model="gpt-4"
        )

        recorder.record_command_start("test")
        trace = recorder.finalize(success=True, tokens_used=1500, cost=0.042)

        assert trace.success is True
        assert trace.tokens_used == 1500
        assert trace.cost == 0.042
        assert trace.ended_at is not None


class TestReplayStorage:
    """Tests for ReplayStorage."""

    def test_storage_creation(self):
        """Test storage creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ReplayStorage(tmpdir)
            assert Path(tmpdir).exists()

    def test_save_and_load_trace(self):
        """Test saving and loading traces."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = ReplayStorage(tmpdir)

            now = datetime.utcnow()
            trace = ReplayTrace(
                task_id="find-files",
                agent_name="gpt-4",
                agent_type="openai",
                model="gpt-4",
                started_at=now,
                ended_at=now + timedelta(seconds=30),
                success=True,
                commands_executed=3,
            )

            # Add some events
            trace.events.append(
                ReplayEvent(
                    timestamp=now.timestamp(),
                    type=EventType.COMMAND_START,
                    content="find . -type f",
                )
            )

            run_id = "run-123"
            path = storage.save_trace(trace, run_id)

            assert path.exists()

            # Load it back
            loaded = storage.load_trace(run_id)

            assert loaded is not None
            assert loaded.task_id == trace.task_id
            assert loaded.success is True
            assert len(loaded.events) == 1

    def test_list_runs(self):
        """Test listing runs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = ReplayStorage(tmpdir)

            now = datetime.utcnow()

            # Save multiple traces
            for i in range(3):
                trace = ReplayTrace(
                    task_id=f"task-{i}",
                    agent_name="agent",
                    agent_type="openai",
                    model="gpt-4",
                    started_at=now,
                )
                storage.save_trace(trace, f"run-{i}")

            runs = storage.list_runs()
            assert len(runs) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
