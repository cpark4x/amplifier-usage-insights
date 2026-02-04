"""SQLite storage for session metrics."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from .parser import Session

if TYPE_CHECKING:
    from .metrics import WeeklyMetrics


class MetricsDB:
    """Simple SQLite operations for V0.5."""

    def __init__(self, db_path: Path | str):
        """Initialize DB connection, create schema if needed."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Create database schema if it doesn't exist."""
        schema_file = Path(__file__).parent / "schema.sql"

        with open(schema_file) as f:
            schema_sql = f.read()

        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema_sql)
            conn.commit()

    def save_session(self, session: Session) -> None:
        """
        Insert or replace session in database.

        Inserts into:
        - sessions table
        - session_tools table
        """
        with sqlite3.connect(self.db_path) as conn:
            # Insert/replace session
            conn.execute(
                """
                INSERT OR REPLACE INTO sessions (
                    session_id, project_path, started_at, ended_at,
                    duration_seconds, turn_count, tool_call_count,
                    delegation_count, error_count, model_used, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.session_id,
                    session.project_path,
                    session.started_at.isoformat(),
                    session.ended_at.isoformat(),
                    session.duration_seconds,
                    session.turn_count,
                    session.tool_call_count,
                    session.delegation_count,
                    session.error_count,
                    session.model_used,
                    session.status,
                ),
            )

            # Delete old tool counts
            conn.execute(
                "DELETE FROM session_tools WHERE session_id = ?",
                (session.session_id,),
            )

            # Insert new tool counts
            for tool_name, count in session.tool_counts.items():
                conn.execute(
                    """
                    INSERT INTO session_tools (session_id, tool_name, call_count)
                    VALUES (?, ?, ?)
                    """,
                    (session.session_id, tool_name, count),
                )

            conn.commit()

    def get_session(self, session_id: str) -> Session | None:
        """Get a single session by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM sessions WHERE session_id = ?
                """,
                (session_id,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            # Get tool counts
            tool_cursor = conn.execute(
                """
                SELECT tool_name, call_count FROM session_tools
                WHERE session_id = ?
                """,
                (session_id,),
            )
            tool_counts = {row[0]: row[1] for row in tool_cursor.fetchall()}

            return Session(
                session_id=row["session_id"],
                project_path=row["project_path"],
                started_at=datetime.fromisoformat(row["started_at"]),
                ended_at=datetime.fromisoformat(row["ended_at"]),
                duration_seconds=row["duration_seconds"],
                turn_count=row["turn_count"],
                tool_call_count=row["tool_call_count"],
                delegation_count=row["delegation_count"],
                error_count=row["error_count"],
                tool_counts=tool_counts,
                model_used=row["model_used"],
                status=row["status"],
            )

    def get_all_sessions(self) -> list[Session]:
        """Get all sessions (for debugging)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT session_id FROM sessions")
            session_ids = [row[0] for row in cursor.fetchall()]

        sessions = []
        for session_id in session_ids:
            session = self.get_session(session_id)
            if session:
                sessions.append(session)

        return sessions

    def get_sessions_in_range(self, start_date: datetime, end_date: datetime) -> list[Session]:
        """Get sessions within a date range."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT session_id FROM sessions
                WHERE started_at >= ? AND started_at < ?
                ORDER BY started_at
                """,
                (start_date.isoformat(), end_date.isoformat()),
            )
            session_ids = [row[0] for row in cursor.fetchall()]

        sessions = []
        for session_id in session_ids:
            session = self.get_session(session_id)
            if session:
                sessions.append(session)

        return sessions

    def session_exists(self, session_id: str) -> bool:
        """Check if a session already exists in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM sessions WHERE session_id = ? LIMIT 1",
                (session_id,),
            )
            return cursor.fetchone() is not None

    def get_session_count(self) -> int:
        """Get total number of sessions in database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM sessions")
            result = cursor.fetchone()
            return result[0] if result else 0

    def get_tool_usage_summary(self) -> dict[str, int]:
        """Get aggregated tool usage across all sessions."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT tool_name, SUM(call_count) as total
                FROM session_tools
                GROUP BY tool_name
                ORDER BY total DESC
                """
            )
            return {row[0]: row[1] for row in cursor.fetchall()}

    def get_weekly_metrics(self, week_start: datetime) -> "WeeklyMetrics | None":
        """
        Get metrics for a specific week.

        Args:
            week_start: Monday 00:00:00 for the week

        Returns:
            WeeklyMetrics object or None if week not computed yet
        """
        # Import here to avoid circular dependency
        from .metrics import WeeklyMetrics

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM weekly_metrics
                WHERE user_id = ? AND week_start = ?
                """,
                ("local", week_start.isoformat()),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            # Parse tool_counts from JSON
            tool_counts = json.loads(row["top_5_tools"]) if row["top_5_tools"] else {}
            top_5_tools = list(tool_counts.keys())[:5] if isinstance(tool_counts, dict) else []

            return WeeklyMetrics(
                user_id=row["user_id"],
                week_start=datetime.fromisoformat(row["week_start"]),
                session_count=row["session_count"],
                total_duration_seconds=row["total_duration_seconds"],
                total_turns=row["total_turns"],
                total_tool_calls=row["total_tool_calls"],
                total_delegations=row["total_delegations"],
                total_errors=row["total_errors"],
                unique_tools=row["unique_tools"],
                tool_counts=tool_counts if isinstance(tool_counts, dict) else {},
                top_5_tools=top_5_tools,
                avg_session_duration=row["avg_session_duration"],
                avg_turns_per_session=row["avg_turns_per_session"],
                delegation_ratio=row["delegation_ratio"],
                error_rate=row["error_rate"],
                sessions_change_pct=row["sessions_change_pct"],
                tools_change_pct=row["tools_change_pct"],
                delegation_change_pct=row["delegation_change_pct"],
                error_change_pct=row["error_change_pct"],
            )

    def save_weekly_metrics(self, metrics: "WeeklyMetrics") -> None:
        """
        Save or update weekly metrics.

        Args:
            metrics: WeeklyMetrics object to persist
        """
        # Import here to avoid circular dependency
        import json

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO weekly_metrics (
                    user_id, week_start, session_count, total_duration_seconds,
                    total_turns, total_tool_calls, total_delegations, total_errors,
                    unique_tools, top_5_tools, avg_session_duration, avg_turns_per_session,
                    delegation_ratio, error_rate, sessions_change_pct,
                    tools_change_pct, delegation_change_pct, error_change_pct
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    metrics.user_id,
                    metrics.week_start.isoformat(),
                    metrics.session_count,
                    metrics.total_duration_seconds,
                    metrics.total_turns,
                    metrics.total_tool_calls,
                    metrics.total_delegations,
                    metrics.total_errors,
                    metrics.unique_tools,
                    json.dumps(metrics.tool_counts),
                    metrics.avg_session_duration,
                    metrics.avg_turns_per_session,
                    metrics.delegation_ratio,
                    metrics.error_rate,
                    metrics.sessions_change_pct,
                    metrics.tools_change_pct,
                    metrics.delegation_change_pct,
                    metrics.error_change_pct,
                ),
            )
            conn.commit()
