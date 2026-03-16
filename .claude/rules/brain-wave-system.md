---
paths:
  - "**/*"
---

# Brain-Wave Memory System

This project uses a three-agent memory system for persistent context across sessions.

## File Size Rules

**CRITICAL**: All Brain-Wave files must stay small to avoid token limits.

| File Type | Target | Maximum |
|-----------|--------|---------|
| Index files | 50 lines | 100 lines |
| Topic files | 50 lines | 100 lines |
| Summaries | 50 lines | 100 lines |
| Maps | 100 lines | 200 lines |
| Sessions | 30 lines | 50 lines |
| Discoveries | 50 lines | 100 lines |

**When files grow too large:**
1. Split into subdirectory with multiple smaller files
2. Create an `_INDEX.md` that links to the parts
3. Archive old content (sessions, changelog entries)

## The Agents

### Alpha-Wave (Indexer)
Creates file indexes, topic trees, and summaries.
- **Output**: `alpha-wave/` folder
- **Invoke**: `use alpha-wave agent`
- **Run first** when starting a new project

### Beta-Wave (Mapper)
Creates deep nested knowledge maps mirroring directory structure.
- **Output**: `beta-wave/` folder
- **Invoke**: `use beta-wave agent`
- **Requires**: Alpha-Wave to run first

### REM (Monitor)
Background agent that keeps everything synchronized.
- **Output**: `rem/` folder with sessions and discoveries
- **Invoke**: `use rem agent`
- **Run periodically** or after significant changes

## Context Restoration Protocol

### Quick Start (New Session)
1. Check `rem/restoration/PROTOCOL.md` for current state
2. Read `rem/sessions/` latest file for where we left off
3. Read `alpha-wave/INDEX.md` for file overview

### Deep Dive (Specific Area)
1. Read `beta-wave/[area]/_MAP.md` for that directory
2. Read `alpha-wave/summaries/[file]-summary.md` for file details
3. Check `rem/discoveries/` for insights about that area

### Full Restore (After Long Break)
1. Read `rem/restoration/PROTOCOL.md`
2. Read `beta-wave/_MAP.md` for architecture overview
3. Read `beta-wave/_CONNECTIONS.md` for dependencies
4. Read `rem/discoveries/` for accumulated knowledge

## Memory Locations

| Location | Purpose | Updated By |
|----------|---------|------------|
| `alpha-wave/INDEX.md` | File listing | Alpha-Wave, REM |
| `alpha-wave/TOPICS.md` | Topic cross-refs | Alpha-Wave, REM |
| `alpha-wave/summaries/` | File summaries | Alpha-Wave, REM |
| `beta-wave/_MAP.md` | Architecture | Beta-Wave, REM |
| `beta-wave/_CONNECTIONS.md` | Dependencies | Beta-Wave, REM |
| `beta-wave/[dir]/_MAP.md` | Directory maps | Beta-Wave, REM |
| `rem/sessions/` | Session states | REM |
| `rem/discoveries/` | Insights | REM |
| `rem/restoration/PROTOCOL.md` | Restore guide | REM |

## Workflow

```
New Project:
  1. use alpha-wave agent    → Creates index + summaries
  2. use beta-wave agent     → Creates deep maps
  3. use rem agent           → Initializes monitoring

Ongoing Work:
  1. Work on code normally
  2. Periodically: use rem agent  → Syncs everything

New Session:
  1. Read rem/restoration/PROTOCOL.md
  2. Continue where you left off
```

## Background Execution

**IMPORTANT**: Brain-Wave agents should run in background to allow continued interaction.

When invoking any Brain-Wave agent, always use `run_in_background: true`:

```
Task tool invocation:
  subagent_type: alpha-wave (or beta-wave, rem, brain-wave-init)
  run_in_background: true
  prompt: "Index the repository"
```

### Monitoring Background Agents

When an agent runs in background:
1. Task tool returns an `output_file` path
2. Use `tail -f <output_file>` to watch live progress
3. Look for `[agent-name] Phase X/X: Complete ✓` to know it's done
4. Use `Read` tool to check final output

### Progress Indicators

Each agent outputs progress as it works:
```
[alpha-wave] Phase 2/7: Index Creation
  → Building INDEX.md...
  ✓ Created alpha-wave/INDEX.md
```

## Key Files to Import

For automatic context loading, these files integrate with Claude's memory:
- `@alpha-wave/INDEX.md` - Quick file reference
- `@beta-wave/_MAP.md` - Architecture overview
- `@rem/restoration/PROTOCOL.md` - How to restore context
