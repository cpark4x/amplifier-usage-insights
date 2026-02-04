"""Amplifier Usage Insights - V0.5 Validation Build."""

__version__ = "0.5.0"

from .insights import InsightsEngine, get_personal_insights
from .metrics import WeeklyMetrics, calculate_growth, calculate_weekly_metrics, get_week_start
from .parser import Session, SessionParser
from .storage import MetricsDB
from .tips import RuleTip, generate_tips

__all__ = [
    "SessionParser",
    "Session",
    "WeeklyMetrics",
    "MetricsDB",
    "RuleTip",
    "InsightsEngine",
    "get_personal_insights",
    "calculate_growth",
    "calculate_weekly_metrics",
    "generate_tips",
    "get_week_start",
]
