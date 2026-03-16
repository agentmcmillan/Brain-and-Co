---
name: memory-decay
description: Compact old sessions using Beads-style memory decay
version: 1.0.0
author: agentmcmillan
homepage: https://github.com/agentmcmillan/Claude-Brain-Care
user-invocable: true
tags:
  - memory
  - maintenance
  - compaction
  - archival
metadata:
  requires:
    config:
      - rem/sessions/
  os:
    - darwin
    - linux
    - windows
---

# Memory Decay: Context Compaction

Automatically compact old Brain-Wave sessions to conserve context tokens.

## What It Does

Implements Beads-style memory decay:
- **< 7 days**: Full detail (unchanged)
- **7-30 days**: Summarized to key points
- **30-90 days**: Minimal (1-line + decisions)
- **> 90 days**: Archived with index

## Usage

```
/memory-decay
```

Or as agent:
```
use memory-decay agent
```

## Why Decay?

AI context windows are finite. Old sessions consume tokens without providing value. Memory decay preserves decisions while freeing context space.

## What's Preserved

| Always Kept | Discarded |
|-------------|-----------|
| Focus area | Verbose descriptions |
| Key decisions | Step-by-step logs |
| Files touched | Intermediate states |
| Outcomes | Redundant context |

## Decay Example

**Original (day 1):**
```markdown
# Session: bw-a1b2c
Date: 2026-01-15

## Current Focus
Working on authentication module...
[50 lines of detail]

## Files Modified
- src/auth/service.ts - Added JWT generation
- src/auth/middleware.ts - Added token validation
[detailed descriptions]

## Decisions Made
After considering options A, B, and C...
[verbose rationale]
```

**After decay (day 14):**
```markdown
# Session: bw-a1b2c [COMPACTED]
> 2026-01-15 | Compacted: 2026-01-29

Focus: Authentication module
Outcome: Completed

## Decisions
- JWT for tokens
- Refresh rotation enabled

## Files
- src/auth/service.ts
- src/auth/middleware.ts
```

**After 60 days:**
```markdown
# bw-a1b2c [MINIMAL]
Auth module: JWT + refresh rotation. Files: auth/service.ts, auth/middleware.ts
```

## Archive Structure

```
rem/
├── sessions/          # Active sessions
├── archive/
│   └── sessions/
│       └── 2026/
│           ├── INDEX.md
│           └── [archived files]
```

## When to Run

- Weekly maintenance
- When `rem/sessions/` exceeds 50 files
- Before major features (free up context)
- After project milestones

## Related Skills

- `rem` - Creates sessions
- `shared-memory` - Exports before archiving
- `brain-wave-init` - Initial setup
