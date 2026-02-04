# Usage Insights Tool - Guide

## What This Tool Does

The `get_usage_insights` tool provides conversational insights about your AI collaboration effectiveness based on your Amplifier session history.

## When to Use

Use this tool when the user wants to understand:
- Their AI usage patterns and trends
- How they're using Amplifier tools
- Whether they're improving over time
- Personalized tips for better effectiveness

## How to Use

The tool accepts natural language queries and returns formatted insights.

### Example Queries

**Weekly Summary:**
- "How am I doing this week?"
- "Show my weekly summary"
- "What's my status?"

**Tool Usage:**
- "What tools do I use most?"
- "Show my tool usage"
- "Which tools am I using?"

**Growth Tracking:**
- "Am I improving?"
- "Show my growth"
- "How have I progressed?"

**Tips:**
- "What are my tips?"
- "How can I improve?"
- "Give me suggestions"

## Response Format

The tool returns:
- **Summary**: Quick overview (e.g., "12 sessions this week, up 50%")
- **Metrics**: Session counts, tool usage, effectiveness indicators
- **Growth**: Week-over-week changes and trends
- **Tips**: Actionable recommendations based on usage patterns

## Data Source

- Reads from `~/.amplifier-usage-insights/metrics.db`
- Analyzes sessions from `~/.amplifier/projects/`
- User must run `amplifier-insights refresh` periodically to update data

## Privacy

All data is stored locally. No session content or messages are stored, only metadata like:
- Session timing and duration
- Tool usage counts
- Turn counts
- Error counts

## Setup Required

Before using this tool, the user must:
1. Install: `pip install -e ~/Projects/amplifier-usage-insights`
2. Initialize: `amplifier-insights init`
3. Scan sessions: `amplifier-insights refresh`
4. Link bundle: `ln -s ~/Projects/amplifier-usage-insights/bundles/usage-insights ~/.amplifier/bundles/`

## Error Handling

If the database doesn't exist, the tool will return:
"No insights data found. Run `amplifier-insights init` and `amplifier-insights refresh` first."

## Example Usage

```
User: "How am I doing this week?"