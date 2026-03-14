---
name: inject
description: Load compounded learnings at session start. Reads the learning INDEX.md with freshness decay scoring, presents top learnings and project context. Use at the beginning of work sessions.
---

# Inject: Load Session Knowledge

Load compounded learnings from previous sessions with freshness-weighted scoring.

## Trigger

User runs `/inject` at session start.

## Process

### Step 1: Load Index

Read `rem/learnings/INDEX.md`. If it doesn't exist, report "No learnings captured yet. Use /forge at session end to start building knowledge."

### Step 2: Apply Freshness Decay

Score each learning based on recency and maturity:

| Age | Freshness Weight |
|-----|-----------------|
| Today | 100% |
| This week (1-7 days) | 80% |
| This month (8-30 days) | 50% |
| Older (31+ days) | 30% |

**Maturity bonus:**
- ESTABLISHED: +20% (capped at 100%)
- CONFIRMED: +10% (capped at 100%)
- NEW: +0%

**Final score** = freshness_weight + maturity_bonus (max 100%)

### Step 3: Rank and Select

Sort learnings by final score, descending. Select top 10 (or fewer if less exist).

### Step 4: Load Cross-Agent Knowledge from Memento

Call Memento MCP tools to surface knowledge from other sessions and agents:

1. **`context`** — loads core memory (preferences, errors, procedures)
2. **`recall`** with topic matching the current project name — surfaces project-specific knowledge
3. **`recall`** with type="error" — surfaces recent error patterns to avoid

Merge Memento results with local learnings. Deduplicate by content similarity.
If Memento is unavailable, skip this step silently.

### Step 5: Load Project Context

Check for these files and include if they exist:
- `project-context.md` or `CLAUDE.md` in the working directory
- `rem/restoration/PROTOCOL.md` — last session state
- `rem/LAST-RUN.md` — last session summary

### Step 6: Present to User

```
=== Knowledge Injection ===

## Top Learnings (by relevance)

1. **[Title]** [ESTABLISHED] (score: 95%)
   [One-line insight]

2. **[Title]** [CONFIRMED] (score: 82%)
   [One-line insight]

3. **[Title]** [NEW] (score: 70%)
   [One-line insight]

...

## Session Context

Last session: [date] — [focus area]
Open questions: [from PROTOCOL.md if exists]

## Quick Stats

Total learnings: [N]
- Established: [N] | Confirmed: [N] | New: [N]
Oldest learning: [date]
Last forge: [date]

=== Ready to work ===
```

## Rules

- ONLY read files, never write during inject
- Present learnings concisely — this is a quick briefing, not a deep dive
- If INDEX.md is empty or missing, suggest running /forge first
- Always include the score so user understands ranking
- If project-context.md exists, summarize it in 2-3 lines max
- Freshness is calculated from the learning's LAST observation date, not first
