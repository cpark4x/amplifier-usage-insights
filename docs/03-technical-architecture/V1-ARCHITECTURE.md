# V1 Technical Architecture: Personal Insights

**Owner:** Chris Park  
**Contributors:** Chris Park (with AI)

**Last Updated:** 2026-02-03

---

## Summary

This document defines the complete technical architecture for Amplifier Usage Insights V1 (Personal Insights). It covers system components, data models, technology choices, integration patterns, and implementation strategy for building a privacy-first analytics system that helps individuals master AI collaboration.

**Key Architectural Decisions:**
- **Local-first storage** (SQLite) - Privacy by design, no server required for V1
- **Incremental computation** - Process sessions as they complete, not batch
- **Conversational-first interface** - Amplifier tool is primary, dashboard is secondary
- **Simple metrics first** - Start with transparent, explainable calculations
- **Python + Vue.js** - Leverage Amplifier ecosystem + modern web tech

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Data Models](#2-data-models)
3. [Technology Stack](#3-technology-stack)
4. [Module Structure](#4-module-structure)
5. [Integration Approach](#5-integration-approach)
6. [Deployment Strategy](#6-deployment-strategy)
7. [Development Phases](#7-development-phases)
8. [Testing Strategy](#8-testing-strategy)
9. [Critical Design Decisions](#9-critical-design-decisions)
10. [Future Considerations](#10-future-considerations)

---

## 1. System Architecture

### High-Level Component View

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                          │
├──────────────────────────────┬──────────────────────────────────┤
│   Conversational Interface   │      Web Dashboard (Vue.js)      │
│   (Amplifier Tool/Agent)     │   (Static Site + API Backend)    │
└──────────────┬───────────────┴──────────────────┬───────────────┘
               │                                   │
               └────────────┬──────────────────────┘
                            ▼
                 ┌──────────────────────┐
                 │    Insights Engine   │
                 │   (Query Interface)  │
                 └──────────┬───────────┘
                            ▼
         ┌──────────────────────────────────────┐
         │        Analytics Core                │
         ├──────────────────────────────────────┤
         │  • Metrics Calculator                │
         │  • Growth Analyzer                   │
         │  • Pattern Detector                  │
         │  • Tips Generator (LLM-based)        │
         └──────────┬───────────────────────────┘
                    ▼
         ┌──────────────────────────┐
         │   Computed Metrics DB    │
         │   (SQLite - Local)       │
         └──────────┬─────────────────┘
                    ▼
         ┌──────────────────────────┐
         │  Session Data Ingestion  │
         ├──────────────────────────┤
         │  • Session Parser        │
         │  • Event Processor       │
         │  • Incremental Updater   │
         └──────────┬─────────────────┘
                    ▼
         ┌──────────────────────────┐
         │   Amplifier Sessions     │
         │  ~/.amplifier/projects/  │
         │  • events.jsonl          │
         │  • transcript.jsonl      │
         │  • metadata.json         │
         └──────────────────────────┘
```

### Data Flow

```
1. Session Ends
   ↓
2. File Watcher detects new/updated session files
   ↓
3. Session Parser reads events.jsonl, transcript.jsonl, metadata.json
   ↓
4. Event Processor extracts metrics (tools used, duration, turns, errors)
   ↓
5. Incremental Updater updates computed metrics (aggregations, trends)
   ↓
6. Metrics stored in local SQLite database
   ↓
7a. User asks "How am I doing?" → Conversational Interface queries Insights Engine
7b. User opens dashboard → Web app queries Insights Engine
   ↓
8. Insights Engine returns formatted results
   ↓
9. Tips Generator (LLM) creates actionable suggestions based on patterns
```

### Component Responsibilities

| Component | Responsibility | Input | Output |
|-----------|---------------|-------|--------|
| **Session Parser** | Parse Amplifier session files | events.jsonl, transcript.jsonl, metadata.json | Structured session data |
| **Event Processor** | Extract metrics from parsed data | Structured session data | Raw metrics |
| **Incremental Updater** | Update aggregations incrementally | Raw metrics | Updated computed metrics |
| **Metrics Calculator** | Compute derived metrics | Raw + computed metrics | Calculated insights |
| **Growth Analyzer** | Detect trends and changes | Time-series metrics | Growth indicators |
| **Pattern Detector** | Identify usage patterns | Session history | Pattern insights |
| **Tips Generator** | Create actionable suggestions | Patterns + metrics | Actionable tips |
| **Insights Engine** | Query interface for all insights | User queries | Formatted results |
| **Conversational Interface** | Natural language queries | User questions | Conversational responses |
| **Web Dashboard** | Visual exploration | Dashboard requests | Charts + tables |

---

## 2. Data Models

### Core Entities

#### **Session** (Raw Data - Parsed from Amplifier)

```python
@dataclass
class Session:
    """Represents a single Amplifier session."""
    
    # Identity
    session_id: str              # From metadata
    project_path: str            # Project directory
    
    # Timing
    started_at: datetime
    ended_at: datetime
    duration_seconds: int
    
    # Basic metrics
    turn_count: int
    model_used: str              # Primary model
    status: str                  # completed, abandoned, error
    
    # Derived from events.jsonl
    tools_used: list[str]        # ["bash", "read_file", "delegate"]
    tool_call_count: int
    tool_call_distribution: dict[str, int]  # {"bash": 12, "read_file": 8}
    
    file_paths_touched: list[str]
    error_count: int
    delegation_count: int
    delegated_agents: list[str]  # Which agents were used
    
    # Parsed from transcript
    user_message_count: int
    assistant_message_count: int
    total_tokens: Optional[int]  # If available
    
    # Privacy: We do NOT store actual content, prompts, or code
```

#### **SessionMetrics** (Computed - Stored in DB)

```python
@dataclass
class SessionMetrics:
    """Computed metrics for a single session."""
    
    session_id: str
    computed_at: datetime
    
    # Complexity indicators
    unique_tools_used: int
    tool_diversity_score: float  # Shannon entropy of tool usage
    files_touched: int
    repos_accessed: int
    
    # Effectiveness indicators
    time_per_turn: float         # duration / turn_count
    tool_calls_per_turn: float
    error_rate: float            # errors / total_actions
    delegation_ratio: float      # delegations / total_actions
    
    # Task classification (high-level, no sensitive content)
    primary_task_category: str   # "coding", "debugging", "research", etc.
    complexity_estimate: str     # "low", "medium", "high"
    
    # Session outcome
    completion_status: str       # "completed", "abandoned", "error_terminated"
```

#### **UserMetrics** (Aggregated - Time Windows)

```python
@dataclass
class UserMetrics:
    """Aggregated metrics for a user over a time period."""
    
    user_id: str                 # Default: "local" (for V1)
    time_period: str             # "week_2026_05", "month_2026_02"
    period_start: datetime
    period_end: datetime
    
    # Volume metrics
    session_count: int
    total_duration_seconds: int
    total_turns: int
    total_tool_calls: int
    
    # Tool sophistication
    unique_tools_used: int
    avg_tool_diversity: float
    tool_usage_distribution: dict[str, int]  # {"bash": 45, "grep": 12}
    most_used_tools: list[str]   # Top 5
    
    # Effectiveness
    avg_time_per_turn: float
    avg_error_rate: float
    avg_delegation_ratio: float
    avg_session_duration: float
    
    # Growth indicators (compare to previous period)
    sessions_vs_prev: float      # +15% or -10%
    tool_diversity_vs_prev: float
    effectiveness_vs_prev: float
    error_rate_vs_prev: float
    
    # Calculated at query time, not stored
    growth_direction: str        # "improving", "declining", "stable"
```

#### **GrowthMetric** (Trends Over Time)

```python
@dataclass
class GrowthMetric:
    """Trend analysis for a specific metric over time."""
    
    user_id: str
    metric_name: str             # "tool_diversity", "error_rate", etc.
    
    # Time series data
    time_series: list[tuple[datetime, float]]
    
    # Trend analysis
    trend_direction: str         # "improving", "declining", "stable"
    trend_strength: float        # -1.0 to +1.0 (correlation coefficient)
    recent_change: float         # % change in last period vs previous
    
    # Statistical
    mean: float
    std_dev: float
    min_value: float
    max_value: float
```

#### **ActionableTip** (Generated Insights)

```python
@dataclass
class ActionableTip:
    """An actionable suggestion based on usage patterns."""
    
    user_id: str
    generated_at: datetime
    category: str                # "tool_usage", "delegation", "error_handling"
    priority: str                # "high", "medium", "low"
    
    # The tip
    observation: str             # "You use bash 3x more than specialized tools"
    recommendation: str          # "Try using grep for file searches instead of bash"
    expected_benefit: str        # "30% faster file operations"
    
    # Context
    based_on_sessions: list[str] # Session IDs that triggered this tip
    metric_values: dict[str, float]  # Relevant metrics
    
    # Lifecycle
    shown_to_user: bool
    dismissed: bool
    marked_helpful: Optional[bool]
```

---

## 3. Technology Stack

### Core Application (Python)

```toml
[project]
name = "amplifier-usage-insights"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    # Data Processing
    "polars>=0.20.0",           # Fast dataframe operations
    "python-dateutil>=2.8.0",   # Date parsing
    
    # Amplifier Integration
    "amplifier-core",           # For session file formats
    
    # LLM for Tips Generation
    "litellm>=1.0.0",           # Universal LLM interface
    
    # Web API
    "fastapi>=0.109.0",         # API framework
    "uvicorn[standard]>=0.27.0", # ASGI server
    "pydantic>=2.5.0",          # Data validation
    
    # CLI
    "typer>=0.9.0",             # CLI framework
    "rich>=13.0.0",             # Terminal output
    
    # File watching
    "watchdog>=4.0.0",          # Monitor session directory
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.2.0",
    "pyright>=1.1.0",
]
```

**Key Library Choices:**

| Library | Purpose | Why This Choice |
|---------|---------|-----------------|
| **Polars** | Data processing | 10-100x faster than pandas, better for time-series |
| **SQLite** | Storage | Built-in, no setup, privacy-first, scales to millions of rows |
| **LiteLLM** | LLM access | Works with any provider, uses user's Amplifier config |
| **FastAPI** | API backend | Fast, modern, automatic OpenAPI docs, async support |
| **Typer** | CLI | Beautiful CLI with auto-completion, minimal boilerplate |
| **Watchdog** | File monitoring | Cross-platform file system events |

### Web Dashboard (Vue.js)

```json
{
  "name": "amplifier-usage-insights-web",
  "version": "0.1.0",
  "dependencies": {
    "vue": "^3.4.0",
    "vite": "^5.0.0",
    "pinia": "^2.1.0",
    "vue-router": "^4.2.0",
    "chart.js": "^4.4.0",
    "vue-chartjs": "^5.3.0",
    "tailwindcss": "^3.4.0",
    "axios": "^1.6.0",
    "date-fns": "^3.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

**Key Library Choices:**

| Library | Purpose | Why This Choice |
|---------|---------|-----------------|
| **Vue 3** | Framework | Reactive, lightweight, easier than React for solo dev |
| **Vite** | Build tool | Lightning-fast dev server and builds |
| **Pinia** | State management | Official Vue store, simpler than Vuex |
| **Chart.js** | Visualization | Simple, beautiful charts without D3 complexity |
| **Tailwind CSS** | Styling | Utility-first, rapid UI development |

### Storage Schema (SQLite)

```sql
-- ~/.amplifier-usage-insights/metrics.db

-- Raw sessions (parsed from Amplifier)
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    project_path TEXT NOT NULL,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP NOT NULL,
    duration_seconds INTEGER NOT NULL,
    turn_count INTEGER NOT NULL,
    model_used TEXT,
    status TEXT NOT NULL,
    tool_call_count INTEGER NOT NULL,
    error_count INTEGER NOT NULL,
    delegation_count INTEGER NOT NULL,
    user_message_count INTEGER NOT NULL,
    assistant_message_count INTEGER NOT NULL,
    total_tokens INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Session metrics (computed)
CREATE TABLE session_metrics (
    session_id TEXT PRIMARY KEY,
    computed_at TIMESTAMP NOT NULL,
    unique_tools_used INTEGER NOT NULL,
    tool_diversity_score REAL NOT NULL,
    files_touched INTEGER NOT NULL,
    repos_accessed INTEGER NOT NULL,
    time_per_turn REAL NOT NULL,
    tool_calls_per_turn REAL NOT NULL,
    error_rate REAL NOT NULL,
    delegation_ratio REAL NOT NULL,
    primary_task_category TEXT,
    complexity_estimate TEXT,
    completion_status TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- Tool usage per session
CREATE TABLE session_tools (
    session_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    call_count INTEGER NOT NULL,
    PRIMARY KEY (session_id, tool_name),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- Aggregated metrics by time period
CREATE TABLE user_metrics (
    user_id TEXT NOT NULL,
    time_period TEXT NOT NULL,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    session_count INTEGER NOT NULL,
    total_duration_seconds INTEGER NOT NULL,
    total_turns INTEGER NOT NULL,
    total_tool_calls INTEGER NOT NULL,
    unique_tools_used INTEGER NOT NULL,
    avg_tool_diversity REAL NOT NULL,
    avg_time_per_turn REAL NOT NULL,
    avg_error_rate REAL NOT NULL,
    avg_delegation_ratio REAL NOT NULL,
    sessions_vs_prev REAL,
    tool_diversity_vs_prev REAL,
    effectiveness_vs_prev REAL,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, time_period)
);

-- Tool usage by time period
CREATE TABLE period_tools (
    user_id TEXT NOT NULL,
    time_period TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    call_count INTEGER NOT NULL,
    PRIMARY KEY (user_id, time_period, tool_name)
);

-- Actionable tips
CREATE TABLE actionable_tips (
    tip_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    generated_at TIMESTAMP NOT NULL,
    category TEXT NOT NULL,
    priority TEXT NOT NULL,
    observation TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    expected_benefit TEXT NOT NULL,
    shown_to_user BOOLEAN DEFAULT FALSE,
    dismissed BOOLEAN DEFAULT FALSE,
    marked_helpful BOOLEAN
);

-- Indexes for common queries
CREATE INDEX idx_sessions_started_at ON sessions(started_at);
CREATE INDEX idx_sessions_project_path ON sessions(project_path);
CREATE INDEX idx_user_metrics_period ON user_metrics(user_id, period_start);
CREATE INDEX idx_tips_user_shown ON actionable_tips(user_id, shown_to_user);
```

---

## 4. Module Structure

### Directory Layout

```
amplifier-usage-insights/
├── pyproject.toml                 # Python package config
├── README.md
├── docs/                          # Existing vision/requirements
│   ├── 01-vision/
│   ├── 02-requirements/
│   └── 03-technical-architecture/
│       └── V1-ARCHITECTURE.md     # This document
│
├── src/
│   └── amplifier_usage_insights/
│       ├── __init__.py
│       ├── __main__.py            # Entry point for CLI
│       │
│       ├── core/                  # Analytics Core
│       │   ├── __init__.py
│       │   ├── models.py          # Data models (Session, Metrics, etc.)
│       │   ├── metrics.py         # Metrics calculation logic
│       │   ├── growth.py          # Growth analysis and trends
│       │   ├── patterns.py        # Pattern detection
│       │   └── tips.py            # Tips generation (LLM-based)
│       │
│       ├── ingestion/             # Session Data Ingestion
│       │   ├── __init__.py
│       │   ├── parser.py          # Parse Amplifier session files
│       │   ├── processor.py       # Extract metrics from parsed data
│       │   ├── watcher.py         # File watcher for new sessions
│       │   └── updater.py         # Incremental metric updates
│       │
│       ├── storage/               # Database Layer
│       │   ├── __init__.py
│       │   ├── schema.sql         # SQLite schema
│       │   ├── db.py              # Database operations
│       │   └── migrations/        # Schema migrations
│       │       └── 001_initial.sql
│       │
│       ├── insights/              # Insights Engine
│       │   ├── __init__.py
│       │   ├── engine.py          # Query interface
│       │   ├── formatters.py      # Format results for different interfaces
│       │   └── queries.py         # Common query patterns
│       │
│       ├── interfaces/            # User Interfaces
│       │   ├── __init__.py
│       │   ├── api.py             # FastAPI backend
│       │   ├── conversational.py  # Conversational tool/agent
│       │   └── cli.py             # CLI commands (typer)
│       │
│       └── utils/
│           ├── __init__.py
│           ├── config.py          # Configuration management
│           └── logging.py         # Logging setup
│
├── bundles/                       # Amplifier Bundle
│   └── usage-insights/
│       ├── bundle.yaml            # Bundle definition
│       ├── tools.yaml             # Tool definitions
│       └── contexts/
│           └── instructions.md    # How to use the insights tool
│
├── web/                           # Vue.js Dashboard
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── stores/                # Pinia stores
│   │   │   ├── metrics.js
│   │   │   └── sessions.js
│   │   ├── components/            # Reusable components
│   │   │   ├── MetricCard.vue
│   │   │   ├── TrendChart.vue
│   │   │   ├── TipsList.vue
│   │   │   └── SessionTable.vue
│   │   ├── views/                 # Page views
│   │   │   ├── Dashboard.vue
│   │   │   ├── GrowthView.vue
│   │   │   ├── SessionsView.vue
│   │   │   └── TipsView.vue
│   │   └── services/
│   │       └── api.js             # API client
│   └── public/
│
└── tests/
    ├── unit/
    │   ├── test_parser.py
    │   ├── test_metrics.py
    │   └── test_growth.py
    ├── integration/
    │   ├── test_ingestion_pipeline.py
    │   └── test_insights_engine.py
    └── fixtures/
        └── sample_sessions/       # Mock Amplifier sessions
```

---

## 5. Integration Approach

### Conversational Interface (Primary)

**Amplifier Tool** - Natural language queries within any Amplifier session

```yaml
# bundles/usage-insights/tools.yaml
tools:
  - name: get_personal_insights
    description: |
      Get insights about your AI collaboration effectiveness.
      
      Ask questions like:
      - "How am I doing this week?"
      - "Show my growth over the last month"
      - "What tools do I use most?"
      - "Give me tips to improve"
      - "Compare this week to last week"
    
    parameters:
      query:
        type: string
        description: Natural language question about usage patterns
        required: true
      
      time_range:
        type: string
        enum: ["week", "month", "90days", "all"]
        default: "week"
        description: Time period for analysis
    
    returns:
      type: object
      properties:
        summary:
          type: string
          description: High-level answer to the query
        
        metrics:
          type: object
          description: Key metrics relevant to the query
        
        tips:
          type: array
          items: {type: string}
          description: Actionable suggestions
        
        growth_indicators:
          type: object
          description: Improvement trends
        
        details_url:
          type: string
          description: Link to dashboard for deep dive
```

**Usage Example:**

```
User: "How's my AI usage this week?"

Assistant (via tool): {
  "summary": "You're showing strong growth! 🚀",
  "metrics": {
    "sessions": {
      "count": 12,
      "vs_last_week": "+50%"
    },
    "tool_sophistication": {
      "unique_tools": 8,
      "diversity_score": 2.1,
      "vs_last_week": "+15%"
    },
    "effectiveness": {
      "avg_time_per_turn": "45s",
      "vs_last_week": "-10% (faster)"
    }
  },
  "tips": [
    {
      "priority": "high",
      "observation": "You use bash 3x more than specialized tools",
      "recommendation": "Try using grep for file searches instead of 'bash cat file | bash grep'",
      "expected_benefit": "30% faster file operations"
    }
  ],
  "growth_indicators": {
    "overall_trend": "improving",
    "weeks_of_improvement": 3,
    "strongest_area": "delegation patterns"
  },
  "details_url": "http://localhost:8080/dashboard"
}

Assistant responds:
"You're showing strong growth this week! 🚀

**This Week vs Last Week:**
- 12 sessions (+50% from 8 last week)
- Tool sophistication up 15% (using 8 different tools effectively)
- 10% faster per turn (45s avg vs 50s last week)

**Growth Area: Tool Usage**
I notice you're using bash 3x more than specialized tools. Try using `grep` for file searches instead of `bash cat | grep` chains - you could see 30% faster file operations.

Want to see your full dashboard with charts and details? [Open Dashboard](http://localhost:8080/dashboard)"
```

**Implementation:**

```python
# src/amplifier_usage_insights/interfaces/conversational.py

from amplifier_usage_insights.insights.engine import InsightsEngine
from amplifier_usage_insights.insights.formatters import ConversationalFormatter

async def get_personal_insights(query: str, time_range: str = "week") -> dict:
    """Tool implementation for conversational interface."""
    
    engine = InsightsEngine()
    formatter = ConversationalFormatter()
    
    # Parse natural language query into structured query
    structured_query = engine.parse_query(query, time_range)
    
    # Execute query
    results = await engine.execute(structured_query)
    
    # Format for conversational response
    response = formatter.format(results)
    
    return response
```

---

### Web Dashboard (Secondary)

**Static Vue.js SPA** - Visual exploration and deep analysis

**Key Views:**

1. **Dashboard (Home)**
   - Summary cards: Sessions this week, growth %, top tools
   - Growth trend chart (last 30 days)
   - Recent actionable tips
   - Quick stats: Error rate, delegation ratio, avg session time

2. **Growth View**
   - Time-series charts for key metrics
   - Week-over-week comparison tables
   - Growth indicators by category
   - Historical performance

3. **Sessions View**
   - Table of all sessions with filters (date, project, duration)
   - Session details drill-down
   - Tool usage per session
   - Search and export

4. **Tips View**
   - All actionable tips (prioritized)
   - Filter by category
   - Mark as helpful/dismiss
   - Track which tips were acted on

**API Endpoints:**

```python
# src/amplifier_usage_insights/interfaces/api.py

from fastapi import FastAPI, Query
from datetime import datetime, timedelta

app = FastAPI(title="Amplifier Usage Insights API")

@app.get("/api/v1/metrics/summary")
async def get_summary(
    time_range: str = Query("week", enum=["week", "month", "90days", "all"])
):
    """Get summary metrics for dashboard."""
    pass

@app.get("/api/v1/metrics/growth")
async def get_growth(
    metric: str = Query(...),
    start_date: datetime = None,
    end_date: datetime = None
):
    """Get time-series data for a specific metric."""
    pass

@app.get("/api/v1/sessions")
async def list_sessions(
    start_date: datetime = None,
    end_date: datetime = None,
    project_path: str = None,
    limit: int = 50,
    offset: int = 0
):
    """List sessions with pagination and filters."""
    pass

@app.get("/api/v1/sessions/{session_id}")
async def get_session(session_id: str):
    """Get detailed metrics for a single session."""
    pass

@app.get("/api/v1/tips")
async def get_tips(
    category: str = None,
    priority: str = None,
    shown: bool = None
):
    """Get actionable tips."""
    pass

@app.post("/api/v1/tips/{tip_id}/feedback")
async def tip_feedback(tip_id: str, helpful: bool):
    """Mark a tip as helpful or not."""
    pass
```

---

## 6. Deployment Strategy

### V1.0 Deployment (Local-First)

**Installation:**

```bash
# Install Python package
pip install amplifier-usage-insights

# Initialize (creates DB, starts file watcher)
amplifier-insights init

# Start background service (watches for new sessions)
amplifier-insights start

# Open dashboard
amplifier-insights dashboard
```

**Components:**

1. **Background Service** (watchdog)
   - Monitors `~/.amplifier/projects/` for new/updated sessions
   - Processes sessions incrementally
   - Updates metrics in real-time
   - Runs as systemd service (Linux) or launchd (macOS)

2. **API Server** (FastAPI)
   - Runs on `localhost:8080` (configurable)
   - Serves dashboard + API endpoints
   - Auto-starts with background service

3. **Web Dashboard** (Vue.js)
   - Static files served by FastAPI
   - Communicates with API via localhost

**File Locations:**

```
~/.amplifier-usage-insights/
├── metrics.db              # SQLite database
├── config.yaml             # User configuration
└── logs/
    └── insights.log        # Service logs
```

### Configuration

```yaml
# ~/.amplifier-usage-insights/config.yaml

# Data sources
amplifier:
  session_dirs:
    - ~/.amplifier/projects/
    - ~/custom/sessions/

# Processing
processing:
  watch_enabled: true
  batch_size: 10
  incremental_update: true

# Privacy
privacy:
  store_content: false       # Never store prompts/code
  redact_file_paths: true    # Store only filenames, not full paths
  retention_days: 365        # Delete data older than 1 year

# API
api:
  host: localhost
  port: 8080
  cors_enabled: false        # Disable CORS for local-only

# Tips generation
tips:
  llm_provider: litellm      # Use user's Amplifier LLM config
  generation_frequency: daily
  max_tips_per_day: 5
```

### Security Considerations

**V1 is local-only:**
- No data leaves the machine
- API bound to localhost only
- No authentication needed (single user)
- SQLite database with user-only permissions

---

## 7. Development Phases

### Phase 0: Foundation (Week 1-2)

**Goal:** Set up project structure, basic ingestion pipeline

**Deliverables:**
- ✅ Project structure created
- ✅ Python package setup (pyproject.toml)
- ✅ Database schema (SQLite)
- ✅ Session parser (reads events.jsonl, transcript.jsonl, metadata.json)
- ✅ Basic CLI (`amplifier-insights init`, `amplifier-insights parse <session>`)

**Success Criteria:**
- Can parse an Amplifier session and extract basic metrics
- Metrics stored in SQLite
- No errors on sample sessions

---

### Phase 1: Core Analytics (Week 3-4)

**Goal:** Implement metrics calculation and storage

**Deliverables:**
- ✅ Metrics calculator (session-level metrics)
- ✅ Aggregation logic (user metrics by time period)
- ✅ Incremental updater (process new sessions)
- ✅ File watcher (detect new sessions automatically)
- ✅ CLI commands: `amplifier-insights status`, `amplifier-insights metrics`

**Success Criteria:**
- File watcher detects new sessions and processes them
- Metrics update incrementally (no full recompute)
- Can query metrics via CLI
- Performance: Process 100 sessions in <10 seconds

---

### Phase 2: Conversational Interface (Week 5-6)

**Goal:** Enable natural language queries within Amplifier

**Deliverables:**
- ✅ Insights Engine (query parser + executor)
- ✅ Conversational formatter (human-readable responses)
- ✅ Amplifier bundle (`usage-insights`)
- ✅ Tool definition (`get_personal_insights`)
- ✅ Growth analyzer (trend detection)

**Success Criteria:**
- Can ask "How am I doing?" in Amplifier and get meaningful response
- Growth comparisons work (this week vs last week)
- Response time <2 seconds for typical queries
- User validation: 3+ users try it and find it valuable

---

### Phase 3: Tips Generation (Week 7)

**Goal:** Generate actionable improvement suggestions

**Deliverables:**
- ✅ Pattern detector (identify usage patterns)
- ✅ Tips generator (LLM-based suggestions)
- ✅ Tip storage and lifecycle (shown, dismissed, helpful)
- ✅ Integration with conversational interface

**Success Criteria:**
- Generates 3-5 relevant tips per week
- Tips are actionable (not generic advice)
- Users can provide feedback (helpful/not helpful)
- 60%+ of tips marked helpful by users

---

### Phase 4: Web Dashboard (Week 8-10)

**Goal:** Visual exploration and deep analysis

**Deliverables:**
- ✅ FastAPI backend (API endpoints)
- ✅ Vue.js frontend (4 main views)
- ✅ Chart components (Chart.js integration)
- ✅ Responsive design (works on laptop + tablet)
- ✅ CLI command: `amplifier-insights dashboard`

**Success Criteria:**
- Dashboard loads in <2 seconds
- All charts render correctly
- Can drill down into individual sessions
- Users prefer dashboard for deep exploration

---

### Phase 5: Polish & Launch (Week 11-12)

**Goal:** Production-ready V1.0

**Deliverables:**
- ✅ Comprehensive tests (80%+ coverage)
- ✅ Documentation (installation, usage, troubleshooting)
- ✅ Error handling and logging
- ✅ Performance optimization
- ✅ Package published (PyPI)
- ✅ Launch blog post + demo video

**Success Criteria:**
- Passes all tests
- No critical bugs in alpha testing
- Installation works on macOS + Linux
- 10+ alpha users providing feedback
- Positive reception from early users

---

## 8. Testing Strategy

### Unit Tests

**Coverage Target:** 80%+

**Key Areas:**
- Session parser (various event types, edge cases)
- Metrics calculator (correct math, edge cases like 0 sessions)
- Growth analyzer (trend detection accuracy)
- Pattern detector (pattern identification)
- Formatters (output correctness)

**Example:**

```python
# tests/unit/test_metrics.py

def test_tool_diversity_score():
    """Test Shannon entropy calculation for tool usage."""
    session = Session(
        tool_call_distribution={"bash": 10, "read_file": 5, "grep": 5}
    )
    metrics = calculate_session_metrics(session)
    
    # Shannon entropy for this distribution
    expected_diversity = 1.055  # Calculated manually
    assert abs(metrics.tool_diversity_score - expected_diversity) < 0.01

def test_growth_comparison_with_no_previous_period():
    """Handle case where there's no previous period to compare."""
    user_metrics = UserMetrics(...)
    growth = calculate_growth(user_metrics, previous=None)
    
    assert growth.sessions_vs_prev is None
    assert growth.trend_direction == "stable"
```

---

### Integration Tests

**Scenarios:**
1. **End-to-End Ingestion**
   - Place sample session in watch directory
   - Verify it's parsed, processed, and stored
   - Query metrics and verify correctness

2. **Incremental Update**
   - Process 10 sessions
   - Add 1 new session
   - Verify only new session is processed

3. **API Endpoints**
   - Test all REST endpoints
   - Verify response formats
   - Test error cases (invalid session ID, etc.)

---

### Fixture Data

**Mock Amplifier Sessions:**

Create realistic fixtures in `tests/fixtures/sample_sessions/`:

- `simple_session/` - Basic session with a few tool calls
- `complex_session/` - Large session with many tools and delegations
- `error_session/` - Session with errors and retries
- `delegation_heavy/` - Multiple agent delegations
- `long_session/` - High turn count, long duration

---

### Performance Tests

**Benchmarks:**

- Parse 100 sessions: <10 seconds
- Calculate metrics for 1000 sessions: <30 seconds
- API response time (summary): <500ms
- Dashboard load time: <2 seconds
- File watcher latency: <5 seconds from session end to metrics update

---

## 9. Critical Design Decisions

### Decision 1: Local SQLite vs. Remote Database

**Choice:** Local SQLite

**Reasoning:**
- ✅ Privacy by design (data never leaves machine)
- ✅ No server setup required
- ✅ Scales to millions of sessions on laptop
- ✅ Simple deployment (pip install + run)
- ✅ Aligns with V1 scope (personal insights)

**Trade-offs:**
- ❌ Can't support team features without data sharing mechanism
- ❌ No real-time sync across devices

**Future:** V2 will add optional cloud sync for team features.

---

### Decision 2: Polars vs. Pandas

**Choice:** Polars

**Reasoning:**
- ✅ 10-100x faster for time-series operations
- ✅ Better memory efficiency
- ✅ Modern API (less legacy baggage)
- ✅ Better type safety

**Trade-offs:**
- ❌ Smaller ecosystem than Pandas
- ❌ Less familiar to many developers

**Mitigation:** Use Polars for internal processing, expose standard Python types in API.

---

### Decision 3: LLM Tips Generation vs. Rule-Based

**Choice:** LLM-based with rule-based fallback

**Reasoning:**
- ✅ More nuanced, contextual suggestions
- ✅ Can explain "why" not just "what"
- ✅ Adapts to usage patterns naturally
- ✅ Uses user's existing Amplifier LLM config

**Trade-offs:**
- ❌ Requires LLM access (costs money)
- ❌ Slower than rule-based (1-2s latency)
- ❌ Less predictable output

**Mitigation:** Cache tips, generate daily not on-demand. Provide rule-based tips if LLM unavailable.

---

### Decision 4: Conversational-First vs. Dashboard-First

**Choice:** Conversational-first

**Reasoning:**
- ✅ Aligns with principle "Conversational First, Dashboard Second"
- ✅ Lower barrier to value (no context switch)
- ✅ Faster to build and validate
- ✅ Natural for users already in Amplifier

**Trade-offs:**
- ❌ Less rich visualization initially
- ❌ Dashboard features delayed

**Sequencing:** Phase 2 = Conversational, Phase 4 = Dashboard (validate engagement first).

---

### Decision 5: Real-Time vs. Batch Processing

**Choice:** Real-time (incremental) with file watcher

**Reasoning:**
- ✅ Aligns with principle "Incremental Computation"
- ✅ Insights available immediately after session
- ✅ Better user experience (no waiting)
- ✅ Scales better (no expensive batch jobs)

**Trade-offs:**
- ❌ More complex (file watching, event-driven)
- ❌ Background service required

**Mitigation:** Make background service optional - CLI can do one-off batch processing.

---

## 10. Future Considerations (V2+)

### V2: Team Insights

**Architectural Changes Needed:**

1. **Multi-User Support**
   - User ID field (currently hardcoded to "local")
   - Authentication system
   - Authorization (who can see team metrics)

2. **Data Aggregation Service**
   - Collect metrics from multiple users
   - Compute team-level aggregations
   - Privacy: aggregated metrics only, no raw session data

3. **Team Database**
   - Centralized storage for team metrics
   - Could be self-hosted or cloud service
   - Encryption at rest

**Current Architecture Supports:**
- ✅ User ID field exists in all models (currently "local")
- ✅ Metrics are already aggregated (easy to combine across users)
- ✅ Tool usage patterns are comparable (standardized metrics)

**Gaps to Address:**
- Need: Secure data sharing mechanism
- Need: Team roster management
- Need: Public team dashboard UI

---

### V3: Manager Insights

**Architectural Changes Needed:**

1. **Coaching Context**
   - Manager-specific views (not just aggregations)
   - Coaching opportunity detection (alerts)
   - Historical coaching log

2. **Comparative Analytics**
   - High performer pattern identification
   - Struggling user early detection
   - Team capability benchmarking

**Current Architecture Supports:**
- ✅ All metrics needed for coaching already computed
- ✅ Growth trends track improvement/decline
- ✅ Pattern detection identifies behaviors

**Gaps to Address:**
- Need: Alert system for coaching opportunities
- Need: Manager-specific UI views
- Need: Integration with performance management systems

---

### Extensibility: Other AI Tools

**Current Architecture:**

```python
# Session parser is Amplifier-specific
class AmplifierSessionParser:
    def parse(self, session_dir: Path) -> Session:
        # Parse events.jsonl, transcript.jsonl
        pass

# But data model is generic
@dataclass
class Session:
    """Generic AI tool session - not Amplifier-specific."""
    session_id: str
    started_at: datetime
    tools_used: list[str]  # Works for any AI tool
    # ...
```

**To Add Another Tool (e.g., Claude Desktop):**

1. Create `ClaudeSessionParser` (implement common interface)
2. Register parser in config
3. All downstream logic works (metrics, growth, tips)

**Design Principle Applied:** "Extensible to Other AI Tools" (Principle #4)

---

## 11. Open Questions & Risks

### Open Questions

1. **Metric Validation**
   - **Q:** Do the metrics we compute actually correlate with user skill?
   - **Validation:** Compare metrics to user self-assessment + peer reviews
   - **Timeline:** Phase 5 (alpha testing)

2. **Privacy Comfort Level**
   - **Q:** Are users comfortable with local analytics on their work?
   - **Validation:** User interviews during alpha
   - **Mitigation:** Transparent about what's tracked, easy opt-out

3. **Engagement Cadence**
   - **Q:** How often will users check insights?
   - **Hypothesis:** Weekly for conversational, monthly for dashboard
   - **Validation:** Measure actual usage patterns in alpha

4. **Tips Quality**
   - **Q:** Are LLM-generated tips actually helpful?
   - **Validation:** Tip feedback system (helpful/not helpful)
   - **Mitigation:** Curate tip templates, use rule-based fallback

---

### Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Amplifier session format changes** | H | M | Version format parsing, graceful degradation |
| **Low engagement after novelty** | H | M | Conversational interface reduces friction, focus on valuable metrics |
| **Metrics don't drive improvement** | H | M | Iterate on metrics based on user feedback, focus on actionable tips |
| **Performance issues with large session histories** | M | M | Incremental computation, database indexes, pagination |
| **Users don't trust the metrics** | H | L | Transparent calculations, show raw data, explainable metrics |
| **Privacy concerns block adoption** | M | L | Local-only storage, no cloud required, clear communication |

---

## 12. Summary

### What We're Building

**V1 Personal Insights** provides individual contributors with comprehensive analytics on their AI collaboration effectiveness through:

1. **Conversational Interface** - Natural language queries within Amplifier sessions
2. **Web Dashboard** - Visual exploration and deep analysis
3. **Growth Tracking** - Week-over-week improvement indicators
4. **Actionable Tips** - LLM-generated suggestions based on patterns

### Key Architectural Principles

- **Privacy by Design** - Local SQLite storage, no data leaves machine
- **Incremental Computation** - Real-time updates as sessions complete
- **Conversational First** - Primary interface is natural language, dashboard is secondary
- **Simple Metrics First** - Transparent, explainable calculations
- **Extensible** - Designed to support team features (V2) and other AI tools (future)

### Implementation Timeline

- **Weeks 1-2:** Foundation (project setup, session parsing)
- **Weeks 3-4:** Core Analytics (metrics calculation, file watching)
- **Weeks 5-6:** Conversational Interface (Amplifier integration)
- **Week 7:** Tips Generation (LLM-based suggestions)
- **Weeks 8-10:** Web Dashboard (Vue.js frontend)
- **Weeks 11-12:** Polish & Launch (testing, docs, alpha release)

**Total: 12 weeks to production-ready V1.0**

### Success Criteria

- ✅ 50%+ weekly active usage (users check insights weekly)
- ✅ 60%+ find value (rate insights as valuable)
- ✅ 40%+ behavior change (users change how they work)
- ✅ 50%+ retention at 60 days (still using 2 months later)

### Next Steps

1. **Create project structure** (directories, pyproject.toml)
2. **Implement session parser** (read Amplifier session files)
3. **Set up SQLite database** (schema + migrations)
4. **Build metrics calculator** (session-level metrics)
5. **Test with real sessions** (validate on your own Amplifier sessions)

---

## Related Documentation

- [VISION.md](../01-vision/VISION.md) - Strategic vision and positioning
- [PRINCIPLES.md](../01-vision/PRINCIPLES.md) - Implementation philosophy
- [SUCCESS-METRICS.md](../01-vision/SUCCESS-METRICS.md) - How we measure success
- [Epic 01: Personal Insights](../02-requirements/epics/01-personal-insights.md) - Feature requirements

---

## Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-02-03 | Chris Park (with AI) | Initial technical architecture for V1 |

---