# Epic 03: Manager Insights

**Owner:** Chris Park  
**Contributors:** Chris Park

---

## 1. Summary

Manager Insights empowers engineering managers to build world-class AI-first teams through data-driven coaching and development. By providing team health visibility, individual performance assessments, coaching opportunity detection, and targeted development planning, this epic transforms managers from outcome observers into proactive capability builders. This validates whether data-driven coaching accelerates team AI effectiveness beyond what transparency and individual improvement alone can achieve.

---

## 2. Problem

**Engineering managers responsible for building AI-first teams lack visibility into how their team members collaborate with AI and where to focus coaching efforts.**

Current reality:
- Managers only see outcomes (what shipped) but not process (how it was built with AI)
- Can't tell who's thriving vs. struggling until outcomes reveal it (too late to coach)
- Can't identify specific skill gaps to target in development conversations
- Don't know who needs coaching, who's ready for complex work, who's plateauing
- Lack data to make coaching conversations actionable and specific
- Can't recognize high performers' methods to scale across team
- Miss early warning signals when team members struggle
- Rely on gut feel instead of objective patterns

**The impact:** Coaching happens reactively (after problems emerge) instead of proactively (before they manifest). High performers go unrecognized because their methods aren't visible. Struggling team members don't get targeted help early enough. Organizations can't systematically build AI-first capability at team scale.

---

## 3. Proposed Solution

**Give managers coaching-focused visibility into team AI collaboration effectiveness with Manager Insights.**

When this epic is complete, managers will be able to:

- **See team health at a glance** - Overall AI adoption, engagement levels, collective effectiveness
- **Assess individual performance** - Who's thriving? Who's struggling? Who's plateauing?
- **Detect coaching opportunities early** - Warning signals before outcomes degrade
- **Understand skill gaps** - What specific areas need development for each team member?
- **Plan targeted development** - Data-driven skill development goals for 1-on-1s
- **Track coaching impact** - Did interventions work? Is the team improving?
- **Identify high performers** - What do they do differently? How to scale their methods?
- **Benchmark team capability** - How does the team compare to world-class AI-first teams?
- **Access via conversation** - "Show team health", "Who needs coaching this week?"
- **Explore via dashboard** - Manager view optimized for coaching and development

**The experience:**

```
Manager in Amplifier session: "Show me team health for this week"

Response:
"Team AI Effectiveness: Strong growth trajectory 📈

Overall Health:
- 13/15 members actively using AI (87% adoption)
- Team effectiveness: 72nd percentile (up from 65th last month)
- Collective growth: +12% this month

🟢 Thriving (5 members):
- Alex: Top quartile, sophisticated delegation patterns
- Sam: Rapid improvement (+25% effectiveness in 30 days)
- Jordan: Consistently high session impact

🟡 Steady (6 members):
- Showing growth but opportunity for acceleration
- Suggest: Share Alex's delegation patterns in next standup

🔴 Needs Coaching (2 members):
- Taylor: Error rate spiking (3x team average this week)
  → Coaching: Review error handling patterns together
- Morgan: Delegation patterns regressing (was 60th %ile, now 35th)
  → Check-in: Is workload or task complexity an issue?

Development Opportunities:
- 8 team members would benefit from agent delegation training
- Tool sophistication gap: Share grep/glob best practices

Ready to dive into individual assessments?"
```

**Critical principle:** Manager views add coaching context, they don't show team metrics that team members can't see (transparency maintained).

---

## 4. User Stories

**IMPORTANT:** User stories will be created ONLY when implementing features. This section tracks what's built, not what's planned.

### Implemented

_(None yet - Epic 02 must complete before starting Epic 03)_

### Future

- ⏭️ **Team health dashboard** - Overall AI adoption, engagement, effectiveness snapshot
- ⏭️ **Individual performance summaries** - Per-team-member assessments with coaching context
- ⏭️ **Coaching opportunity detection** - Early warning signals for struggling patterns
- ⏭️ **Skill gap identification** - What specific areas need development per person
- ⏭️ **Development planning interface** - Set and track AI skill development goals
- ⏭️ **Coaching impact tracking** - Did interventions work? Before/after comparison
- ⏭️ **High performer pattern analysis** - What makes top performers effective?
- ⏭️ **Team capability benchmarking** - Compare to world-class AI-first teams
- ⏭️ **Growth trajectory visualization** - Who's improving, who's plateauing, who's regressing
- ⏭️ **Coaching conversation prompts** - Suggested discussion topics based on data
- ⏭️ **Team readiness assessment** - Who's ready for more complex work?
- ⏭️ **Conversational manager queries** - "Who needs coaching?", "Show team capability trends"
- ⏭️ **Manager web dashboard** - Coaching-optimized view with individual drill-down

---

## 5. Outcomes

**Success Looks Like:**

- **80%+ manager weekly engagement** - Managers check team health dashboard weekly
- **3+ coaching conversations per month** - Driven by insights (not just scheduled 1-on-1s)
- **70%+ early detection** - Struggling patterns identified before outcomes degrade
- **Top 25% team capability** - Team ranks in top quartile of AI effectiveness
- **90%+ continuous improvement** - Nearly all team members show sustained growth over 6 months
- **80%+ manager confidence** - Managers feel equipped to coach AI skills effectively

**We'll Measure:**

- Manager engagement (dashboard usage, coaching conversation frequency)
- Proactive intervention (early detection rate, coaching triggered by insights)
- Team capability (collective effectiveness benchmark, skill variance reduction)
- Manager effectiveness (retention of high performers, skill development velocity)
- Manager satisfaction (confidence in coaching, trust in metrics)

See [SUCCESS-METRICS.md](../../01-vision/SUCCESS-METRICS.md) for detailed V3 metrics.

---

## 6. Dependencies

**Requires:**
- **Epic 01 complete** - Personal Insights validated and working
- **Epic 02 complete** - Team Insights adopted by teams
- **Team participation** - 70%+ of team using Personal and Team Insights
- **Manager training** - How to use insights for coaching, not surveillance
- **Role-based access** - Managers see coaching context, team sees team metrics

**Enables:**
- Organization-wide AI capability benchmarking
- Cross-team best practice sharing at manager level
- AI skill development as part of formal career progression
- Building AI-first culture at organizational scale

**Blocks:**
- Nothing - this is the final phase of the V1/V2/V3 sequence

---

## 7. Risks & Mitigations

| Risk | Impact | Probability | Strategic Response |
|------|--------|-------------|-------------------|
| Feels like surveillance despite design | H | H | Emphasize coaching framing, make opt-in initially, demonstrate value to teams first |
| Manager misuse (performance reviews) | H | M | Training required, explicit guardrails, emphasize growth over punishment |
| Team members resist manager visibility | H | M | Managers see coaching context only (not raw sessions), team controls what's shared |
| Low manager engagement (don't use it) | M | M | Make insights highly actionable, integrate into existing 1-on-1 workflows |
| Metrics don't translate to effective coaching | H | M | Co-design with managers, validate coaching suggestions work |
| Creates pressure instead of growth | H | L | Monitor team satisfaction, require growth mindset training for managers |
| Trust breakdown if misused | H | L | Clear usage guidelines, audit manager access patterns, revoke if abused |
| Manager overwhelm (too much data) | M | M | Progressive disclosure, highlight highest-priority coaching opportunities first |

---

## 8. Open Questions

- [ ] What's the manager onboarding process? (Training required before access?)
- [ ] How do we prevent misuse for performance reviews? (Technical controls or policy only?)
- [ ] Should manager views require team member consent? (Epic 02 is public, but coaching context adds more)
- [ ] What coaching suggestions are most effective? (Validate with manager interviews)
- [ ] How do we measure "good coaching"? (Team member improvement, team satisfaction?)
- [ ] Should managers see individual session details or just aggregated patterns? (Privacy vs. utility trade-off)
- [ ] What's the right frequency for manager dashboard updates? (Daily, weekly?)
- [ ] How do we handle managers who don't use insights? (Required or optional?)
- [ ] Can managers compare teams or only manage their own team? (Cross-team visibility?)
- [ ] What happens when managers leave or team members switch teams? (Data retention, access revocation)

---

## 9. Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-02-03 | Chris Park | Initial epic for V3 Manager Insights |

---
