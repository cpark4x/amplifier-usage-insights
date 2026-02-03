# Epic 02: Team Insights

**Owner:** Chris Park  
**Contributors:** Chris Park

---

## 1. Summary

Team Insights enables team members to learn from each other through transparent, public metrics that foster healthy competition and knowledge sharing. By providing peer comparison, collective growth tracking, and visibility into what high performers do differently, this epic transforms individual improvement into collective team capability development. This validates whether transparency drives faster collective growth than isolated individual improvement.

---

## 2. Problem

**Teams using AI tools have no visibility into collective effectiveness or opportunities to learn from each other.**

Current reality:
- Each team member improves in isolation (or doesn't improve at all)
- No one knows who the high performers are or what they do differently
- Best practices stay siloed within individuals
- No healthy competition or peer learning
- Team AI capability develops unevenly
- Managers see who ships what, but teams can't see collaboration patterns
- Knowledge sharing is accidental, not systematic

**The impact:** Teams plateau at mediocre AI usage because best practices don't spread. Organizations have pockets of excellence but can't scale it across the team. Competitive advantage is limited to individual performers, not team capability.

---

## 3. Proposed Solution

**Give teams transparent visibility into collective AI collaboration effectiveness with Team Insights.**

When this epic is complete, team members will be able to:

- **See team-wide metrics** - Collective usage, adoption rates, tool patterns
- **Compare to peers** - Percentile rankings, relative performance (public to all team members)
- **Learn from high performers** - What do top performers do differently?
- **Track collective growth** - Is the team improving over time?
- **Share knowledge systematically** - Surface effective techniques, spread across team
- **Celebrate team wins** - Collective achievements and milestones
- **Identify collaboration opportunities** - Who's working on similar problems?
- **Access via conversation** - "Show team metrics", "How do I compare to the team?"
- **Explore via dashboard** - Team view with peer comparison and best practices

**The experience:**

```
Team member in Amplifier session: "How does my AI usage compare to the team?"

Response:
"You're in the 65th percentile this week! 📊

Team snapshot:
- 12/15 team members actively using Amplifier
- Collective growth: +18% effectiveness vs. last month
- Top pattern: High performers delegate to agents 2.3x more often

Your standing:
- Tool sophistication: 65th percentile (above average)
- Delegation patterns: 45th percentile (opportunity area)
- Session effectiveness: 70th percentile (strong)

What top performers do differently:
- Break down complex tasks into 3-5 agent delegations vs. your 1-2
- Use 'foundation:zen-architect' before 'modular-builder'

Try: More agent delegation for your next complex task.

See team dashboard for full breakdown."
```

**Critical principle:** All team metrics are **public to team members**. This is transparency, not surveillance.

---

## 4. User Stories

**IMPORTANT:** User stories will be created ONLY when implementing features. This section tracks what's built, not what's planned.

### Implemented

_(None yet - Epic 01 must complete before starting Epic 02)_

### Future

- ⏭️ **Team roster and participation** - Who's on the team, who's actively using
- ⏭️ **Collective team metrics** - Team-wide usage, patterns, growth over time
- ⏭️ **Peer comparison** - Percentile rankings across key effectiveness dimensions
- ⏭️ **High performer identification** - Who's in top quartile, what patterns they exhibit
- ⏭️ **Best practice surfacing** - "What do high performers do differently?"
- ⏭️ **Team growth dashboard** - Collective skill progression over time
- ⏭️ **Knowledge sharing prompts** - "3 people tried this technique after seeing it worked for Alex"
- ⏭️ **Team leaderboard** - Transparent rankings with growth indicators (public to team)
- ⏭️ **Collaboration opportunities** - "Sam is working on similar problems - consider collaborating"
- ⏭️ **Team opt-in controls** - Team members control what's shared at team level
- ⏭️ **Conversational team queries** - "Show team metrics", "Who's the top performer in delegation?"
- ⏭️ **Team web dashboard** - Visual team view with peer comparison

---

## 5. Outcomes

**Success Looks Like:**

- **70%+ team participation** - Majority of team actively using
- **60%+ peer learning** - Team members report learning from peer metrics
- **30%+ team skill growth** - Collective AI effectiveness increases measurably over 90 days
- **80%+ support transparency** - Team accepts and values public metrics culture
- **Best practice spread** - When high-performer patterns identified, 60%+ try them within 2 weeks

**We'll Measure:**

- Team adoption rate (what % of team has V1 and participates in team view)
- Peer learning (self-reported + observed pattern changes after viewing team metrics)
- Collective improvement (team average effectiveness over time)
- Knowledge transfer (speed at which best practices spread)
- Team culture (acceptance of transparency, peer mentoring instances)

See [SUCCESS-METRICS.md](../../01-vision/SUCCESS-METRICS.md) for detailed V2 metrics.

---

## 6. Dependencies

**Requires:**
- **Epic 01 complete** - Personal Insights working and validated (must have individual value first)
- **3+ team members with V1 installed** - Need critical mass for meaningful comparison
- **Team roster definition** - Who's on the team? How do we define team boundaries?
- **Shared storage or aggregation** - Team metrics require data from multiple users

**Enables:**
- Epic 03: Manager Insights (managers need team data to provide coaching)
- Team capability benchmarking (compare teams across organization)
- Cross-team knowledge sharing (what works in Team A can inform Team B)

**Blocks:**
- Manager coaching features (Epic 03) - need team visibility first

---

## 7. Risks & Mitigations

| Risk | Impact | Probability | Strategic Response |
|------|--------|-------------|-------------------|
| Team members resist public metrics | H | H | Make opt-in initially, demonstrate value before requiring, emphasize growth over ranking |
| Unhealthy competition instead of learning | H | M | Frame as percentiles not rankings, pair comparisons with "what to learn", no shaming |
| Low team adoption (not enough users) | H | M | Epic 01 must deliver strong value, V2 requires team buy-in, seed with early adopters |
| Privacy concerns about sharing data | H | M | Clear controls on what's shared, team-level aggregation only, no session details exposed |
| Gaming the metrics | M | M | Focus on hard-to-game process indicators, emphasize learning over competition |
| Team fragmentation (some participate, some don't) | M | H | Require minimum team participation (e.g., 50%) before enabling team view |
| Comparison discourages struggling members | H | L | Show growth trajectory alongside current standing, celebrate improvement |

---

## 8. Open Questions

- [ ] How do we define team boundaries? (GitHub org, manager assignment, self-selected?)
- [ ] What's the minimum team size for meaningful comparison? (3? 5? 10?)
- [ ] Should team participation be opt-in or opt-out? (Privacy vs. value trade-off)
- [ ] How do we handle teams with wildly different work types? (Fair comparison?)
- [ ] What level of granularity for peer comparison? (Percentiles, quartiles, top/middle/bottom?)
- [ ] Should we show identities in team metrics or anonymize? (Transparency principle says show, but privacy?)
- [ ] How often do team metrics update? (Real-time, daily, weekly?)
- [ ] What's the onboarding flow for teams? (All join together, or gradual rollout?)
- [ ] How do we prevent team metrics from becoming performance review fodder? (Despite transparency principle)

---

## 9. Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-02-03 | Chris Park | Initial epic for V2 Team Insights |

---
