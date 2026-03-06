# amplifier-usage-insights

**You work with AI constantly. Do you actually know if you're getting better?**

A CLI analytics tool that scans your Amplifier AI agent sessions and tells you how you're actually working with AI — delegation patterns, tool usage, error rates, week-over-week trends.

---

## What the data shows

After scanning **4,362 sessions** and tracking **57,094+ tool calls** across **32 unique tools**:

- Delegation ratio grew from **0.42× per session** (January) → **14.9×** (March)
- `bash` dropped from **52% of tool calls** (January) → **28%** (March) — a measurable shift toward higher-level agents
- Error rate stayed under **1%** throughout
- The tool found and helped fix bugs in its own parser (yes, meta)

These aren't hypotheticals. This is what running the tool on real usage looks like.

---

## Example output

```
This Week vs Last Week:
• 181 sessions (+62%)
• 32 different tools used
• Delegation ratio: 14.9× per session
• Error rate: 0.8%

Top Tools:
1. bash        (28%)
2. read_file   (24%)
3. todo        (14%)
4. web_search  (8.5%)
5. delegate    (5.5%)

💡 Tips:

[HIGH] Your bash usage is 28% — consider delegating more file and git operations
```

---

## What it does

- **Work Summary** — Sessions, tools used, delegation patterns, error rates
- **Growth Tracking** — Week-over-week trends so you can see if habits are actually changing
- **Actionable Tips** — Rule-based suggestions tied to your specific patterns
- **Conversational Access** — Ask "How am I doing this week?" inside any Amplifier session

---

## Quick Start

### Install

```bash
cd ~/Projects/amplifier-usage-insights
pip install -e .
```

### Initialize and scan

```bash
amplifier-insights init
amplifier-insights refresh   # Scans your Amplifier session data
```

### Get insights

```bash
amplifier-insights show          # Weekly summary
amplifier-insights show tools    # Tool usage breakdown
amplifier-insights show growth   # Growth trends over time
```

### Or ask conversationally (in any Amplifier session)

```
"How am I doing this week?"
"What tools do I use most?"
"Am I improving?"
```

*(Requires Amplifier tool configured in `settings.yaml`)*

---

## Architecture

```
Amplifier Sessions (events.jsonl, transcript.jsonl, metadata.json)
    ↓
Session Parser (extract metrics: tools, delegations, errors)
    ↓
SQLite Database (local, privacy-first storage)
    ↓
Metrics Calculator (weekly aggregations, growth comparison)
    ↓
Rule-Based Tips (pattern rules)
    ↓
Insights Engine (query interface)
    ↓
┌─────────────────────┬──────────────────────┐
│ CLI Tool            │ Amplifier Tool       │
│ (amplifier-insights)│ (conversational)     │
└─────────────────────┴──────────────────────┘
```

---

## Tech stack

- **Python 3.11+**, SQLite, Typer CLI, Rich terminal output
- 52 tests passing
- Local-only storage — your session data stays on your machine

---

## Principles

1. **Growth Over Surveillance** — Help you improve, not police you
2. **AI-First Metrics** — Measure AI collaboration quality, not pre-AI productivity
3. **Leading Indicators** — Process quality (delegation, tool choice) predicts outcomes
4. **Privacy by Design** — Local storage, no upload required
5. **Individual Value First** — Personal insights before any team features

---

## Roadmap

| What | Status |
|---|---|
| CLI analytics core | ✅ Shipped |
| Conversational Amplifier tool | ✅ Shipped |
| Growth trend tracking | ✅ Shipped |
| Web dashboard + visualizations | Planned |
| LLM-generated tips (vs. rule-based) | Planned |
| Team insights + peer comparison | Planned |

---

## Related

- [amplifier-session-capture](https://github.com/cpark4x/amplifier-session-capture) — Session-level data collection
- [amplifier-doc-driven-dev](https://github.com/cpark4x/amplifier-doc-driven-dev) — Documentation-driven development recipes

---

## Built by

**Chris Park** — Senior PM, Microsoft Office of the CTO, AI Incubation group.

Questions, feedback, or ideas: open an issue or find me at [@cpark4x](https://github.com/cpark4x).

---

MIT License
