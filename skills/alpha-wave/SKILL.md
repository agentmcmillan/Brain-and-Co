---
name: alpha-wave
description: Knowledge indexer - builds file indexes, topic trees, and summaries
version: 1.0.0
author: agentmcmillan
homepage: https://github.com/agentmcmillan/Claude-Brain-Care
user-invocable: true
tags:
  - memory
  - indexing
  - summaries
  - productivity
metadata:
  requires:
    bins:
      - git
  os:
    - darwin
    - linux
    - windows
---

# Alpha-Wave: Knowledge Indexer

Creates comprehensive file indexes and summaries for instant codebase understanding.

## What It Does

- Scans repository structure
- Creates `INDEX.md` with file categorization
- Generates `TOPICS.md` with cross-references
- Writes per-file summaries in `summaries/`
- Installs memory hooks in `.claude/rules/`

## Usage

```
/alpha-wave
```

Or as agent:
```
use alpha-wave agent
```

## Output Structure

```
alpha-wave/
├── INDEX.md           # Overview (~50 lines)
├── index/             # Detailed by category
│   ├── core.md
│   ├── source.md
│   └── config.md
├── TOPICS.md          # Topic overview
├── topics/            # Per-topic details
├── summaries/         # Per-file summaries
└── STATE.md           # Sync checkpoint
```

## Token Efficiency

Alpha-Wave is optimized for minimal token usage:
- Index files: max 50 lines
- Summaries: max 30 lines
- Skips generated/config files
- Uses tables over prose

## When to Run

- First time setup (via `brain-wave-init`)
- After major refactoring
- When files seem outdated
- Before starting large features

## Progress Output

```
[alpha-wave] Phase 2/7: Index Creation
  → Building INDEX.md...
  ✓ Created alpha-wave/INDEX.md
```

## Integration

After running, `CLAUDE.md` is updated to import:
```markdown
@alpha-wave/INDEX.md
@alpha-wave/TOPICS.md
```

These auto-load in every session.

## Related Skills

- `brain-wave-init` - Full system setup
- `beta-wave` - Deep mapping (runs after alpha)
- `rem` - Ongoing sync
