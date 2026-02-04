"""Metrics calculation and growth tracking."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TypedDict

from .storage import MetricsDB


class GrowthIndicators(TypedDict):
    """Growth comparison results."""

    sessions_change_pct: float | None
    tools_change_pct: float | None
    delegation_change_pct: float | None
    error_change_pct: float | None
    trend: str  # "improving", "declining", "stable"


@dataclass
class WeeklyMetrics:
    """Aggregated metrics for one week."""

    # Identity
    user_id: str  # "local" for V0.5
    week_start: datetime  # Monday of the week

    # Volume
    session_count: int
    total_duration_seconds: int
    total_turns: int
    total_tool_calls: int
    total_delegations: int
    total_errors: int

    # Tool usage
    unique_tools: int
    tool_counts: dict[str, int]  # Aggregated across week
    top_5_tools: list[str]

    # Derived metrics
    avg_session_duration: float
    avg_turns_per_session: float
    delegation_ratio: float  # delegations / total_sessions
    error_rate: float  # errors / tool_calls

    # Growth (compare to previous week)
    sessions_change_pct: float | None  # +15% or -10%
    tools_change_pct: float | None
    delegation_change_pct: float | None
    error_change_pct: float | None


def get_week_start(dt: datetime) -> datetime:
    """
    Get Monday 00:00:00 for the week containing dt.

    Args:
        dt: Any datetime within the week

    Returns:
        Monday at 00:00:00 for that week

    Example:
        >>> dt = datetime(2024, 1, 3)  # Wednesday
        >>> week_start = get_week_start(dt)
        >>> week_start.weekday()  # 0 = Monday
        0
    """
    # Get days since Monday (0 = Monday, 6 = Sunday)
    days_since_monday = dt.weekday()

    # Subtract days to get to Monday
    monday = dt - timedelta(days=days_since_monday)

    # Set time to 00:00:00
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def calculate_growth(current: WeeklyMetrics, previous: WeeklyMetrics | None) -> GrowthIndicators:
    """
    Calculate growth indicators.

    Args:
        current: Current week's metrics
        previous: Previous week's metrics (None if first week)

    Returns:
        {
            "sessions_change_pct": 15.0,  # +15%
            "tools_change_pct": 0.0,
            "delegation_change_pct": -5.0,  # -5%
            "error_change_pct": 10.0,
            "trend": "improving",  # or "declining", "stable"
        }

    Trend Logic:
        improving: sessions up, delegation up, errors down, tools up (score >= 3)
        declining: opposite (score <= 1)
        stable: mixed signals or <10% changes
    """
    if previous is None:
        return {
            "sessions_change_pct": None,
            "tools_change_pct": None,
            "delegation_change_pct": None,
            "error_change_pct": None,
            "trend": "stable",
        }

    # Calculate % changes (handle division by zero)
    def pct_change(current_val: float, previous_val: float) -> float:
        if previous_val == 0:
            return 100.0 if current_val > 0 else 0.0
        return ((current_val - previous_val) / previous_val) * 100

    sessions_change = pct_change(current.session_count, previous.session_count)
    tools_change = pct_change(current.unique_tools, previous.unique_tools)
    delegation_change = pct_change(current.delegation_ratio, previous.delegation_ratio)
    error_change = pct_change(current.error_rate, previous.error_rate)

    # Determine trend (simple scoring)
    score = 0
    if sessions_change > 10:
        score += 1  # More sessions is good
    if current.delegation_ratio > previous.delegation_ratio:
        score += 1  # More delegation is good
    if current.error_rate < previous.error_rate:
        score += 1  # Fewer errors is good
    if current.unique_tools > previous.unique_tools:
        score += 1  # More tool diversity is good

    trend = "improving" if score >= 3 else "declining" if score <= 1 else "stable"

    return {
        "sessions_change_pct": sessions_change,
        "tools_change_pct": tools_change,
        "delegation_change_pct": delegation_change,
        "error_change_pct": error_change,
        "trend": trend,
    }


def calculate_weekly_metrics(db: MetricsDB, week_start: datetime) -> WeeklyMetrics:
    """
    Aggregate all sessions in week into WeeklyMetrics.

    Queries all sessions where started_at in [week_start, week_start + 7 days),
    computes counts, averages, ratios, and compares to previous week.

    Args:
        db: MetricsDB instance
        week_start: Monday 00:00:00 for the week to calculate

    Returns:
        WeeklyMetrics with all fields populated including growth indicators

    Example:
        >>> db = MetricsDB("~/.amplifier-usage-insights/metrics.db")
        >>> week_start = get_week_start(datetime.now())
        >>> metrics = calculate_weekly_metrics(db, week_start)
        >>> assert metrics.session_count >= 0
    """
    week_end = week_start + timedelta(days=7)

    # Get all sessions in this week
    sessions = db.get_sessions_in_range(week_start, week_end)

    # If no sessions, return empty metrics
    if not sessions:
        return WeeklyMetrics(
            user_id="local",
            week_start=week_start,
            session_count=0,
            total_duration_seconds=0,
            total_turns=0,
            total_tool_calls=0,
            total_delegations=0,
            total_errors=0,
            unique_tools=0,
            tool_counts={},
            top_5_tools=[],
            avg_session_duration=0.0,
            avg_turns_per_session=0.0,
            delegation_ratio=0.0,
            error_rate=0.0,
            sessions_change_pct=None,
            tools_change_pct=None,
            delegation_change_pct=None,
            error_change_pct=None,
        )

    # Aggregate volume metrics
    session_count = len(sessions)
    total_duration_seconds = sum(s.duration_seconds for s in sessions)
    total_turns = sum(s.turn_count for s in sessions)
    total_tool_calls = sum(s.tool_call_count for s in sessions)
    total_delegations = sum(s.delegation_count for s in sessions)
    total_errors = sum(s.error_count for s in sessions)

    # Aggregate tool usage
    tool_counts: dict[str, int] = {}
    for session in sessions:
        for tool_name, count in session.tool_counts.items():
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + count

    unique_tools = len(tool_counts)

    # Get top 5 tools by usage
    sorted_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)
    top_5_tools = [tool_name for tool_name, _ in sorted_tools[:5]]

    # Calculate derived metrics
    avg_session_duration = total_duration_seconds / session_count if session_count > 0 else 0.0
    avg_turns_per_session = total_turns / session_count if session_count > 0 else 0.0
    delegation_ratio = total_delegations / session_count if session_count > 0 else 0.0
    error_rate = total_errors / total_tool_calls if total_tool_calls > 0 else 0.0

    # Create current week metrics (without growth data yet)
    current_week = WeeklyMetrics(
        user_id="local",
        week_start=week_start,
        session_count=session_count,
        total_duration_seconds=total_duration_seconds,
        total_turns=total_turns,
        total_tool_calls=total_tool_calls,
        total_delegations=total_delegations,
        total_errors=total_errors,
        unique_tools=unique_tools,
        tool_counts=tool_counts,
        top_5_tools=top_5_tools,
        avg_session_duration=avg_session_duration,
        avg_turns_per_session=avg_turns_per_session,
        delegation_ratio=delegation_ratio,
        error_rate=error_rate,
        sessions_change_pct=None,
        tools_change_pct=None,
        delegation_change_pct=None,
        error_change_pct=None,
    )

    # Get previous week's metrics for growth comparison
    previous_week_start = week_start - timedelta(days=7)
    previous_week = db.get_weekly_metrics(previous_week_start)

    # Calculate growth
    growth = calculate_growth(current_week, previous_week)

    # Update growth fields
    current_week.sessions_change_pct = growth["sessions_change_pct"]
    current_week.tools_change_pct = growth["tools_change_pct"]
    current_week.delegation_change_pct = growth["delegation_change_pct"]
    current_week.error_change_pct = growth["error_change_pct"]

    return current_week
