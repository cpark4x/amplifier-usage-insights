# Amplifier Usage Insights: Principles

**The principles that guide every implementation decision in Amplifier Usage Insights.**

These are not generic software principles—they're specific to building an analytics system for AI-first teams that drives growth, not surveillance.

**Owner:** Chris Park  
**Contributors:** Chris Park

**Last Updated:** 2026-02-03

---

## Summary

These principles define how we build Amplifier Usage Insights: as a growth tool that respects users, measures what matters in AI-first work, and provides leading indicators that enable proactive improvement. They guide product decisions (what features to build), technical decisions (how to build them), design decisions (how they should feel), and development decisions (how we work as a team). These principles serve as the decision framework for AI to make correct choices aligned with our vision of building world-class AI-first teams.

---

## Table of Contents

1. [Core Product Principles](#core-product-principles)
2. [Technical Principles](#technical-principles)
3. [Design Principles](#design-principles)
4. [Development Principles](#development-principles)
5. [Anti-Patterns](#anti-patterns)
6. [Decision Framework](#decision-framework)
7. [How to Use These Principles](#how-to-use-these-principles)

---

## Core Product Principles

These principles define what makes Amplifier Usage Insights different from other analytics products.

### 1. Growth Over Surveillance

**What it means:** Every feature must help users improve, not help managers police them.

**How it guides decisions:**
- ✅ Personal insights that show growth trajectory and improvement opportunities
- ✅ Public team metrics that foster healthy competition and peer learning
- ✅ Coaching-focused manager views that identify development needs
- ❌ Hidden manager dashboards that users can't see
- ❌ Features designed primarily for performance reviews
- ❌ Metrics that shame or punish rather than guide

**Example applications:**
- When team insights show someone is in the bottom quartile, also show what top performers do differently (actionable, not shaming)
- Manager views highlight "who needs coaching" not "who's underperforming" (growth framing)
- All insights include improvement tips, not just data

**Decision rule:** If a feature primarily serves managers without helping the individual improve, it violates this principle.

---

### 2. Transparency Builds Trust

**What it means:** Team members should see the same metrics managers see about team performance.

**How it guides decisions:**
- ✅ Team insights are public to all team members
- ✅ Metrics and calculations are explainable and transparent
- ✅ Users understand what's being measured and why
- ❌ Manager-only dashboards for team metrics
- ❌ Hidden scoring or ranking systems
- ❌ Opaque algorithms that users can't understand

**Example applications:**
- Team leaderboard shows everyone where they stand (transparency, not secrecy)
- Metrics definitions are documented and visible (no black boxes)
- Users can see their raw session data that feeds the system (full transparency)

**Decision rule:** If managers can see team metrics that team members can't, redesign the feature to be transparent by default.

---

### 3. Measure AI Collaboration, Not Pre-AI Productivity

**What it means:** Success in AI-first teams requires different metrics than traditional software development.

**How it guides decisions:**
- ✅ Track agent delegation patterns, tool usage sophistication, AI leverage
- ✅ Measure effectiveness per session (impact vs. time), not just hours worked
- ✅ Capture growth in AI collaboration skills over time
- ❌ Lines of code written (AI generates code, humans orchestrate)
- ❌ Hours logged (efficiency matters more than time)
- ❌ Traditional velocity metrics that miss AI effectiveness

**Example applications:**
- High performers who delegate to agents effectively get recognized, even if they "write" less code
- Session quality measured by outcome achieved and complexity handled, not duration
- Growth metrics track increasing sophistication of AI usage, not increasing output volume

**Decision rule:** Before adding a metric, ask: "Does this measure AI collaboration effectiveness, or pre-AI productivity?"

---

### 4. Leading Indicators Over Lagging Indicators

**What it means:** Process quality and growth patterns predict success better than outcomes alone.

**How it guides decisions:**
- ✅ Track process indicators that predict future success (delegation patterns, error handling, tool usage)
- ✅ Identify growth trajectories early (who's improving vs. plateauing)
- ✅ Enable proactive coaching before outcomes turn bad
- ❌ Wait for shipped features to assess effectiveness
- ❌ Focus only on outcomes without understanding process
- ❌ React to problems instead of predicting them

**Example applications:**
- When delegation patterns degrade (indicator), flag for coaching before the feature ships badly (outcome)
- Track week-over-week improvement in tool sophistication as a leading indicator of future performance
- Identify when someone's patterns match high performers, even before their outcomes catch up

**Decision rule:** For every outcome metric, identify the process metric that predicts it and surface both.

---

### 5. Individual Value First, Then Team, Then Manager

**What it means:** Users must get value from the system before their managers do.

**How it guides decisions:**
- ✅ V1 focuses entirely on personal insights for individuals
- ✅ Team features only after individuals are getting value
- ✅ Manager features build on top of working individual and team systems
- ❌ Build manager dashboards first (no adoption)
- ❌ Require team participation before individual value exists (chicken-egg)
- ❌ Features that only managers want (dead on arrival)

**Example applications:**
- Personal insights work standalone—no team required (individuals get value immediately)
- Team insights require 3+ active users but provide value to those users, not just managers
- Manager coaching features are the last to build (require healthy individual and team usage)

**Decision rule:** Sequence validation: Individual → Team → Manager. Build in this order, deliver value at each stage.

---

### 6. Fair Assessment Accounts for AI Maturity

**What it means:** AI tools are still maturing; outcomes reflect both skill and tool capability.

**How it guides decisions:**
- ✅ Measure process and skill (controllable) separately from outcomes (influenced by AI limits)
- ✅ Context matters—same outcome with different difficulty levels indicates different skill
- ✅ Recognize when someone hit AI limitations vs. their own limitations
- ❌ Judge only on outcomes (unfair when AI had a bad session)
- ❌ Ignore task difficulty or AI capability variations
- ❌ Assume all failures are user skill issues

**Example applications:**
- Show "attempted complexity" alongside "success rate" (tried hard things vs. easy things)
- When errors spike system-wide (AI issue), don't penalize individuals' metrics that day
- Highlight when someone successfully worked around AI limitations (skill indicator)

**Decision rule:** Before comparing performance, ensure comparisons account for task difficulty and AI capability variations.

---

## Technical Principles

How we actually build the system.

### 1. Privacy by Design

**What it means:** User data is protected by architecture, not just policy.

**How it guides decisions:**
- ✅ Personal insights stored locally or in user-controlled storage
- ✅ Team insights require explicit opt-in from all participants
- ✅ Sensitive content (code, prompts) redacted before aggregation
- ❌ Centralized storage of all user data without controls
- ❌ Assume policy will protect privacy (need technical safeguards)
- ❌ Require sharing personal data to get any value

**Example applications:**
- Personal insights work entirely from local session data (no upload required for V1)
- Team insights use aggregated metrics, not raw session logs
- Manager views never expose individual session content without permission

**Decision rule:** If a feature requires sharing personal data, make it opt-in and provide value without it first.

---

### 2. Amplifier Session Data as Source of Truth

**What it means:** Build on Amplifier's existing session infrastructure; don't reinvent data collection.

**How it guides decisions:**
- ✅ Parse events.jsonl, transcript.jsonl, metadata.json (existing Amplifier session files)
- ✅ Use amplifier-session-insights module as data collection layer
- ✅ Extend session data capture if needed, don't replace it
- ❌ Build custom logging infrastructure
- ❌ Require users to instrument their sessions differently
- ❌ Ignore Amplifier's existing session structure

**Example applications:**
- Analytics engine reads from ~/.amplifier/sessions/ or ~/.amplifier/projects/
- Leverage existing session metadata (duration, turn count, model used)
- Extend hooks-session-learning module to capture additional metrics

**Decision rule:** If you're about to build custom data collection, check if Amplifier sessions already provide it.

---

### 3. Incremental Computation

**What it means:** Process new data incrementally, not by recomputing everything.

**How it guides decisions:**
- ✅ Update metrics when new sessions arrive (event-driven)
- ✅ Cache aggregations and update incrementally
- ✅ Enable real-time or near-real-time insights
- ❌ Batch recompute all metrics nightly (slow, wasteful)
- ❌ Force full recalculation on every view
- ❌ Lock users out during processing

**Example applications:**
- When a session ends, update that user's metrics immediately (not on next dashboard load)
- Team metrics recalculate only affected users when data changes
- Growth trends update as sessions arrive, not on-demand

**Decision rule:** If adding a metric requires full recomputation, redesign it to be incremental.

---

### 4. Extensible to Other AI Tools

**What it means:** Architecture should support Amplifier first but allow other AI tool data later.

**How it guides decisions:**
- ✅ Abstract data source layer (Amplifier now, others later)
- ✅ Define common metrics applicable across AI tools
- ✅ Plugin architecture for tool-specific metrics
- ❌ Hard-code Amplifier-specific assumptions throughout
- ❌ Build UI that only works with Amplifier data
- ❌ Assume Amplifier is the only data source forever

**Example applications:**
- Data ingestion layer has "AmplifierSessionReader" but also "SessionReader" interface
- Metrics like "tool usage patterns" work for any AI tool, not just Amplifier
- UI shows "AI tool usage" not "Amplifier usage" (forward-compatible language)

**Decision rule:** When implementing Amplifier-specific features, design the interface to support other tools, even if implementation is Amplifier-only.

---

## Design Principles

How the interface should feel and behave.

### 1. Conversational First, Dashboard Second

**What it means:** Natural language queries within Amplifier are the primary interface, web dashboard is secondary.

**How it guides decisions:**
- ✅ All insights available via conversational prompts ("How am I doing?", "Show team metrics")
- ✅ Web dashboard for deep exploration and visualization
- ✅ Conversational interface integrated into users' existing workflow (Amplifier sessions)
- ❌ Require switching to a separate dashboard for basic questions
- ❌ Build only a web interface
- ❌ Make web dashboard required for any value

**Example applications:**
- User can ask "How's my AI usage this week?" in any Amplifier session and get an answer
- Dashboard provides rich visualizations for when users want to dig deeper
- Tips and insights surface conversationally during work, not requiring context switch

**Decision rule:** If an insight requires opening the dashboard, consider how to surface it conversationally.

---

### 2. Progressive Disclosure

**What it means:** Show the most important insights first, reveal details on demand.

**How it guides decisions:**
- ✅ Summary view shows key metrics and trends at a glance
- ✅ Click/ask to drill into details and raw data
- ✅ Defaults optimized for quick understanding
- ❌ Dump all data and let users figure it out
- ❌ Hide important insights behind multiple clicks
- ❌ Require configuration before showing anything useful

**Example applications:**
- Personal dashboard: Top card shows "growth trajectory" (most important), details below
- Conversational response: "You improved 15% this week [summary]. Ask for details on tool usage, delegation patterns, or tips."
- Manager view: Team health at top, individual details available on request

**Decision rule:** Can a user understand the key insight in 5 seconds? If not, simplify the summary.

---

### 3. Actionable Over Academic

**What it means:** Every insight should suggest what to do next, not just present data.

**How it guides decisions:**
- ✅ Metrics paired with improvement suggestions
- ✅ "You vs. high performers" includes what they do differently
- ✅ Manager coaching views suggest specific interventions
- ❌ Show charts without context or action items
- ❌ Academic analysis that doesn't drive behavior change
- ❌ Data for data's sake

**Example applications:**
- "Your tool usage is below average" + "Try using grep for file searches instead of reading each file"
- "Team's delegation patterns plateaued" + "Share this example of effective delegation from [high performer]"
- Manager view: "Alex's error rate spiking" + "Coaching suggestion: Review error handling patterns together"

**Decision rule:** For every metric displayed, answer "So what?" and "What should I do about it?"

---

## Development Principles

How we work as a team building this.

### 1. Build, Measure, Learn (for AI-First Teams)

**What it means:** We're learning what metrics matter for AI-first teams—iterate quickly based on feedback.

**How it guides decisions:**
- ✅ Ship small increments, validate with real users
- ✅ Expect to evolve metrics as we learn what predicts success
- ✅ Instrument everything to understand what users find valuable
- ❌ Perfect the metrics before shipping
- ❌ Assume we know what matters without validation
- ❌ Build everything before getting feedback

**Example applications:**
- V1 ships basic metrics, learns which users actually look at
- Iterate on "growth indicators" based on which ones correlate with user improvement
- Add metrics incrementally as we validate they matter

**Decision rule:** When unsure if a metric matters, ship it behind a flag and measure if users engage with it.

---

### 2. Documentation-Driven Development

**What it means:** Vision, principles, and epics are written before code.

**How it guides decisions:**
- ✅ This document (PRINCIPLES.md) guides all implementation decisions
- ✅ Epics define features before building them
- ✅ User stories document only what's actually built (no speculative docs)
- ❌ Code first, document later
- ❌ Build features without clear principles
- ❌ Write user stories for planned features (only implemented ones)

**Example applications:**
- Before implementing team insights, write the epic defining what problem it solves
- Use this principles doc to resolve implementation debates
- Create user stories only after features ship (implementation record, not plan)

**Decision rule:** If you can't articulate why a feature aligns with principles, don't build it yet.

---

### 3. Ruthless Simplicity

**What it means:** Prefer simple, obvious implementations over clever, complex ones.

**How it guides decisions:**
- ✅ Simple metrics that users understand
- ✅ Straightforward calculations (no ML unless necessary)
- ✅ Clear, debuggable code
- ❌ Fancy algorithms when simple ones work
- ❌ Abstraction for future flexibility we don't need yet
- ❌ Complexity without clear benefit

**Example applications:**
- Growth metric: Simple week-over-week comparison before trying trend analysis
- Tool sophistication: Count distinct tools used before analyzing usage patterns
- Storage: JSON files before databases (for V1 personal insights)

**Decision rule:** When choosing between simple and clever, choose simple unless complexity solves a real problem.

---

## Anti-Patterns

Patterns that violate our principles and vision.

### ❌ Manager-Only Metrics

**Bad:** Build a dashboard that only managers can see with team member metrics  
**Good:** Team insights visible to all team members; manager views add coaching context, not hidden metrics

**Why it's bad:** Violates "Transparency Builds Trust" and "Growth Over Surveillance"

---

### ❌ Outcome-Only Assessment

**Bad:** Rank team members by features shipped or business impact alone  
**Good:** Show outcomes alongside process quality, growth trajectory, and task difficulty

**Why it's bad:** Violates "Leading Indicators Over Lagging Indicators" and "Fair Assessment Accounts for AI Maturity"

---

### ❌ Traditional Productivity Metrics

**Bad:** Measure lines of code written, hours logged, commits per day  
**Good:** Measure AI delegation effectiveness, tool sophistication, session impact

**Why it's bad:** Violates "Measure AI Collaboration, Not Pre-AI Productivity"

---

### ❌ Surveillance Features

**Bad:** Real-time manager view of who's working and what they're doing  
**Good:** Weekly summary of team patterns with coaching suggestions

**Why it's bad:** Violates "Growth Over Surveillance"

---

### ❌ Manager Value Before User Value

**Bad:** Build manager coaching dashboard in V1 before individuals get personal insights  
**Good:** V1 = personal insights, V2 = team insights, V3 = manager coaching

**Why it's bad:** Violates "Individual Value First, Then Team, Then Manager"

---

### ❌ Opaque Scoring

**Bad:** Calculate a hidden "AI effectiveness score" that managers see but users don't  
**Good:** All metrics visible to users with clear explanations of how they're calculated

**Why it's bad:** Violates "Transparency Builds Trust"

---

### ❌ One-Size-Fits-All Dashboard

**Bad:** Generic analytics dashboard that serves everyone the same way  
**Good:** Three distinct views optimized for each persona's needs (Individual, Team, Manager)

**Why it's bad:** Violates the vision of purpose-built views for each persona

---

## Decision Framework

**When AI faces choices, use these criteria:**

### Priority Hierarchy

1. **Does it drive growth?** - Features must help users improve, not just measure them
2. **Is it transparent?** - Users should see and understand what's being measured
3. **Does it measure AI-first work?** - Metrics must capture AI collaboration, not pre-AI productivity
4. **Is it fair?** - Assessment must account for AI tool limitations and task difficulty
5. **Does it follow the sequence?** - Individual value → Team value → Manager value

---

### Specific Decision Rules

**If considering adding a metric:**
→ YES if it's AI-specific, actionable, and transparent. NO if it's traditional productivity or opaque.

**If considering a manager-only feature:**
→ NO. Redesign to provide value to individuals or be transparent to the team.

**If considering outcome-based ranking:**
→ NO unless paired with process quality, growth trajectory, and difficulty context.

**If considering centralized data storage:**
→ ONLY if users have control and opt-in. Prefer local/edge storage for V1.

**If considering a metric users don't understand:**
→ NO. Simplify or explain until it's transparent.

**If considering building for managers before individuals:**
→ NO. Always validate individual value first.

**If considering a feature that requires team adoption to work:**
→ ONLY if individual value already exists. Team features build on individual usage.

---

## How to Use These Principles

### When Making Product Decisions

1. **Check against principles** - Does this align with our core principles?
2. **Apply decision framework** - What does the decision rule say?
3. **Identify conflicts** - Which principle does this violate (if any)?
4. **Justify exceptions** - Can you explain why breaking the principle is necessary?
5. **Seek simplicity** - Is there a simpler approach that aligns with principles?

### When Reviewing Code

1. **Does it support growth over surveillance?** (Principle 1)
2. **Is it transparent?** (Principle 2)
3. **Is it AI-first?** (Principle 3)
4. **Does it use leading indicators?** (Principle 4)
5. **Does it follow the sequence?** (Principle 5)

### When Adding Features

1. **Does this connect to the vision?** (Check VISION.md)
2. **Does this follow our principles?** (Check this doc)
3. **What does the decision framework say?** (See above)
4. **How do we measure success?** (Check SUCCESS-METRICS.md)
5. **Is this the right sequence?** (Individual → Team → Manager)

---

## Principles Evolve, Vision Doesn't

**These principles will evolve** as we learn from building and users. The vision (what we're building and why) stays stable. Principles (how we build it) improve over time.

**When principles conflict:** Vision wins. If a principle blocks achieving the vision, update the principle.

**When reality conflicts with principles:** Learn from reality. Principles should guide, not constrain learning.

---

## Related Documentation

**Vision folder (strategic context):**
- [VISION.md](VISION.md) - Strategic vision and positioning
- [SUCCESS-METRICS.md](SUCCESS-METRICS.md) - How we measure success *(to be created)*

**Implementation details:**
- [docs/README.md](../README.md) - Epic index
- [Epics](../02-requirements/epics/) - Feature requirements

---

## Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-02-03 | Chris Park | Initial principles document |

---
