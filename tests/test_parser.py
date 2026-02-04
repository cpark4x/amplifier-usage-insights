"""Tests for session parser."""

import json
from pathlib import Path

import pytest

from amplifier_usage_insights.parser import SessionParser


@pytest.fixture
def sample_session_dir(tmp_path: Path) -> Path:
    """Create a sample session directory with test data."""
    session_dir = tmp_path / "test_session"
    session_dir.mkdir()

    # Create events.jsonl (using real Amplifier event format)
    events = [
        {
            "event": "tool:pre",
            "session_id": "test-session-123",
            "timestamp": "2024-01-01T10:00:00Z",
            "data": {"tool_name": "bash"},
        },
        {
            "event": "tool:pre",
            "session_id": "test-session-123",
            "timestamp": "2024-01-01T10:00:05Z",
            "data": {"tool_name": "bash"},
        },
        {
            "event": "tool:pre",
            "session_id": "test-session-123",
            "timestamp": "2024-01-01T10:00:10Z",
            "data": {"tool_name": "read_file"},
        },
        {
            "event": "tool:pre",
            "session_id": "test-session-123",
            "timestamp": "2024-01-01T10:00:15Z",
            "data": {
                "tool_name": "task",
                "tool_input": {
                    "agent": "foundation:web-research",
                    "instruction": "Search for documentation"
                }
            },
        },
        {
            "type": "error",
            "session_id": "test-session-123",
            "timestamp": "2024-01-01T10:00:20Z",
        },
    ]
    
    with open(session_dir / "events.jsonl", "w") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")

    # Create transcript.jsonl
    transcript = [
        {
            "role": "user",
            "content": "First message",
            "timestamp": "2024-01-01T10:00:00Z",
        },
        {
            "role": "assistant",
            "content": "Response",
            "timestamp": "2024-01-01T10:00:10Z",
        },
        {
            "role": "user",
            "content": "Second message",
            "timestamp": "2024-01-01T10:05:00Z",
        },
        {
            "role": "assistant",
            "content": "Final response",
            "timestamp": "2024-01-01T10:10:00Z",
        },
    ]
    
    with open(session_dir / "transcript.jsonl", "w") as f:
        for message in transcript:
            f.write(json.dumps(message) + "\n")

    # Create metadata.json
    metadata = {
        "project_path": "/test/project",
        "model_used": "claude-3-5-sonnet-20241022",
        "status": "completed",
    }
    
    with open(session_dir / "metadata.json", "w") as f:
        json.dump(metadata, f)

    return session_dir


def test_parse_session(sample_session_dir: Path) -> None:
    """Test parsing a complete session."""
    parser = SessionParser()
    session = parser.parse_session(sample_session_dir)

    assert session.session_id == "test-session-123"
    assert session.project_path == "/test/project"
    assert session.turn_count == 2  # 2 user messages
    assert session.tool_call_count == 4  # bash, bash, read_file, task
    assert session.delegation_count == 1  # task with agent field
    assert session.error_count == 1
    assert session.tool_counts == {"bash": 2, "read_file": 1, "task": 1}
    assert session.model_used == "claude-3-5-sonnet-20241022"
    assert session.status == "completed"
    assert session.duration_seconds == 600  # 10 minutes


def test_parse_events_only(tmp_path: Path) -> None:
    """Test parsing when only events.jsonl exists."""
    session_dir = tmp_path / "events_only"
    session_dir.mkdir()

    events = [
        {
            "event": "tool:pre",
            "session_id": "events-only-session",
            "timestamp": "2024-01-01T10:00:00Z",
            "data": {"tool_name": "grep"},
        },
    ]
    
    with open(session_dir / "events.jsonl", "w") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")

    # Create minimal transcript.jsonl
    with open(session_dir / "transcript.jsonl", "w") as f:
        f.write(json.dumps({
            "role": "user",
            "content": "test",
            "timestamp": "2024-01-01T10:00:00Z",
        }) + "\n")

    # Create minimal metadata.json
    with open(session_dir / "metadata.json", "w") as f:
        json.dump({}, f)

    parser = SessionParser()
    session = parser.parse_session(session_dir)

    assert session.session_id == "events-only-session"
    assert session.tool_counts == {"grep": 1}


def test_parse_empty_session(tmp_path: Path) -> None:
    """Test parsing an empty session directory."""
    session_dir = tmp_path / "empty_session"
    session_dir.mkdir()

    # Create empty files
    (session_dir / "events.jsonl").touch()
    (session_dir / "transcript.jsonl").touch()
    (session_dir / "metadata.json").write_text("{}")

    parser = SessionParser()
    session = parser.parse_session(session_dir)

    assert session.tool_call_count == 0
    assert session.turn_count == 0
    assert session.error_count == 0
    assert session.tool_counts == {}


def test_find_sessions(tmp_path: Path) -> None:
    """Test finding sessions in project directory."""
    projects_dir = tmp_path / "projects"
    
    # Create project structure
    project_a = projects_dir / "project-a" / "sessions"
    project_b = projects_dir / "project-b" / "sessions"
    
    project_a.mkdir(parents=True)
    project_b.mkdir(parents=True)
    
    # Create session directories
    (project_a / "session-1").mkdir()
    (project_a / "session-2").mkdir()
    (project_b / "session-3").mkdir()
    
    parser = SessionParser()
    sessions = parser.find_sessions(projects_dir)
    
    assert len(sessions) == 3
    session_names = {s.name for s in sessions}
    assert session_names == {"session-1", "session-2", "session-3"}


def test_find_sessions_no_projects_dir(tmp_path: Path) -> None:
    """Test finding sessions when projects directory doesn't exist."""
    parser = SessionParser()
    sessions = parser.find_sessions(tmp_path / "nonexistent")
    
    assert sessions == []
