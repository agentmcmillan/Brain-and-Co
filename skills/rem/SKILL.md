---
name: rem
description: Repository Evolution Monitor - syncs memory and tracks sessions
version: 1.0.0
author: agentmcmillan
homepage: https://github.com/agentmcmillan/Claude-Brain-Care
user-invocable: true
tags:
  - memory
  - sync
  - sessions
  - monitoring
metadata:
  requires:
    bins:
      - git
    config:
      - alpha-wave/INDEX.md
      - beta-wave/_MAP.md
  os:
    - darwin
    - linux
    - windows
---

# REM: Repository Evolution Monitor

Background agent that keeps Brain-Wave memory synchronized and captures session state.

## What It Does

- Detects file changes since last run
- Updates Alpha-Wave indexes for changed files
- Updates Beta-Wave maps for structural changes
- Captures current session state
- Logs discoveries and insights
- Maintains restoration protocols

## Usage

```
/rem
```

Or as agent:
```
use rem agent
```

Run periodically during development to keep memory fresh.

## Output Structure

```
rem/
├── CHANGELOG.md           # Recent updates
├── LAST-RUN.md            # Last sync status
├── sessions/
│   └── [timestamp].md     # Session snapshots
├── chats/
│   └── [timestamp].md     # Chat summaries
├── discoveries/
│   ├── architecture.md    # Structural insights
│   ├── conventions.md     # Naming patterns
│   └── issues.md          # Known problems
└── restoration/
    └── PROTOCOL.md        # How to restore context
```

## Four Persistence Layers

1. **Session State** - Current focus, active questions
2. **Semantic Indices** - Cross-references, entities
3. **Discovery Logs** - Accumulated insights
4. **Restoration Protocols** - How to rebuild context

## When to Run

- After completing features
- Before ending work session
- When context feels stale
- After other agents complete

## Restoration Protocol

On new session, REM's protocol guides context restoration:

**Quick Restore** (< 1 min):
1. Read latest session
2. Read INDEX.md

**Full Restore** (< 3 min):
1. Quick steps
2. Read architecture maps
3. Read discoveries

## Chat Summary

REM captures conversation summaries:
```markdown
## Intention
What the user wanted

## Execution
What was done

## Issues
Problems hit

## Outcome
Success/Partial/Failed
```

## Related Skills

- `alpha-wave` - Index source
- `beta-wave` - Map source
- `brain-wave-init` - Full setup
