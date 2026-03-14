---
paths:
  - "**/*"
---

# Brain-Wave Memory System

This project uses a three-agent memory system for persistent context across sessions.

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

## Key Files to Import

For automatic context loading, these files integrate with Claude's memory:
- `@alpha-wave/INDEX.md` - Quick file reference
- `@beta-wave/_MAP.md` - Architecture overview
- `@rem/restoration/PROTOCOL.md` - How to restore context
