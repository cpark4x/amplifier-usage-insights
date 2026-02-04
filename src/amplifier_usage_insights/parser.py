"""Session parser for Amplifier session data."""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TypedDict


class EventsData(TypedDict):
    """Return type for _parse_events method."""

    tool_counts: dict[str, int]
    delegation_count: int
    error_count: int
    session_id: str | None


class TranscriptData(TypedDict):
    """Return type for _parse_transcript method."""

    turn_count: int
    started_at: datetime
    ended_at: datetime


@dataclass
class Session:
    """Minimal session data for V0.5."""

    # Identity
    session_id: str
    project_path: str

    # Timing
    started_at: datetime
    ended_at: datetime
    duration_seconds: int

    # Basic counts
    turn_count: int
    tool_call_count: int
    delegation_count: int
    error_count: int

    # Tool usage (simple dict)
    tool_counts: dict[str, int]  # {"bash": 12, "read_file": 8}

    # Metadata
    model_used: str
    status: str  # "completed", "abandoned"


class SessionParser:
    """Parse Amplifier session files into structured data."""

    def find_sessions(self, projects_dir: Path | None = None) -> list[Path]:
        """
        Find all session directories in ~/.amplifier/projects/

        Structure:
            ~/.amplifier/projects/
            ├── project-a/
            │   └── sessions/
            │       ├── session-id-1/
            │       └── session-id-2/
            └── project-b/
                └── sessions/
                    └── session-id-3/

        Returns: [session-id-1/, session-id-2/, session-id-3/]
        """
        if projects_dir is None:
            projects_dir = Path.home() / ".amplifier" / "projects"

        sessions: list[Path] = []

        if not projects_dir.exists():
            return sessions

        for project_dir in projects_dir.iterdir():
            if not project_dir.is_dir():
                continue

            sessions_dir = project_dir / "sessions"
            if sessions_dir.exists():
                for session_dir in sessions_dir.iterdir():
                    if session_dir.is_dir():
                        sessions.append(session_dir)

        return sessions

    def parse_session(self, session_dir: Path) -> Session:
        """
        Parse a single Amplifier session directory.

        Input: Path to session dir containing:
            - events.jsonl (tool calls, errors)
            - transcript.jsonl (turns)
            - metadata.json (session info)

        Output: Session object with all metrics

        Raises:
            FileNotFoundError: If required session files are missing
            json.JSONDecodeError: If files are corrupted
            ValueError: If required fields are missing
        """
        events_file = session_dir / "events.jsonl"
        transcript_file = session_dir / "transcript.jsonl"
        metadata_file = session_dir / "metadata.json"

        # Parse events for tool usage
        events_data = self._parse_events(events_file)

        # Parse transcript for timing and turns
        transcript_data = self._parse_transcript(transcript_file)

        # Parse metadata for project info
        metadata_data = self._parse_metadata(metadata_file)

        # Calculate duration
        duration_seconds = int(
            (transcript_data["ended_at"] - transcript_data["started_at"]).total_seconds()
        )

        return Session(
            session_id=events_data["session_id"] or session_dir.name,
            project_path=metadata_data.get("project_path", str(session_dir.parent.parent)),
            started_at=transcript_data["started_at"],
            ended_at=transcript_data["ended_at"],
            duration_seconds=duration_seconds,
            turn_count=transcript_data["turn_count"],
            tool_call_count=sum(events_data["tool_counts"].values()),
            delegation_count=events_data["delegation_count"],
            error_count=events_data["error_count"],
            tool_counts=events_data["tool_counts"],
            model_used=metadata_data.get("model_used", "unknown"),
            status=metadata_data.get("status", "completed"),
        )

    def _parse_events(self, events_file: Path) -> EventsData:
        """
        Parse events.jsonl to extract tool usage.

        Returns:
            {
                "tool_counts": {"bash": 12, "delegate": 8},
                "delegation_count": 8,
                "error_count": 3,
                "session_id": "abc123"
            }
        """
        tool_counts: dict[str, int] = {}
        delegation_count = 0
        error_count = 0
        session_id: str | None = None

        if not events_file.exists():
            return EventsData(
                tool_counts={},
                delegation_count=0,
                error_count=0,
                session_id=None,
            )

        with open(events_file) as f:
            for line in f:
                if not line.strip():
                    continue

                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Get session ID from first event
                if session_id is None and "session_id" in event:
                    session_id = event["session_id"]

                # Count tool calls (from tool:pre events)
                if event.get("event") == "tool:pre":
                    tool_name = event.get("data", {}).get("tool_name", "unknown")
                    tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1

                    # Delegation is task tool + agent parameter
                    if tool_name == "task":
                        tool_input = event.get("data", {}).get("tool_input", {})
                        if isinstance(tool_input, dict) and "agent" in tool_input:
                            delegation_count += 1

                # Count errors
                if event.get("type") == "error" or event.get("status") == "error":
                    error_count += 1

        return EventsData(
            tool_counts=tool_counts,
            delegation_count=delegation_count,
            error_count=error_count,
            session_id=session_id,
        )

    def _parse_transcript(self, transcript_file: Path) -> TranscriptData:
        """
        Parse transcript.jsonl to extract timing and turn count.

        Returns:
            {
                "turn_count": 12,
                "started_at": datetime(...),
                "ended_at": datetime(...)
            }
        """
        turns = 0
        started_at: datetime | None = None
        ended_at: datetime | None = None

        if not transcript_file.exists():
            # Fallback to current time if no transcript
            now = datetime.now()
            return TranscriptData(turn_count=0, started_at=now, ended_at=now)

        with open(transcript_file) as f:
            for line in f:
                if not line.strip():
                    continue

                try:
                    message = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Parse timestamp
                timestamp_str = message.get("timestamp", "")
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    except ValueError:
                        continue

                    if started_at is None:
                        started_at = timestamp
                    ended_at = timestamp

                # Count user turns
                if message.get("role") == "user":
                    turns += 1

        # Fallback if no valid timestamps
        if started_at is None or ended_at is None:
            now = datetime.now()
            started_at = started_at or now
            ended_at = ended_at or now

        return TranscriptData(turn_count=turns, started_at=started_at, ended_at=ended_at)

    def _parse_metadata(self, metadata_file: Path) -> dict[str, str]:
        """
        Parse metadata.json to extract project info.

        Returns:
            {
                "project_path": "/path/to/project",
                "model_used": "claude-3-5-sonnet-20241022",
                "status": "completed"
            }
        """
        if not metadata_file.exists():
            return {}

        try:
            with open(metadata_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
