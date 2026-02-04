-- V0.5 Schema (Minimal - 3 tables)

-- Raw sessions (parsed from Amplifier)
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    project_path TEXT NOT NULL,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP NOT NULL,
    duration_seconds INTEGER NOT NULL,
    turn_count INTEGER NOT NULL,
    tool_call_count INTEGER NOT NULL,
    delegation_count INTEGER NOT NULL,
    error_count INTEGER NOT NULL,
    model_used TEXT,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tool usage per session
CREATE TABLE IF NOT EXISTS session_tools (
    session_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    call_count INTEGER NOT NULL,
    PRIMARY KEY (session_id, tool_name),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- Weekly aggregations
CREATE TABLE IF NOT EXISTS weekly_metrics (
    user_id TEXT NOT NULL,
    week_start TIMESTAMP NOT NULL,
    session_count INTEGER NOT NULL,
    total_duration_seconds INTEGER NOT NULL,
    total_turns INTEGER NOT NULL,
    total_tool_calls INTEGER NOT NULL,
    total_delegations INTEGER NOT NULL,
    total_errors INTEGER NOT NULL,
    unique_tools INTEGER NOT NULL,
    top_5_tools TEXT NOT NULL,  -- JSON dict of tool counts
    avg_session_duration REAL NOT NULL,
    avg_turns_per_session REAL NOT NULL,
    delegation_ratio REAL NOT NULL,
    error_rate REAL NOT NULL,
    sessions_change_pct REAL,
    tools_change_pct REAL,
    delegation_change_pct REAL,
    error_change_pct REAL,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, week_start)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_sessions_started_at ON sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_weekly_metrics_week ON weekly_metrics(week_start);
