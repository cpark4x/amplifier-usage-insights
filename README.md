# Amplifier Usage Insights

**Analytics system that helps individuals, teams, and managers understand AI collaboration effectiveness and build world-class AI-first teams.**

## What It Does

Transforms Amplifier session data into actionable insights about how you work with AI:

- **📊 Work Summary** - Sessions, tools used, time spent, delegation patterns
- **📈 Growth Tracking** - Week-over-week improvement in AI collaboration skills
- **💡 Actionable Tips** - Specific suggestions based on your usage patterns
- **🎯 Conversational Access** - Ask "How am I doing?" in any Amplifier session

## Quick Start (V0.5)

### 1. Install

```bash
cd ~/Projects/amplifier-usage-insights
pip install -e .
```

### 2. Initialize Database

```bash
amplifier-insights init
amplifier-insights refresh  # Scan your Amplifier sessions
```

### 3. Get Insights

**Via CLI:**
```bash
amplifier-insights show         # Weekly summary
amplifier-insights show tools   # Tool usage breakdown
amplifier-insights show growth  # Growth trends
```

**In Amplifier Sessions:**
```
"How am I doing this week?"
"What tools do I use most?"
"Am I improving?"
```

*(Tool automatically loads if configured in settings.yaml)*

## Current Status

**V0.5 (Validation Build) - ✅ Complete**
- Analytics core (session parser, metrics calculator, SQLite storage)
- Conversational interface (Amplifier tool)
- Rule-based tips generator
- CLI tool (`amplifier-insights`)
- Tested with 509 real sessions
- 49 tests passing, 95%+ coverage

**Next: 2-Week Validation Period**
- Test: Do insights drive behavior change?
- Measure: Weekly usage frequency
- Decide: Build web dashboard (V1.0) or iterate on metrics

**V1.0 (Future) - 📋 Planned**
- Web dashboard with visualizations
- LLM-based tips (vs. rule-based)
- Advanced growth analytics
- Real-time updates

**V2.0 (Future) - 📋 Planned**
- Team Insights (peer comparison, collective learning)
- Shared storage for multi-user
- Best practice identification

**V3.0 (Future) - 📋 Planned**
- Manager Insights (coaching, team health)
- Development planning
- Team capability benchmarking

## Documentation

**Vision & Requirements:**
- [VISION.md](docs/01-vision/VISION.md) - Problems, positioning, roadmap
- [PRINCIPLES.md](docs/01-vision/PRINCIPLES.md) - Design principles and decision framework
- [SUCCESS-METRICS.md](docs/01-vision/SUCCESS-METRICS.md) - How we measure success

**Epics:**
- [Epic 01: Personal Insights](docs/02-requirements/epics/01-personal-insights.md) - V1 scope
- [Epic 02: Team Insights](docs/02-requirements/epics/02-team-insights.md) - V2 scope
- [Epic 03: Manager Insights](docs/02-requirements/epics/03-manager-insights.md) - V3 scope

**Technical:**
- [V0.5 Design](docs/03-technical-architecture/V0.5-DESIGN.md) - Validation build architecture
- [V1 Architecture](docs/03-technical-architecture/V1-ARCHITECTURE.md) - Full vision architecture

## Architecture (V0.5)

```
Amplifier Sessions (events.jsonl, transcript.jsonl, metadata.json)
    ↓
Session Parser (extract metrics: tools, delegations, errors)
    ↓
SQLite Database (local, privacy-first storage)
    ↓
Metrics Calculator (weekly aggregations, growth comparison)
    ↓
Rule-Based Tips (5 pattern rules)
    ↓
Insights Engine (query interface)
    ↓
┌─────────────────────┬──────────────────────┐
│ CLI Tool            │ Amplifier Tool       │
│ (amplifier-insights)│ (conversational)     │
└─────────────────────┴──────────────────────┘
```

## Principles

1. **Growth Over Surveillance** - Help users improve, not police them
2. **Transparency Builds Trust** - Team metrics public to all team members
3. **AI-First Metrics** - Measure AI collaboration, not pre-AI productivity
4. **Leading Indicators** - Process quality predicts success
5. **Privacy by Design** - Local storage, no upload required for V1
6. **Individual Value First** - Personal insights before team/manager features

## Example Output

```
Here's your weekly summary:

This Week vs Last Week:
• 100 sessions (N/A)
• 14 different tools used
• Delegation ratio: 3%
• Error rate: 0%
• Avg session duration: 25min

Top Tools This Week:
1. bash
2. read_file
3. todo
4. edit_file
5. delegate

💡 2 Tips for Improvement:

[HIGH] delegation
📊 Your delegation ratio is 3% (3 delegations in 100 sessions)
💡 Break down complex problems and delegate to specialized agents
✨ Better results through specialized expertise

[MEDIUM] tool_usage
📊 You use bash 54% of the time (1131 calls this week)
💡 Try grep/glob instead of bash for file operations
✨ 30% faster with specialized tools
```

## Related Projects

- [amplifier-session-insights](https://github.com/cpark4x/amplifier-session-insights) - Session-level data collection
- [amplifier-doc-driven-dev](https://github.com/cpark4x/amplifier-doc-driven-dev) - Documentation-driven development recipes

## Contributing

This is currently a personal project by [@cpark4x](https://github.com/cpark4x) built for learning and experimentation.

If you're interested in collaborating or have feedback, please open an issue!

## License

MIT
