"""Tests for metrics calculation and growth tracking."""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from amplifier_usage_insights.metrics import (
    WeeklyMetrics,
    calculate_growth,
    calculate_weekly_metrics,
    get_week_start,
)
from amplifier_usage_insights.parser import Session
from amplifier_usage_insights.storage import MetricsDB


def test_get_week_start() -> None:
    """Test getting Monday 00:00:00 for any date."""
    # Test Wednesday
    wednesday = datetime(2024, 1, 3, 15, 30, 45)
    week_start = get_week_start(wednesday)

    assert week_start.weekday() == 0  # Monday
    assert week_start.year == 2024
    assert week_start.month == 1
    assert week_start.day == 1  # Monday, Jan 1
    assert week_start.hour == 0
    assert week_start.minute == 0
    assert week_start.second == 0
    assert week_start.microsecond == 0


def test_get_week_start_already_monday() -> None:
    """Test getting week start when date is already Monday."""
    monday = datetime(2024, 1, 1, 12, 0, 0)
    week_start = get_week_start(monday)

    assert week_start.day == 1
    assert week_start.hour == 0
    assert week_start.minute == 0


def test_get_week_start_sunday() -> None:
    """Test getting week start for Sunday (last day of week)."""
    sunday = datetime(2024, 1, 7, 20, 0, 0)
    week_start = get_week_start(sunday)

    assert week_start.weekday() == 0  # Monday
    assert week_start.day == 1  # Previous Monday


def test_calculate_growth_no_previous() -> None:
    """Test growth calculation with no previous week data."""
    current = WeeklyMetrics(
        user_id="local",
        week_start=datetime(2024, 1, 1),
        session_count=10,
        total_duration_seconds=3600,
        total_turns=50,
        total_tool_calls=100,
        total_delegations=20,
        total_errors=5,
        unique_tools=8,
        tool_counts={"bash": 30, "read_file": 20},
        top_5_tools=["bash", "read_file"],
        avg_session_duration=360.0,
        avg_turns_per_session=5.0,
        delegation_ratio=2.0,
        error_rate=0.05,
        sessions_change_pct=None,
        tools_change_pct=None,
        delegation_change_pct=None,
        error_change_pct=None,
    )

    growth = calculate_growth(current, None)

    assert growth["sessions_change_pct"] is None
    assert growth["tools_change_pct"] is None
    assert growth["delegation_change_pct"] is None
    assert growth["error_change_pct"] is None
    assert growth["trend"] == "stable"


def test_calculate_growth_improving() -> None:
    """Test growth calculation showing improvement."""
    previous = WeeklyMetrics(
        user_id="local",
        week_start=datetime(2024, 1, 1),
        session_count=10,
        total_duration_seconds=3600,
        total_turns=50,
        total_tool_calls=100,
        total_delegations=20,
        total_errors=15,
        unique_tools=8,
        tool_counts={"bash": 30},
        top_5_tools=["bash"],
        avg_session_duration=360.0,
        avg_turns_per_session=5.0,
        delegation_ratio=2.0,
        error_rate=0.15,
        sessions_change_pct=None,
        tools_change_pct=None,
        delegation_change_pct=None,
        error_change_pct=None,
    )

    current = WeeklyMetrics(
        user_id="local",
        week_start=datetime(2024, 1, 8),
        session_count=15,  # +50% sessions
        total_duration_seconds=5400,
        total_turns=75,
        total_tool_calls=150,
        total_delegations=40,  # +100% delegations
        total_errors=15,  # Same errors but more tool calls
        unique_tools=12,  # +4 tools
        tool_counts={"bash": 30, "read_file": 20, "grep": 10},
        top_5_tools=["bash", "read_file", "grep"],
        avg_session_duration=360.0,
        avg_turns_per_session=5.0,
        delegation_ratio=2.67,  # Higher
        error_rate=0.10,  # Lower
        sessions_change_pct=None,
        tools_change_pct=None,
        delegation_change_pct=None,
        error_change_pct=None,
    )

    growth = calculate_growth(current, previous)

    assert growth["sessions_change_pct"] == 50.0  # +50%
    assert growth["tools_change_pct"] == 50.0  # 8 -> 12 = +50%
    assert growth["delegation_change_pct"] > 0  # Improved
    assert growth["error_change_pct"] < 0  # Fewer errors per tool call
    assert growth["trend"] == "improving"  # Score should be >= 3


def test_calculate_growth_declining() -> None:
    """Test growth calculation showing decline."""
    previous = WeeklyMetrics(
        user_id="local",
        week_start=datetime(2024, 1, 1),
        session_count=15,
        total_duration_seconds=5400,
        total_turns=75,
        total_tool_calls=150,
        total_delegations=40,
        total_errors=10,
        unique_tools=12,
        tool_counts={"bash": 30, "read_file": 20},
        top_5_tools=["bash", "read_file"],
        avg_session_duration=360.0,
        avg_turns_per_session=5.0,
        delegation_ratio=2.67,
        error_rate=0.067,
        sessions_change_pct=None,
        tools_change_pct=None,
        delegation_change_pct=None,
        error_change_pct=None,
    )

    current = WeeklyMetrics(
        user_id="local",
        week_start=datetime(2024, 1, 8),
        session_count=8,  # Fewer sessions
        total_duration_seconds=2880,
        total_turns=40,
        total_tool_calls=80,
        total_delegations=10,  # Fewer delegations
        total_errors=15,  # More errors
        unique_tools=8,  # Fewer tools
        tool_counts={"bash": 30},
        top_5_tools=["bash"],
        avg_session_duration=360.0,
        avg_turns_per_session=5.0,
        delegation_ratio=1.25,  # Lower
        error_rate=0.1875,  # Higher
        sessions_change_pct=None,
        tools_change_pct=None,
        delegation_change_pct=None,
        error_change_pct=None,
    )

    growth = calculate_growth(current, previous)

    assert growth["sessions_change_pct"] < 0  # Fewer sessions
    assert growth["tools_change_pct"] < 0  # Fewer tools
    assert growth["delegation_change_pct"] < 0  # Less delegation
    assert growth["error_change_pct"] > 0  # More errors
    assert growth["trend"] == "declining"  # Score should be <= 1


def test_calculate_growth_stable() -> None:
    """Test growth calculation showing stable (mixed signals)."""
    previous = WeeklyMetrics(
        user_id="local",
        week_start=datetime(2024, 1, 1),
        session_count=10,
        total_duration_seconds=3600,
        total_turns=50,
        total_tool_calls=100,
        total_delegations=20,
        total_errors=10,
        unique_tools=10,
        tool_counts={"bash": 30},
        top_5_tools=["bash"],
        avg_session_duration=360.0,
        avg_turns_per_session=5.0,
        delegation_ratio=2.0,
        error_rate=0.10,
        sessions_change_pct=None,
        tools_change_pct=None,
        delegation_change_pct=None,
        error_change_pct=None,
    )

    current = WeeklyMetrics(
        user_id="local",
        week_start=datetime(2024, 1, 8),
        session_count=10,  # Same sessions (no score)
        total_duration_seconds=3600,
        total_turns=50,
        total_tool_calls=100,
        total_delegations=22,  # Slight increase (score +1)
        total_errors=9,  # Slight decrease (score +1)
        unique_tools=10,  # Same (no score)
        tool_counts={"bash": 30},
        top_5_tools=["bash"],
        avg_session_duration=360.0,
        avg_turns_per_session=5.0,
        delegation_ratio=2.2,  # Slight increase
        error_rate=0.09,  # Slight decrease
        sessions_change_pct=None,
        tools_change_pct=None,
        delegation_change_pct=None,
        error_change_pct=None,
    )

    growth = calculate_growth(current, previous)

    # Score = 2 (delegation up, errors down, but sessions/tools unchanged) -> stable
    assert growth["trend"] == "stable"  # Mixed signals


@pytest.fixture
def db_with_sessions(tmp_path: Path) -> MetricsDB:
    """Create a database with sample sessions for a week."""
    db_path = tmp_path / "test_metrics.db"
    db = MetricsDB(db_path)

    # Create sessions for current week (Monday 2024-01-01 to Sunday 2024-01-07)
    base_date = datetime(2024, 1, 1, 10, 0, 0)  # Monday

    sessions = [
        Session(
            session_id=f"session-{i}",
            project_path="/test/project",
            started_at=base_date + timedelta(days=i, hours=i),
            ended_at=base_date + timedelta(days=i, hours=i, minutes=30),
            duration_seconds=1800,
            turn_count=5,
            tool_call_count=10,
            delegation_count=2,
            error_count=1,
            tool_counts={"bash": 5, "read_file": 3, "delegate": 2},
            model_used="claude-3-5-sonnet-20241022",
            status="completed",
        )
        for i in range(5)  # 5 sessions across the week
    ]

    for session in sessions:
        db.save_session(session)

    return db


def test_calculate_weekly_metrics(db_with_sessions: MetricsDB) -> None:
    """Test calculating weekly metrics from sessions."""
    week_start = datetime(2024, 1, 1, 0, 0, 0)  # Monday
    metrics = calculate_weekly_metrics(db_with_sessions, week_start)

    assert metrics.user_id == "local"
    assert metrics.week_start == week_start
    assert metrics.session_count == 5
    assert metrics.total_duration_seconds == 9000  # 5 * 1800
    assert metrics.total_turns == 25  # 5 * 5
    assert metrics.total_tool_calls == 50  # 5 * 10
    assert metrics.total_delegations == 10  # 5 * 2
    assert metrics.total_errors == 5  # 5 * 1
    assert metrics.unique_tools == 3  # bash, read_file, delegate
    assert metrics.tool_counts == {"bash": 25, "read_file": 15, "delegate": 10}
    assert set(metrics.top_5_tools) == {"bash", "read_file", "delegate"}
    assert metrics.avg_session_duration == 1800.0
    assert metrics.avg_turns_per_session == 5.0
    assert metrics.delegation_ratio == 2.0  # 10 / 5
    assert metrics.error_rate == 0.1  # 5 / 50


def test_calculate_weekly_metrics_empty_week(tmp_path: Path) -> None:
    """Test calculating metrics for a week with no sessions."""
    db_path = tmp_path / "empty_test.db"
    db = MetricsDB(db_path)

    week_start = datetime(2024, 1, 1, 0, 0, 0)
    metrics = calculate_weekly_metrics(db, week_start)

    assert metrics.session_count == 0
    assert metrics.total_duration_seconds == 0
    assert metrics.total_tool_calls == 0
    assert metrics.unique_tools == 0
    assert metrics.tool_counts == {}
    assert metrics.top_5_tools == []
    assert metrics.avg_session_duration == 0.0
    assert metrics.delegation_ratio == 0.0
    assert metrics.error_rate == 0.0


def test_calculate_weekly_metrics_with_growth(tmp_path: Path) -> None:
    """Test calculating metrics with growth comparison to previous week."""
    db_path = tmp_path / "growth_test.db"
    db = MetricsDB(db_path)

    # Create sessions for previous week
    prev_week_start = datetime(2024, 1, 1, 0, 0, 0)
    prev_sessions = [
        Session(
            session_id=f"prev-session-{i}",
            project_path="/test/project",
            started_at=prev_week_start + timedelta(days=i),
            ended_at=prev_week_start + timedelta(days=i, hours=1),
            duration_seconds=3600,
            turn_count=10,
            tool_call_count=20,
            delegation_count=4,
            error_count=2,
            tool_counts={"bash": 10, "read_file": 6, "delegate": 4},
            model_used="claude-3-5-sonnet-20241022",
            status="completed",
        )
        for i in range(5)  # 5 sessions
    ]

    for session in prev_sessions:
        db.save_session(session)

    # Calculate and save previous week metrics
    prev_metrics = calculate_weekly_metrics(db, prev_week_start)
    db.save_weekly_metrics(prev_metrics)

    # Create sessions for current week (with growth)
    curr_week_start = datetime(2024, 1, 8, 0, 0, 0)
    curr_sessions = [
        Session(
            session_id=f"curr-session-{i}",
            project_path="/test/project",
            started_at=curr_week_start + timedelta(days=i),
            ended_at=curr_week_start + timedelta(days=i, hours=1),
            duration_seconds=3600,
            turn_count=10,
            tool_call_count=20,
            delegation_count=5,  # More delegations
            error_count=1,  # Fewer errors
            tool_counts={"bash": 8, "read_file": 6, "delegate": 5, "grep": 1},  # More diverse
            model_used="claude-3-5-sonnet-20241022",
            status="completed",
        )
        for i in range(7)  # 7 sessions (one week, Mon-Sun)
    ]

    for session in curr_sessions:
        db.save_session(session)

    # Calculate current week metrics (should include growth comparison)
    curr_metrics = calculate_weekly_metrics(db, curr_week_start)

    assert curr_metrics.session_count == 7
    assert curr_metrics.sessions_change_pct == 40.0  # 5 -> 7 = +40%
    assert curr_metrics.unique_tools == 4  # bash, read_file, delegate, grep
    assert curr_metrics.tools_change_pct > 0  # 3 -> 4 tools


def test_calculate_weekly_metrics_top_5_tools(tmp_path: Path) -> None:
    """Test that top_5_tools is correctly limited to 5 tools."""
    db_path = tmp_path / "top5_test.db"
    db = MetricsDB(db_path)

    # Create a session with 10 different tools
    session = Session(
        session_id="multi-tool-session",
        project_path="/test/project",
        started_at=datetime(2024, 1, 1, 10, 0, 0),
        ended_at=datetime(2024, 1, 1, 11, 0, 0),
        duration_seconds=3600,
        turn_count=10,
        tool_call_count=55,
        delegation_count=5,
        error_count=0,
        tool_counts={
            "bash": 20,
            "read_file": 10,
            "delegate": 5,
            "grep": 5,
            "edit_file": 5,
            "glob": 4,
            "write_file": 3,
            "LSP": 2,
            "python_check": 1,
        },
        model_used="claude-3-5-sonnet-20241022",
        status="completed",
    )

    db.save_session(session)

    week_start = datetime(2024, 1, 1, 0, 0, 0)
    metrics = calculate_weekly_metrics(db, week_start)

    assert metrics.unique_tools == 9
    assert len(metrics.top_5_tools) == 5
    # Check that top 5 are actually the most used
    assert metrics.top_5_tools[0] == "bash"  # 20 calls
    assert metrics.top_5_tools[1] == "read_file"  # 10 calls


def test_calculate_weekly_metrics_division_by_zero(tmp_path: Path) -> None:
    """Test metrics calculation handles edge cases without crashing."""
    db_path = tmp_path / "edge_test.db"
    db = MetricsDB(db_path)

    # Session with zero tool calls
    session = Session(
        session_id="zero-tools-session",
        project_path="/test/project",
        started_at=datetime(2024, 1, 1, 10, 0, 0),
        ended_at=datetime(2024, 1, 1, 10, 0, 10),
        duration_seconds=10,
        turn_count=1,
        tool_call_count=0,
        delegation_count=0,
        error_count=0,
        tool_counts={},
        model_used="claude-3-5-sonnet-20241022",
        status="completed",
    )

    db.save_session(session)

    week_start = datetime(2024, 1, 1, 0, 0, 0)
    metrics = calculate_weekly_metrics(db, week_start)

    assert metrics.session_count == 1
    assert metrics.error_rate == 0.0  # Should handle 0 / 0 gracefully
    assert metrics.delegation_ratio == 0.0
    assert metrics.unique_tools == 0
