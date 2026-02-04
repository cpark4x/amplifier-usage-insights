"""Insights engine for querying and formatting usage metrics."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, TypedDict

from .metrics import calculate_weekly_metrics, get_week_start
from .storage import MetricsDB
from .tips import RuleTip, generate_tips


class InsightsSummary(TypedDict):
    """Structured insights data."""

    summary: str
    metrics: dict[str, Any]
    growth: dict[str, Any]
    tips: list[RuleTip]


class InsightsEngine:
    """Query interface for V0.5 conversational tool."""

    def __init__(self, db_path: Path | str):
        """
        Initialize insights engine with database connection.

        Args:
            db_path: Path to SQLite database (e.g., ~/.amplifier-usage-insights/metrics.db)
        """
        self.db = MetricsDB(db_path)

    def query_weekly_summary(self, time_range: str = "this_week") -> InsightsSummary:
        """
        Get weekly summary for conversational response.

        Args:
            time_range: Which week to query - "this_week" or "last_week"

        Returns:
            {
                "summary": "12 sessions this week, up 50% from last week",
                "metrics": {
                    "sessions": {"count": 12, "change": "+50%"},
                    "tools": {"unique": 8, "top_5": ["bash", "delegate", ...]},
                    "effectiveness": {"avg_duration": "25min", "delegation_ratio": 0.4}
                },
                "growth": {
                    "trend": "improving",
                    "strongest_area": "delegation",
                    "areas_to_improve": ["error_handling"]
                },
                "tips": [RuleTip(...), ...]
            }

        Example:
            >>> engine = InsightsEngine("~/.amplifier-usage-insights/metrics.db")
            >>> summary = engine.query_weekly_summary()
            >>> assert "summary" in summary
        """
        # Determine which week to query
        now = datetime.now()
        if time_range == "this_week":
            week_start = get_week_start(now)
        elif time_range == "last_week":
            week_start = get_week_start(now - timedelta(days=7))
        else:
            week_start = get_week_start(now)

        # Get or compute weekly metrics
        current_week = self.db.get_weekly_metrics(week_start)
        if current_week is None:
            # Not computed yet - compute now
            current_week = calculate_weekly_metrics(self.db, week_start)
            self.db.save_weekly_metrics(current_week)

        # Get previous week for comparison
        previous_week_start = week_start - timedelta(days=7)
        previous_week = self.db.get_weekly_metrics(previous_week_start)

        # Generate tips
        tips = generate_tips(current_week, previous_week)

        # Build summary text
        summary_parts = []
        summary_parts.append(f"{current_week.session_count} sessions this week")

        if current_week.sessions_change_pct is not None:
            change = current_week.sessions_change_pct
            if change > 0:
                summary_parts.append(f"up {change:.0f}% from last week")
            elif change < 0:
                summary_parts.append(f"down {abs(change):.0f}% from last week")
            else:
                summary_parts.append("same as last week")

        summary = ", ".join(summary_parts)

        # Identify strongest area and areas to improve
        strongest_area = "unknown"
        areas_to_improve = []

        if previous_week is not None:
            growth_scores = {
                "delegation": current_week.delegation_change_pct or 0,
                "tool_diversity": current_week.tools_change_pct or 0,
                "error_handling": -(
                    current_week.error_change_pct or 0
                ),  # Negative because fewer errors is better
            }

            # Strongest area is highest positive change
            strongest_area = max(growth_scores.items(), key=lambda x: x[1])[0]

            # Areas to improve are negative changes
            for area, change in growth_scores.items():
                if change < -5:  # Declining by more than 5%
                    areas_to_improve.append(area)

        # Determine overall trend
        trend = "stable"
        if current_week.sessions_change_pct is not None:
            if current_week.sessions_change_pct > 10:
                trend = "improving"
            elif current_week.sessions_change_pct < -10:
                trend = "declining"

        return {
            "summary": summary,
            "metrics": {
                "sessions": {
                    "count": current_week.session_count,
                    "change": f"{current_week.sessions_change_pct:+.0f}%"
                    if current_week.sessions_change_pct is not None
                    else "N/A",
                    "total_duration": f"{current_week.total_duration_seconds // 3600}h {(current_week.total_duration_seconds % 3600) // 60}m",
                },
                "tools": {
                    "unique": current_week.unique_tools,
                    "top_5": current_week.top_5_tools,
                    "total_calls": current_week.total_tool_calls,
                },
                "effectiveness": {
                    "avg_duration": f"{current_week.avg_session_duration / 60:.0f}min",
                    "delegation_ratio": current_week.delegation_ratio,
                    "error_rate": current_week.error_rate,
                },
            },
            "growth": {
                "trend": trend,
                "strongest_area": strongest_area,
                "areas_to_improve": areas_to_improve,
            },
            "tips": tips,
        }

    def query_tool_usage(self) -> dict[str, int | list[tuple[str, int]]]:
        """
        Get tool usage breakdown.

        Returns:
            {
                "total_calls": 150,
                "unique_tools": 8,
                "top_tools": [("bash", 45), ("delegate", 32), ...]
            }
        """
        tool_counts = self.db.get_tool_usage_summary()
        sorted_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            "total_calls": sum(tool_counts.values()),
            "unique_tools": len(tool_counts),
            "top_tools": sorted_tools,
        }

    def query_growth(self) -> dict[str, str | float | None]:
        """
        Get growth indicators.

        Returns:
            {
                "current_week_sessions": 12,
                "previous_week_sessions": 8,
                "sessions_change": "+50%",
                "trend": "improving",
                "delegation_change": "+20%",
                "error_change": "-10%"
            }
        """
        # Get current and previous week
        now = datetime.now()
        current_week_start = get_week_start(now)
        previous_week_start = current_week_start - timedelta(days=7)

        current_week = self.db.get_weekly_metrics(current_week_start)
        if current_week is None:
            current_week = calculate_weekly_metrics(self.db, current_week_start)
            self.db.save_weekly_metrics(current_week)

        previous_week = self.db.get_weekly_metrics(previous_week_start)

        return {
            "current_week_sessions": current_week.session_count,
            "previous_week_sessions": previous_week.session_count if previous_week else 0,
            "sessions_change": f"{current_week.sessions_change_pct:+.0f}%"
            if current_week.sessions_change_pct is not None
            else "N/A",
            "delegation_change": f"{current_week.delegation_change_pct:+.0f}%"
            if current_week.delegation_change_pct is not None
            else "N/A",
            "error_change": f"{current_week.error_change_pct:+.0f}%"
            if current_week.error_change_pct is not None
            else "N/A",
            "tools_change": f"{current_week.tools_change_pct:+.0f}%"
            if current_week.tools_change_pct is not None
            else "N/A",
            "trend": "improving"
            if current_week.sessions_change_pct and current_week.sessions_change_pct > 10
            else "stable",
        }


def format_conversational_response(data: InsightsSummary) -> str:
    """
    Format insights data for natural language response.

    Input: query_weekly_summary() output

    Output: Human-readable string like:

    "You're showing strong growth! 🚀

    This Week vs Last Week:
    • 12 sessions (+50% from 8 last week)
    • 8 different tools used (up from 6)
    • Delegation ratio: 40% (you're breaking down problems well!)
    • Error rate: 12% (slightly higher than last week)

    Growth Area: Error Handling
    Your error rate increased 10% this week. When you hit errors,
    try asking for alternative approaches instead of retrying the same path.

    Top Tools This Week:
    1. bash (45 calls) - consider using grep/glob for file operations
    2. delegate (32 calls) - great job breaking down problems!
    3. read_file (28 calls)
    4. edit_file (18 calls)
    5. grep (12 calls)

    Overall trend: Improving 📈 (3 weeks of growth)"

    Args:
        data: Output from query_weekly_summary()

    Returns:
        Formatted conversational response string
    """
    lines = []

    # Header based on trend
    trend = data["growth"]["trend"]
    if trend == "improving":
        lines.append("You're showing strong growth! 🚀\n")
    elif trend == "declining":
        lines.append("Let's look at your week and find opportunities to improve.\n")
    else:
        lines.append("Here's your weekly summary:\n")

    # Metrics section
    lines.append("This Week vs Last Week:")
    metrics = data["metrics"]

    sessions_info = metrics["sessions"]
    lines.append(f"• {sessions_info['count']} sessions ({sessions_info['change']})")

    tools_info = metrics["tools"]
    lines.append(f"• {tools_info['unique']} different tools used")

    effectiveness = metrics["effectiveness"]
    delegation_pct = effectiveness["delegation_ratio"] * 100
    lines.append(f"• Delegation ratio: {delegation_pct:.0f}%")

    error_pct = effectiveness["error_rate"] * 100
    lines.append(f"• Error rate: {error_pct:.0f}%")
    lines.append(f"• Avg session duration: {effectiveness['avg_duration']}")

    lines.append("")  # Blank line

    # Top tools section
    if tools_info["top_5"]:
        lines.append("Top Tools This Week:")
        for i, tool_name in enumerate(tools_info["top_5"], 1):
            lines.append(f"{i}. {tool_name}")
        lines.append("")

    # Tips section
    tips = data["tips"]
    if tips:
        lines.append(f"💡 {len(tips)} Tips for Improvement:")
        for tip in tips[:3]:  # Show top 3 tips
            lines.append(f"\n[{tip.priority.upper()}] {tip.category}")
            lines.append(f"📊 {tip.observation}")
            lines.append(f"💡 {tip.recommendation}")
            lines.append(f"✨ {tip.expected_benefit}")
        lines.append("")

    # Overall trend
    if trend != "stable":
        lines.append(
            f"Overall trend: {trend.capitalize()} {'📈' if trend == 'improving' else '📉'}"
        )

    return "\n".join(lines)


def get_personal_insights(query: str = "How am I doing this week?") -> dict[str, Any]:
    """
    Tool implementation for Amplifier.

    Called when user asks about their AI usage in any Amplifier session.

    Args:
        query: Natural language query about AI usage

    Returns:
        {
            "response": "Formatted conversational response",
            "data": {...}  # Structured data
        }

    Example:
        >>> result = get_personal_insights("How am I doing?")
        >>> assert "response" in result
        >>> assert "data" in result
    """
    # Initialize engine
    db_path = Path.home() / ".amplifier-usage-insights" / "metrics.db"

    # Ensure database exists
    if not db_path.exists():
        return {
            "response": "No insights data found. Run `amplifier-insights init` and `amplifier-insights refresh` first.",
            "data": {},
        }

    engine = InsightsEngine(db_path)

    # Simple query routing based on keywords
    query_lower = query.lower()

    if "tool" in query_lower and ("what" in query_lower or "which" in query_lower):
        # Tool usage query
        data = engine.query_tool_usage()
        response = format_tool_usage_response(data)
    elif "grow" in query_lower or "improv" in query_lower or "progress" in query_lower:
        # Growth query
        data = engine.query_growth()
        response = format_growth_response(data)
    else:
        # Default: weekly summary
        summary_data = engine.query_weekly_summary()
        response = format_conversational_response(summary_data)
        data = summary_data

    return {
        "response": response,
        "data": data,
    }


def format_tool_usage_response(data: dict[str, Any]) -> str:
    """
    Format tool usage data for conversational response.

    Args:
        data: Output from query_tool_usage()

    Returns:
        Formatted string showing tool usage breakdown
    """
    lines = []
    lines.append("📊 Your Tool Usage:\n")
    lines.append(f"Total tool calls: {data['total_calls']}")
    lines.append(f"Unique tools: {data['unique_tools']}\n")

    lines.append("Top Tools:")
    top_tools = data["top_tools"]
    if isinstance(top_tools, list):
        for i, (tool_name, count) in enumerate(top_tools[:10], 1):
            total_calls = data["total_calls"]
            pct = (
                (count / total_calls * 100)
                if isinstance(total_calls, int) and total_calls > 0
                else 0
            )
            lines.append(f"{i}. {tool_name}: {count} calls ({pct:.0f}%)")

    return "\n".join(lines)


def format_growth_response(data: dict[str, Any]) -> str:
    """
    Format growth data for conversational response.

    Args:
        data: Output from query_growth()

    Returns:
        Formatted string showing growth trends
    """
    lines = []
    lines.append("📈 Your Growth This Week:\n")

    current = data["current_week_sessions"]
    previous = data["previous_week_sessions"]

    lines.append(f"Sessions: {current} (was {previous} last week)")
    lines.append(f"Session growth: {data['sessions_change']}")
    lines.append(f"Delegation growth: {data['delegation_change']}")
    lines.append(f"Tool diversity growth: {data['tools_change']}")
    lines.append(f"Error rate change: {data['error_change']}")

    trend = data["trend"]
    trend_str = trend.capitalize() if isinstance(trend, str) else "Unknown"
    lines.append(f"\nOverall trend: {trend_str}")

    return "\n".join(lines)
