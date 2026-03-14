---
name: forge
description: Extract and compound learnings at session end. Reads rem/CHANGELOG.md, git log, and discoveries to synthesize dated learning files with maturity tracking. Use at end of work sessions to capture knowledge.
---

# Forge: Knowledge Compounding

Extract learnings from the current session and compound them into persistent knowledge.

## Trigger

User runs `/forge` at session end (or any time they want to capture learnings).

## Process

### Step 1: Gather Session Evidence

Read these sources for learning material:

```
1. rem/CHANGELOG.md — what changed this session
2. rem/discoveries/*.md — insights captured by hooks
3. git log --oneline -20 — recent commits
4. git diff --stat HEAD~5 — files changed recently
```

### Step 2: Synthesize Learnings

For each learning, assign a **maturity tag**:

| Tag | Meaning | Criteria |
|-----|---------|----------|
| `NEW` | First observation | Never seen before in INDEX.md |
| `CONFIRMED` | Seen twice | Exists in INDEX.md as NEW |
| `ESTABLISHED` | Proven pattern | Exists as CONFIRMED, or 3+ observations |

### Step 3: Write Daily Learning File

Create `rem/learnings/[YYYY-MM-DD].md`:

```markdown
# Learnings: [YYYY-MM-DD]

Session focus: [brief description of what was worked on]

## Learnings

### 1. [Learning Title] — [NEW|CONFIRMED|ESTABLISHED]

**Context**: [When/where this was observed]
**Insight**: [The actual learning]
**Evidence**: [File, commit, or discovery that proves it]

### 2. [Next Learning] — [TAG]
...

## Upgraded

- [Learning X] upgraded from NEW → CONFIRMED (seen again in [context])

## Summary

- Total learnings: [N]
- New: [N] | Confirmed: [N] | Established: [N]
- Key theme: [one-line summary]
```

### Step 4: Update INDEX.md

Read `rem/learnings/INDEX.md` (create if missing). Update it:

```markdown
# Learning Index

Last updated: [YYYY-MM-DD]
Total learnings: [N]

## By Maturity

### ESTABLISHED
- **[Title]** — [one-line] (confirmed: [date], established: [date])

### CONFIRMED
- **[Title]** — [one-line] (first: [date], confirmed: [date])

### NEW
- **[Title]** — [one-line] (first: [date])

## By Topic

### [Topic 1]
- [Learning] ([maturity])

### [Topic 2]
- [Learning] ([maturity])
```

**Maturity upgrade rules:**
- If a NEW learning appears again → upgrade to CONFIRMED
- If a CONFIRMED learning appears again → upgrade to ESTABLISHED
- Include the date of each transition

### Step 5: Sync to Memento (Cross-Agent Memory)

For each ESTABLISHED or CONFIRMED learning, persist to Memento for cross-agent sharing:

```
Use the Memento MCP `remember` tool:
- topic: learning's topic category (e.g., "debugging", "architecture", "deployment")
- type: "procedure" (for how-to learnings) or "fact" (for observations)
- content: the learning's insight (1-2 sentences)
- importance: ESTABLISHED=0.8, CONFIRMED=0.6
- scope: "permanent"
```

Skip NEW learnings (they haven't been validated yet). Skip if Memento is unavailable.

### Step 6: Report

Print a summary to the user:

```
=== Forge Complete ===

Learnings captured: [N]
  - [N] new, [N] confirmed, [N] established
Upgrades: [N] learnings matured
Memento synced: [N] learnings persisted to cross-agent memory

Written to: rem/learnings/[date].md
Index updated: rem/learnings/INDEX.md
```

## Rules

- ALWAYS read existing INDEX.md before writing to check for maturity upgrades
- NEVER duplicate learnings — upgrade maturity instead
- Keep learning descriptions concise (1-2 sentences)
- Include concrete evidence (file paths, commit hashes, error messages)
- Create `rem/learnings/` directory if it doesn't exist
- If no meaningful learnings found, say so honestly — don't fabricate
- Memento sync is best-effort — don't fail the forge if Memento is unreachable
