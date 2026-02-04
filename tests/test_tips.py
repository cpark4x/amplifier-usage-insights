"""Tests for rule-based tips generation."""

from datetime import datetime

import pytest

from amplifier_usage_insights.metrics import WeeklyMetrics
from amplifier_usage_insights.tips import (
    RuleTip,
    generate_tips,
    rule_declining_tool_diversity,
    rule_high_bash_usage,
    rule_high_error_rate,
    rule_long_sessions,
    rule_low_delegation,
)


@pytest.fixture
def baseline_metrics() -> WeeklyMetrics:
    """Create baseline metrics for testing."""
    return WeeklyMetrics(
        user_id="local",
        week_start=datetime(2024, 1, 1),
        session_count=10,
        total_duration_seconds=18000,  # 5 hours
        total_turns=50,
        total_tool_calls=100,
        total_delegations=30,
        total_errors=10,
        unique_tools=8,
        tool_counts={"bash": 30, "read_file": 20, "delegate": 30, "grep": 10, "edit_file": 10},
        top_5_tools=["bash", "delegate", "read_file", "grep", "edit_file"],
        avg_session_duration=1800.0,  # 30 min
        avg_turns_per_session=5.0,
        delegation_ratio=3.0,
        error_rate=0.10,
        sessions_change_pct=None,
        tools_change_pct=None,
        delegation_change_pct=None,
        error_change_pct=None,
    )


def test_rule_high_bash_usage_triggered(baseline_metrics: WeeklyMetrics) -> None:
    """Test high bash usage rule triggers when bash > 30%."""
    # bash is 30/100 = 30% (exactly at threshold)
    tip = rule_high_bash_usage(baseline_metrics)
    assert tip is None  # Should not trigger at exactly 30%

    # Increase bash to >30%
    baseline_metrics.tool_counts["bash"] = 35
    tip = rule_high_bash_usage(baseline_metrics)

    assert tip is not None
    assert tip.rule_id == "high_bash_usage"
    assert tip.category == "tool_usage"
    assert tip.priority == "medium"
    assert "bash" in tip.observation.lower()
    assert "grep" in tip.recommendation.lower() or "glob" in tip.recommendation.lower()


def test_rule_high_bash_usage_not_triggered(baseline_metrics: WeeklyMetrics) -> None:
    """Test high bash usage rule does not trigger when bash < 30%."""
    baseline_metrics.tool_counts["bash"] = 20  # 20/100 = 20%
    tip = rule_high_bash_usage(baseline_metrics)

    assert tip is None


def test_rule_low_delegation_triggered(baseline_metrics: WeeklyMetrics) -> None:
    """Test low delegation rule triggers when delegation ratio < 0.3."""
    baseline_metrics.delegation_ratio = 0.2  # 20% delegation
    baseline_metrics.total_delegations = 2

    tip = rule_low_delegation(baseline_metrics)

    assert tip is not None
    assert tip.rule_id == "low_delegation"
    assert tip.category == "delegation"
    assert tip.priority == "high"
    assert "delegation" in tip.observation.lower()
    assert "break down" in tip.recommendation.lower() or "delegate" in tip.recommendation.lower()


def test_rule_low_delegation_not_triggered(baseline_metrics: WeeklyMetrics) -> None:
    """Test low delegation rule does not trigger when delegation ratio >= 0.3."""
    baseline_metrics.delegation_ratio = 0.5  # 50% delegation
    tip = rule_low_delegation(baseline_metrics)

    assert tip is None


def test_rule_high_error_rate_triggered(baseline_metrics: WeeklyMetrics) -> None:
    """Test high error rate rule triggers when error rate > 15%."""
    baseline_metrics.error_rate = 0.20  # 20% error rate
    baseline_metrics.total_errors = 20

    tip = rule_high_error_rate(baseline_metrics)

    assert tip is not None
    assert tip.rule_id == "high_error_rate"
    assert tip.category == "error_handling"
    assert tip.priority == "high"
    assert "error" in tip.observation.lower()
    assert "alternative" in tip.recommendation.lower() or "retry" in tip.recommendation.lower()


def test_rule_high_error_rate_not_triggered(baseline_metrics: WeeklyMetrics) -> None:
    """Test high error rate rule does not trigger when error rate <= 15%."""
    baseline_metrics.error_rate = 0.10  # 10% error rate
    tip = rule_high_error_rate(baseline_metrics)

    assert tip is None


def test_rule_declining_tool_diversity_triggered(baseline_metrics: WeeklyMetrics) -> None:
    """Test declining tool diversity rule triggers when unique_tools decreases."""
    previous = WeeklyMetrics(
        user_id="local",
        week_start=datetime(2024, 1, 1),
        session_count=10,
        total_duration_seconds=18000,
        total_turns=50,
        total_tool_calls=100,
        total_delegations=30,
        total_errors=10,
        unique_tools=12,  # More tools last week
        tool_counts={"bash": 30},
        top_5_tools=["bash"],
        avg_session_duration=1800.0,
        avg_turns_per_session=5.0,
        delegation_ratio=3.0,
        error_rate=0.10,
        sessions_change_pct=None,
        tools_change_pct=None,
        delegation_change_pct=None,
        error_change_pct=None,
    )

    current = baseline_metrics
    current.unique_tools = 8  # Fewer tools this week

    tip = rule_declining_tool_diversity(current, previous)

    assert tip is not None
    assert tip.rule_id == "declining_tool_diversity"
    assert tip.category == "tool_usage"
    assert tip.priority == "medium"
    assert "fewer tools" in tip.observation.lower() or "diversity" in tip.observation.lower()
    assert "explore" in tip.recommendation.lower()


def test_rule_declining_tool_diversity_not_triggered(baseline_metrics: WeeklyMetrics) -> None:
    """Test declining tool diversity rule does not trigger when tools increase or stay same."""
    previous = WeeklyMetrics(
        user_id="local",
        week_start=datetime(2024, 1, 1),
        session_count=10,
        total_duration_seconds=18000,
        total_turns=50,
        total_tool_calls=100,
        total_delegations=30,
        total_errors=10,
        unique_tools=8,  # Same as current
        tool_counts={"bash": 30},
        top_5_tools=["bash"],
        avg_session_duration=1800.0,
        avg_turns_per_session=5.0,
        delegation_ratio=3.0,
        error_rate=0.10,
        sessions_change_pct=None,
        tools_change_pct=None,
        delegation_change_pct=None,
        error_change_pct=None,
    )

    tip = rule_declining_tool_diversity(baseline_metrics, previous)
    assert tip is None  # Same number of tools


def test_rule_declining_tool_diversity_no_previous(baseline_metrics: WeeklyMetrics) -> None:
    """Test declining tool diversity rule with no previous week."""
    tip = rule_declining_tool_diversity(baseline_metrics, None)
    assert tip is None


def test_rule_long_sessions_triggered(baseline_metrics: WeeklyMetrics) -> None:
    """Test long sessions rule triggers when avg duration > 60 min."""
    baseline_metrics.avg_session_duration = 4000.0  # ~67 minutes
    tip = rule_long_sessions(baseline_metrics)

    assert tip is not None
    assert tip.rule_id == "long_sessions"
    assert tip.category == "task_management"
    assert tip.priority == "medium"
    assert "minutes" in tip.observation or "session" in tip.observation.lower()
    assert "smaller" in tip.recommendation.lower() or "break" in tip.recommendation.lower()


def test_rule_long_sessions_not_triggered(baseline_metrics: WeeklyMetrics) -> None:
    """Test long sessions rule does not trigger when avg duration <= 60 min."""
    baseline_metrics.avg_session_duration = 1800.0  # 30 minutes
    tip = rule_long_sessions(baseline_metrics)

    assert tip is None


def test_generate_tips_no_rules_triggered(baseline_metrics: WeeklyMetrics) -> None:
    """Test generate_tips returns empty list when no rules trigger."""
    # Baseline metrics are designed to not trigger any rules
    baseline_metrics.tool_counts["bash"] = 20  # < 30%
    baseline_metrics.delegation_ratio = 0.5  # > 0.3
    baseline_metrics.error_rate = 0.10  # < 0.15
    baseline_metrics.avg_session_duration = 1800.0  # 30 min

    tips = generate_tips(baseline_metrics, None)

    assert tips == []


def test_generate_tips_multiple_rules() -> None:
    """Test generate_tips with multiple rules triggered."""
    metrics = WeeklyMetrics(
        user_id="local",
        week_start=datetime(2024, 1, 1),
        session_count=10,
        total_duration_seconds=40000,  # Long sessions
        total_turns=50,
        total_tool_calls=100,
        total_delegations=2,  # Low delegation
        total_errors=20,  # High errors
        unique_tools=5,
        tool_counts={"bash": 50, "read_file": 30, "delegate": 2},  # High bash
        top_5_tools=["bash", "read_file", "delegate"],
        avg_session_duration=4000.0,  # ~67 minutes
        avg_turns_per_session=5.0,
        delegation_ratio=0.2,  # Low
        error_rate=0.20,  # High
        sessions_change_pct=None,
        tools_change_pct=None,
        delegation_change_pct=None,
        error_change_pct=None,
    )

    tips = generate_tips(metrics, None)

    # Should trigger: high_bash, low_delegation, high_error_rate, long_sessions
    assert len(tips) >= 4

    # Verify we got the expected tips
    rule_ids = {tip.rule_id for tip in tips}
    assert "high_bash_usage" in rule_ids
    assert "low_delegation" in rule_ids
    assert "high_error_rate" in rule_ids
    assert "long_sessions" in rule_ids

    # Verify priority sorting (high priority tips first)
    priorities = [tip.priority for tip in tips]
    high_count = priorities.count("high")
    assert high_count > 0

    # First tips should be high priority
    if len(tips) > 1:
        assert tips[0].priority in ["high", "medium"]


def test_generate_tips_with_growth() -> None:
    """Test generate_tips includes growth-based tips."""
    previous = WeeklyMetrics(
        user_id="local",
        week_start=datetime(2024, 1, 1),
        session_count=10,
        total_duration_seconds=18000,
        total_turns=50,
        total_tool_calls=100,
        total_delegations=30,
        total_errors=10,
        unique_tools=10,
        tool_counts={"bash": 30},
        top_5_tools=["bash"],
        avg_session_duration=1800.0,
        avg_turns_per_session=5.0,
        delegation_ratio=3.0,
        error_rate=0.10,
        sessions_change_pct=None,
        tools_change_pct=None,
        delegation_change_pct=None,
        error_change_pct=None,
    )

    current = WeeklyMetrics(
        user_id="local",
        week_start=datetime(2024, 1, 8),
        session_count=8,
        total_duration_seconds=14400,
        total_turns=40,
        total_tool_calls=80,
        total_delegations=24,
        total_errors=8,
        unique_tools=6,  # Declined from 10
        tool_counts={"bash": 30},
        top_5_tools=["bash"],
        avg_session_duration=1800.0,
        avg_turns_per_session=5.0,
        delegation_ratio=3.0,
        error_rate=0.10,
        sessions_change_pct=None,
        tools_change_pct=None,
        delegation_change_pct=None,
        error_change_pct=None,
    )

    tips = generate_tips(current, previous)

    # Should trigger declining_tool_diversity
    rule_ids = {tip.rule_id for tip in tips}
    assert "declining_tool_diversity" in rule_ids


def test_generate_tips_all_fields_present() -> None:
    """Test that generated tips have all required fields."""
    metrics = WeeklyMetrics(
        user_id="local",
        week_start=datetime(2024, 1, 1),
        session_count=10,
        total_duration_seconds=18000,
        total_turns=50,
        total_tool_calls=100,
        total_delegations=1,  # Low delegation - will trigger
        total_errors=10,
        unique_tools=8,
        tool_counts={"bash": 30},
        top_5_tools=["bash"],
        avg_session_duration=1800.0,
        avg_turns_per_session=5.0,
        delegation_ratio=0.1,  # Low
        error_rate=0.10,
        sessions_change_pct=None,
        tools_change_pct=None,
        delegation_change_pct=None,
        error_change_pct=None,
    )

    tips = generate_tips(metrics, None)

    assert len(tips) > 0

    for tip in tips:
        # Verify all required fields are present
        assert isinstance(tip, RuleTip)
        assert tip.rule_id
        assert tip.category
        assert tip.priority in ["high", "medium", "low"]
        assert tip.observation
        assert tip.recommendation
        assert tip.expected_benefit
        assert isinstance(tip.generated_at, datetime)
        assert isinstance(tip.based_on_week, datetime)


def test_rule_zero_tool_calls_no_crash() -> None:
    """Test rules handle zero tool calls without crashing."""
    metrics = WeeklyMetrics(
        user_id="local",
        week_start=datetime(2024, 1, 1),
        session_count=1,
        total_duration_seconds=100,
        total_turns=5,
        total_tool_calls=0,  # Zero tool calls
        total_delegations=0,
        total_errors=0,
        unique_tools=0,
        tool_counts={},
        top_5_tools=[],
        avg_session_duration=100.0,
        avg_turns_per_session=5.0,
        delegation_ratio=0.0,
        error_rate=0.0,
        sessions_change_pct=None,
        tools_change_pct=None,
        delegation_change_pct=None,
        error_change_pct=None,
    )

    # Should not crash
    tip_bash = rule_high_bash_usage(metrics)
    tip_error = rule_high_error_rate(metrics)

    assert tip_bash is None
    assert tip_error is None


def test_rule_zero_sessions_no_crash() -> None:
    """Test rules handle zero sessions without crashing."""
    metrics = WeeklyMetrics(
        user_id="local",
        week_start=datetime(2024, 1, 1),
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

    # Should not crash
    tips = generate_tips(metrics, None)
    assert tips == []


def test_tips_sorted_by_priority() -> None:
    """Test that tips are sorted by priority (high > medium > low)."""
    metrics = WeeklyMetrics(
        user_id="local",
        week_start=datetime(2024, 1, 1),
        session_count=10,
        total_duration_seconds=40000,
        total_turns=50,
        total_tool_calls=100,
        total_delegations=1,  # Low - HIGH priority
        total_errors=20,  # High - HIGH priority
        unique_tools=5,
        tool_counts={"bash": 40, "read_file": 30, "delegate": 1},  # High bash - MEDIUM
        top_5_tools=["bash", "read_file", "delegate"],
        avg_session_duration=4000.0,  # Long - MEDIUM priority
        avg_turns_per_session=5.0,
        delegation_ratio=0.1,  # Low
        error_rate=0.20,  # High
        sessions_change_pct=None,
        tools_change_pct=None,
        delegation_change_pct=None,
        error_change_pct=None,
    )

    tips = generate_tips(metrics, None)

    # Should have multiple tips
    assert len(tips) >= 3

    # First tips should be high priority
    high_priority_tips = [t for t in tips if t.priority == "high"]
    medium_priority_tips = [t for t in tips if t.priority == "medium"]

    # High priority should come before medium
    if high_priority_tips and medium_priority_tips:
        first_high_idx = tips.index(high_priority_tips[0])
        first_medium_idx = tips.index(medium_priority_tips[0])
        assert first_high_idx < first_medium_idx
