---
name: planning-enhanced
description: Manus-style persistent markdown planning with Brain-Wave sync
version: 1.0.0
author: agentmcmillan
homepage: https://github.com/agentmcmillan/Claude-Brain-Care
user-invocable: true
tags:
  - planning
  - research
  - markdown
  - persistent
metadata:
  requires:
    bins:
      - git
    config:
      - alpha-wave/INDEX.md
  os:
    - darwin
    - linux
    - windows
---

# Planning Enhanced: Brain-Wave Integrated

Manus-style persistent markdown planning with automatic Brain-Wave synchronization.

## What It Does

- Creates persistent planning files
- Pre-populates with Brain-Wave context
- References indexed files in plans
- Syncs findings to REM discoveries
- Captures session state automatically

## Usage

```
/planning-with-files "investigate auth slowness"
```

Or as agent:
```
use planning-enhanced agent
```

## Planning Files

### task_plan.md
```markdown
# Task Plan: [Title]
> Brain-Wave Context: Loaded ✓

## Brain-Wave References
- Index: @alpha-wave/INDEX.md
- Architecture: @beta-wave/_MAP.md

## Relevant Files
[Auto-populated from index]

## Phases
### Phase 1: [Name]
- [ ] Task 1.1
  - Files: [from index]
  - Pattern: [from patterns]
```

### findings.md
```markdown
# Findings: [Task]
> Syncs to: rem/discoveries/planning.md

## From Brain-Wave (Pre-loaded)
[Prior discoveries]

## New Discoveries
#### [timestamp] - [Finding]
- **Context**: [what investigated]
- **Discovery**: [what found]
- **Sync Status**: [ ] Synced to REM
```

### progress.md
```markdown
# Progress: [Task]
> Syncs to: rem/sessions/planning-[timestamp].md

## Session Log
### [timestamp] - Session Start
- Brain-Wave context loaded
- Focus: [current work]
```

## Bidirectional Sync

### Brain-Wave → Planning
```
alpha-wave/INDEX.md → task_plan.md (file refs)
beta-wave/_MAP.md → task_plan.md (architecture)
rem/discoveries/ → findings.md (prior knowledge)
```

### Planning → Brain-Wave
```
findings.md → rem/discoveries/planning.md
progress.md → rem/sessions/planning-[timestamp].md
new patterns → suggest beta-wave update
```

## Example

```
/planning-with-files for adding user profiles

=== Planning with Brain-Wave ===

Loading context...
✓ 47 files indexed
✓ Architecture mapped
✓ 3 prior insights

Relevant for "user profiles":
- Existing: src/models/user.ts
- Pattern: Prisma models in src/models/
- Prior: Auth module works well

Creating planning files...

.planning/task_plan.md
├─ Brain-Wave references included
├─ Relevant files pre-populated
└─ Created ✓

.planning/findings.md
├─ Prior discoveries loaded
└─ Created ✓

.planning/progress.md
├─ Session template ready
└─ Created ✓

Ready! Findings will sync to rem/discoveries/
```

## When to Use

- Exploratory research
- Uncertain scope tasks
- Investigation work
- Documentation-heavy planning
- Long-running research

## On Completion

Files auto-sync to Brain-Wave:
1. Findings → `rem/discoveries/planning.md`
2. Progress → `rem/sessions/planning-[timestamp].md`
3. Updates → `rem/restoration/PROTOCOL.md`

## Related Skills

- `bart-enhanced` - Story-based planning
- `rem` - Receives planning discoveries
- `mcralph-orchestrator` - Routes to this for research
