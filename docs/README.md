# Amplifier Usage Insights Documentation

A comprehensive analytics system to help individuals, teams, and managers understand performance and growth based on AI tool usage.

---

## 🚀 Quick Links

| Document | Purpose |
|----------|---------|
| [VISION](01-vision/VISION.md) | Problems we're solving, positioning, and roadmap |
| [PRINCIPLES](01-vision/PRINCIPLES.md) | Design principles and decision framework |
| [SUCCESS-METRICS](01-vision/SUCCESS-METRICS.md) | How we measure success |
| [Epics](02-requirements/epics/) | High-level features and capabilities |
| [User Stories](02-requirements/user-stories/) | Detailed implemented features |

---

## 📊 Epic Status

| # | Epic | Status | Description |
|---|------|--------|-------------|
| 01 | [TBD](02-requirements/epics/) | Planning | First epic to be defined |

**Status Legend:** 🔵 Planning | 🟡 In Progress | 🟢 Complete

---

## 📁 Documentation Structure

```
docs/
├── 01-vision/              # Strategic direction and vision
│   ├── VISION.md          # Problems, positioning, roadmap
│   ├── PRINCIPLES.md      # Design principles and decision framework
│   └── SUCCESS-METRICS.md # How we measure success
│
├── 02-requirements/        # What we're building
│   ├── epics/             # High-level features (Epic 01, Epic 02, ...)
│   └── user-stories/      # Detailed user stories derived from epics
│
└── templates/             # Templates for creating new documents
    ├── VISION_TEMPLATE.md
    ├── EPIC_TEMPLATE.md
    ├── USER_STORY_TEMPLATE.md
    ├── PRINCIPLES_TEMPLATE.md
    └── SUCCESS_METRICS_TEMPLATE.md
```

---

## 🎯 Next Steps

The documentation structure is ready. Here's the recommended sequence:

1. **Define the Vision** → Create `01-vision/VISION.md` using the vision template
2. **Establish Principles** → Create `01-vision/PRINCIPLES.md` for design decisions
3. **Set Success Metrics** → Create `01-vision/SUCCESS-METRICS.md` for measurable goals
4. **Break Down Epics** → Create epic files in `02-requirements/epics/`
5. **Derive User Stories** → Create stories in `02-requirements/user-stories/` as features are implemented

---

## 📝 Contributing

### Vision Documents
- **When to update:** Rarely - only when strategic direction shifts
- **Who decides:** Requires broad stakeholder alignment
- **Process:** Discuss → Draft → Review → Commit

### Epics
- **When to create:** During planning phases
- **Format:** Use `templates/EPIC_TEMPLATE.md`
- **Naming:** `XX-descriptive-name.md` (e.g., `01-core-data-foundation.md`)

### User Stories
- **When to create:** ONLY when implementing a feature
- **Format:** Use `templates/USER_STORY_TEMPLATE.md`
- **Naming:** `XX-YY-story-name.md` (e.g., `01-01-session-data-collection.md`)

### Principles & Metrics
- **When to update:** As we learn and evolve
- **Who decides:** Team consensus
- **Process:** Propose → Discuss → Update

---

## 💡 Tips for Navigation

- **New to the project?** Start with [VISION](01-vision/VISION.md)
- **Understanding decisions?** Read [PRINCIPLES](01-vision/PRINCIPLES.md)
- **Measuring impact?** Check [SUCCESS-METRICS](01-vision/SUCCESS-METRICS.md)
- **Building features?** Review relevant [Epics](02-requirements/epics/)
- **Implementation details?** See [User Stories](02-requirements/user-stories/)

---

**Last Updated:** 2026-02-03  
**Documentation Tier:** Standard
