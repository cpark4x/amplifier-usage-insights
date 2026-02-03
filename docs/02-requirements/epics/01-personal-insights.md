# Epic 01: Personal Insights

**Owner:** Chris Park  
**Contributors:** Chris Park

---

## 1. Summary

Personal Insights enables individual contributors to understand their AI collaboration effectiveness through comprehensive analytics on their Amplifier usage. By surfacing work history, growth trajectory, and actionable improvement opportunities, this epic transforms raw session data into a feedback loop that drives continuous skill development. This is the foundation that validates whether measurement drives improvement in AI-first work.

---

## 2. Problem

**Individual contributors using AI tools daily have no systematic way to understand if they're getting better at AI collaboration.**

Current reality:
- They use Amplifier (or other AI tools) for hours each day
- Success or failure feels random—sometimes AI helps, sometimes it doesn't
- No visibility into whether they're improving over time or developing bad habits
- Can't tell if poor outcomes are due to their approach or AI tool limitations
- No feedback loop to guide improvement
- High performers don't know what makes them effective
- Struggling users don't know what to change

**The impact:** People plateau at basic AI usage instead of becoming world-class AI practitioners. Organizations invest in AI tools but not in developing the skills to use them effectively. Competitive advantage is lost.

---

## 3. Proposed Solution

**Give users comprehensive visibility into their AI collaboration effectiveness with Personal Insights.**

When this epic is complete, users will be able to:

- **See their complete work history** - All Amplifier sessions aggregated with usage patterns over time
- **Track their growth** - Week-over-week improvement in AI collaboration skills
- **Understand their patterns** - Tool usage, delegation effectiveness, session characteristics
- **Get actionable tips** - Specific suggestions based on their individual patterns
- **Compare to their past self** - "Am I better this month than last month?"
- **Explore via conversation** - Ask "How am I doing?" in any Amplifier session
- **Dive deep via dashboard** - Web interface for detailed exploration and visualization

**The experience:**

```
User in Amplifier session: "How's my AI usage this week?"

Response:
"You're showing strong growth! 🚀

This week:
- 12 sessions (up from 8 last week)
- 15% more effective tool usage (using grep instead of multiple file reads)
- Delegation patterns improved - breaking down problems well

Growth area: Error handling
- Your error rate is 2x higher than your average
- Tip: When you hit errors, try asking for alternative approaches instead of retrying the same path

Want to see your full dashboard?"
```

Users get immediate feedback during their work, not requiring context switch to a separate analytics tool.

---

## 4. User Stories

**IMPORTANT:** User stories will be created ONLY when implementing features. This section tracks what's built, not what's planned.

### Implemented

_(None yet - stories created as features are built)_

### Future

- ⏭️ **Session history aggregation** - View all sessions with filters (date range, project, duration)
- ⏭️ **Basic personal metrics** - Duration, turns, tool usage, files touched, error patterns
- ⏭️ **Growth tracking** - Week-over-week comparison, skill progression indicators
- ⏭️ **Tool usage analysis** - Which tools used, frequency, effectiveness patterns
- ⏭️ **Delegation patterns** - Agent usage, task decomposition effectiveness
- ⏭️ **Actionable tips** - Context-specific improvement suggestions based on patterns
- ⏭️ **Conversational interface** - Natural language queries within Amplifier sessions
- ⏭️ **Web dashboard** - Visual exploration with charts and detailed breakdowns
- ⏭️ **Personal benchmarking** - Compare current performance to personal best
- ⏭️ **Privacy controls** - Control what data is collected and retained

---

## 5. Outcomes

**Success Looks Like:**

- **50%+ weekly active usage** - Users check insights at least weekly
- **60%+ find value** - Rate insights as valuable or very valuable
- **40%+ behavior change** - Users report changing how they work based on insights
- **50%+ retention at 60 days** - Still using 2 months after install
- **Measurable improvement** - Users show objective skill growth over time

**We'll Measure:**

- Engagement metrics (DAU, query frequency, dashboard visits)
- Behavior change (self-reported + observed pattern changes)
- Skill improvement (tool sophistication, delegation effectiveness, error rates over time)
- User satisfaction (perceived value, would recommend, retention)
- Strategic validation (does measurement drive improvement?)

See [SUCCESS-METRICS.md](../../01-vision/SUCCESS-METRICS.md) for detailed metrics.

---

## 6. Dependencies

**Requires:**
- Amplifier session data (events.jsonl, transcript.jsonl, metadata.json)
- amplifier-session-insights module (data collection layer)
- LLM access for conversational interface
- Web hosting for dashboard (static site or simple server)

**Enables:**
- V2: Team Insights (requires multiple users with V1 installed)
- Learning which metrics drive improvement (guides V2/V3 priorities)
- Data foundation for team and manager insights

**Blocks:**
- All team and manager features (V2/V3) depend on V1 validation

---

## 7. Risks & Mitigations

| Risk | Impact | Probability | Strategic Response |
|------|--------|-------------|-------------------|
| Users find metrics confusing/meaningless | H | M | Progressive disclosure, start with simplest metrics, iterate based on feedback |
| Privacy concerns prevent adoption | H | M | Local-only storage for V1, clear privacy controls, transparency about what's tracked |
| Insights don't drive behavior change | H | M | Focus on actionable tips, show concrete improvement paths, validate with user research |
| Low engagement after initial curiosity | M | H | Conversational interface keeps insights accessible during work, not separate tool |
| Metrics don't correlate with actual skill | H | L | Validate metrics against user perception and outcomes, iterate based on data |
| Users game the metrics | M | L | Focus on leading indicators hard to game (process quality, not quantity) |
| Dashboard becomes required for value | M | M | Prioritize conversational interface, dashboard is secondary |

---

## 8. Open Questions

- [ ] What metrics do users actually care about? (Validate with early users)
- [ ] Which improvement tips are most actionable? (A/B test different tip styles)
- [ ] How often should users check insights? (Daily, weekly, monthly?)
- [ ] What's the right granularity for growth tracking? (Daily, weekly, monthly comparisons?)
- [ ] Should personal insights be opt-in or default-on? (Privacy vs. adoption trade-off)
- [ ] What visualizations are most useful? (Charts, tables, trends?)
- [ ] How do we handle users with very few sessions? (Need minimum data for meaningful insights)
- [ ] What's the conversational UX? (Inline in sessions, separate command, tool call?)

---

## 9. Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-02-03 | Chris Park | Initial epic for V1 Personal Insights |

---
