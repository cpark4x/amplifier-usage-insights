"""Tests for SQLite storage."""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from amplifier_usage_insights.parser import Session
from amplifier_usage_insights.storage import MetricsDB


@pytest.fixture
def db(tmp_path: Path) -> MetricsDB:
    """Create a temporary test database."""
    db_path = tmp_path / "test_metrics.db"
    return MetricsDB(db_path)


@pytest.fixture
def sample_session() -> Session:
    """Create a sample session for testing."""
    return Session(
        session_id="test-session-1",
        project_path="/test/project",
        started_at=datetime(2024, 1, 1, 10, 0, 0),
        ended_at=datetime(2024, 1, 1, 10, 30, 0),
        duration_seconds=1800,
        turn_count=5,
        tool_call_count=10,
        delegation_count=2,
        error_count=1,
        tool_counts={"bash": 5, "read_file": 3, "delegate": 2},
        model_used="claude-3-5-sonnet-20241022",
        status="completed",
    )


def test_save_and_get_session(db: MetricsDB, sample_session: Session) -> None:
    """Test saving and retrieving a session."""
    db.save_session(sample_session)
    
    retrieved = db.get_session(sample_session.session_id)
    
    assert retrieved is not None
    assert retrieved.session_id == sample_session.session_id
    assert retrieved.project_path == sample_session.project_path
    assert retrieved.turn_count == sample_session.turn_count
    assert retrieved.tool_call_count == sample_session.tool_call_count
    assert retrieved.delegation_count == sample_session.delegation_count
    assert retrieved.error_count == sample_session.error_count
    assert retrieved.tool_counts == sample_session.tool_counts
    assert retrieved.model_used == sample_session.model_used
    assert retrieved.status == sample_session.status


def test_get_nonexistent_session(db: MetricsDB) -> None:
    """Test retrieving a session that doesn't exist."""
    retrieved = db.get_session("nonexistent-session")
    assert retrieved is None


def test_save_session_updates_existing(db: MetricsDB, sample_session: Session) -> None:
    """Test that saving a session with same ID updates it."""
    db.save_session(sample_session)
    
    # Modify and save again
    sample_session.turn_count = 10
    sample_session.error_count = 3
    db.save_session(sample_session)
    
    retrieved = db.get_session(sample_session.session_id)
    assert retrieved is not None
    assert retrieved.turn_count == 10
    assert retrieved.error_count == 3


def test_get_all_sessions(db: MetricsDB) -> None:
    """Test retrieving all sessions."""
    # Create multiple sessions
    sessions = [
        Session(
            session_id=f"session-{i}",
            project_path="/test/project",
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            ended_at=datetime(2024, 1, 1, 10, 30, 0),
            duration_seconds=1800,
            turn_count=5,
            tool_call_count=10,
            delegation_count=2,
            error_count=1,
            tool_counts={"bash": 5},
            model_used="claude-3-5-sonnet-20241022",
            status="completed",
        )
        for i in range(3)
    ]
    
    for session in sessions:
        db.save_session(session)
    
    all_sessions = db.get_all_sessions()
    assert len(all_sessions) == 3
    assert {s.session_id for s in all_sessions} == {"session-0", "session-1", "session-2"}


def test_get_sessions_in_range(db: MetricsDB) -> None:
    """Test retrieving sessions within a date range."""
    base_date = datetime(2024, 1, 1, 10, 0, 0)
    
    # Create sessions across different days
    sessions = [
        Session(
            session_id=f"session-day-{i}",
            project_path="/test/project",
            started_at=base_date + timedelta(days=i),
            ended_at=base_date + timedelta(days=i, hours=1),
            duration_seconds=3600,
            turn_count=5,
            tool_call_count=10,
            delegation_count=2,
            error_count=1,
            tool_counts={"bash": 5},
            model_used="claude-3-5-sonnet-20241022",
            status="completed",
        )
        for i in range(5)
    ]
    
    for session in sessions:
        db.save_session(session)
    
    # Get sessions from day 1 to day 3 (exclusive)
    start = base_date + timedelta(days=1)
    end = base_date + timedelta(days=3)
    
    filtered = db.get_sessions_in_range(start, end)
    assert len(filtered) == 2
    assert {s.session_id for s in filtered} == {"session-day-1", "session-day-2"}


def test_session_exists(db: MetricsDB, sample_session: Session) -> None:
    """Test checking if a session exists."""
    assert not db.session_exists(sample_session.session_id)
    
    db.save_session(sample_session)
    
    assert db.session_exists(sample_session.session_id)


def test_get_session_count(db: MetricsDB, sample_session: Session) -> None:
    """Test getting total session count."""
    assert db.get_session_count() == 0
    
    db.save_session(sample_session)
    assert db.get_session_count() == 1
    
    # Add another session
    sample_session.session_id = "test-session-2"
    db.save_session(sample_session)
    assert db.get_session_count() == 2


def test_get_tool_usage_summary(db: MetricsDB) -> None:
    """Test aggregating tool usage across sessions."""
    sessions = [
        Session(
            session_id="session-1",
            project_path="/test/project",
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            ended_at=datetime(2024, 1, 1, 10, 30, 0),
            duration_seconds=1800,
            turn_count=5,
            tool_call_count=10,
            delegation_count=2,
            error_count=1,
            tool_counts={"bash": 5, "read_file": 3},
            model_used="claude-3-5-sonnet-20241022",
            status="completed",
        ),
        Session(
            session_id="session-2",
            project_path="/test/project",
            started_at=datetime(2024, 1, 1, 11, 0, 0),
            ended_at=datetime(2024, 1, 1, 11, 30, 0),
            duration_seconds=1800,
            turn_count=5,
            tool_call_count=10,
            delegation_count=2,
            error_count=1,
            tool_counts={"bash": 3, "grep": 2, "delegate": 2},
            model_used="claude-3-5-sonnet-20241022",
            status="completed",
        ),
    ]
    
    for session in sessions:
        db.save_session(session)
    
    summary = db.get_tool_usage_summary()
    
    assert summary["bash"] == 8  # 5 + 3
    assert summary["read_file"] == 3
    assert summary["grep"] == 2
    assert summary["delegate"] == 2
