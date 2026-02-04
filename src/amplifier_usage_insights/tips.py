"""Rule-based tips generation for actionable insights."""

from dataclasses import dataclass
from datetime import datetime

from .metrics import WeeklyMetrics


@dataclass
class RuleTip:
    """Rule-based actionable tip."""

    rule_id: str  # "high_bash_usage", "low_delegation", etc.
    category: str  # "tool_usage", "delegation", "error_handling"
    priority: str  # "high", "medium", "low"

    # The tip
    observation: str
    recommendation: str
    expected_benefit: str

    # When generated
    generated_at: datetime
    based_on_week: datetime


def rule_high_bash_usage(metrics: WeeklyMetrics) -> RuleTip | None:
    """Suggest grep/glob if bash is overused."""
    bash_count = metrics.tool_counts.get("bash", 0)
    total_calls = metrics.total_tool_calls

    if total_calls == 0:
        return None

    bash_pct = bash_count / total_calls

    if bash_pct > 0.30:  # >30% bash usage
        return RuleTip(
            rule_id="high_bash_usage",
            category="tool_usage",
            priority="medium",
            observation=f"You use bash {bash_pct:.0%} of the time ({bash_count} calls this week)",
            recommendation="Try using grep for searching files and glob for finding files instead of bash commands",
            expected_benefit="30% faster file operations with specialized tools",
            generated_at=datetime.now(),
            based_on_week=metrics.week_start,
        )

    return None


def rule_low_delegation(metrics: WeeklyMetrics) -> RuleTip | None:
    """Suggest breaking down problems if delegation is low."""
    if metrics.session_count == 0:
        return None

    delegation_ratio = metrics.delegation_ratio

    if delegation_ratio < 0.3:  # <30% delegation rate
        return RuleTip(
            rule_id="low_delegation",
            category="delegation",
            priority="high",
            observation=f"Your delegation ratio is {delegation_ratio:.0%} ({metrics.total_delegations} delegations in {metrics.session_count} sessions)",
            recommendation="Break down complex problems into smaller tasks and delegate to specialized agents",
            expected_benefit="Better results through specialized expertise and reduced cognitive load",
            generated_at=datetime.now(),
            based_on_week=metrics.week_start,
        )

    return None


def rule_high_error_rate(metrics: WeeklyMetrics) -> RuleTip | None:
    """Suggest asking for alternatives if error rate is high."""
    if metrics.total_tool_calls == 0:
        return None

    error_rate = metrics.error_rate

    if error_rate > 0.15:  # >15% error rate
        return RuleTip(
            rule_id="high_error_rate",
            category="error_handling",
            priority="high",
            observation=f"Your error rate is {error_rate:.0%} ({metrics.total_errors} errors in {metrics.total_tool_calls} tool calls)",
            recommendation="When you hit errors, try asking for alternative approaches instead of retrying the same path",
            expected_benefit="Faster problem resolution and less frustration",
            generated_at=datetime.now(),
            based_on_week=metrics.week_start,
        )

    return None


def rule_declining_tool_diversity(
    current: WeeklyMetrics, previous: WeeklyMetrics | None
) -> RuleTip | None:
    """Suggest exploring new tools if diversity is declining."""
    if previous is None or current.session_count == 0:
        return None

    # Check if tool diversity decreased
    if current.unique_tools < previous.unique_tools:
        decline_count = previous.unique_tools - current.unique_tools

        return RuleTip(
            rule_id="declining_tool_diversity",
            category="tool_usage",
            priority="medium",
            observation=f"You're using {decline_count} fewer tools this week ({current.unique_tools} vs {previous.unique_tools} last week)",
            recommendation="Explore the full toolkit - try using tools you haven't used recently",
            expected_benefit="Increased effectiveness by choosing the right tool for each task",
            generated_at=datetime.now(),
            based_on_week=current.week_start,
        )

    return None


def rule_long_sessions(metrics: WeeklyMetrics) -> RuleTip | None:
    """Suggest smaller tasks if sessions are getting too long."""
    if metrics.session_count == 0:
        return None

    avg_duration_minutes = metrics.avg_session_duration / 60

    if avg_duration_minutes > 60:  # >60 minutes average
        return RuleTip(
            rule_id="long_sessions",
            category="task_management",
            priority="medium",
            observation=f"Your average session is {avg_duration_minutes:.0f} minutes ({metrics.session_count} sessions this week)",
            recommendation="Break work into smaller, focused tasks for better concentration and faster iterations",
            expected_benefit="Better focus and more frequent completion milestones",
            generated_at=datetime.now(),
            based_on_week=metrics.week_start,
        )

    return None


def generate_tips(
    current_week: WeeklyMetrics, previous_week: WeeklyMetrics | None
) -> list[RuleTip]:
    """
    Generate tips based on simple pattern matching.

    Rules:
    1. If bash usage > 30% of total tools → suggest grep/glob
    2. If delegation_ratio < 0.3 → suggest breaking down problems
    3. If error_rate > 0.15 → suggest asking for alternatives
    4. If unique_tools declining → suggest exploring new tools
    5. If avg_session_duration > 60min → suggest smaller tasks

    Args:
        current_week: Current week's metrics
        previous_week: Previous week's metrics (None if first week)

    Returns:
        List of 0-5 tips (only triggered rules)

    Example:
        >>> metrics = WeeklyMetrics(...)
        >>> tips = generate_tips(metrics, None)
        >>> assert all(isinstance(tip, RuleTip) for tip in tips)
    """
    tips = []

    # Apply each rule
    tip = rule_high_bash_usage(current_week)
    if tip:
        tips.append(tip)

    tip = rule_low_delegation(current_week)
    if tip:
        tips.append(tip)

    tip = rule_high_error_rate(current_week)
    if tip:
        tips.append(tip)

    tip = rule_declining_tool_diversity(current_week, previous_week)
    if tip:
        tips.append(tip)

    tip = rule_long_sessions(current_week)
    if tip:
        tips.append(tip)

    # Sort by priority (high > medium > low)
    priority_order = {"high": 0, "medium": 1, "low": 2}
    tips.sort(key=lambda t: priority_order.get(t.priority, 3))

    return tips
