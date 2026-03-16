---
name: beta-wave
description: Deep knowledge mapper - creates nested architecture maps and dependency graphs
version: 1.0.0
author: agentmcmillan
homepage: https://github.com/agentmcmillan/Claude-Brain-Care
user-invocable: true
tags:
  - memory
  - architecture
  - mapping
  - dependencies
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

# Beta-Wave: Deep Knowledge Mapper

Creates detailed architecture maps that capture institutional knowledge about your codebase.

## What It Does

- Reads Alpha-Wave's index
- Creates `_MAP.md` for each directory
- Builds dependency graph in `_CONNECTIONS.md`
- Documents patterns in `_PATTERNS.md`
- Infers design decisions in `_DECISIONS.md`

## Prerequisites

Alpha-Wave must run first:
```
use alpha-wave agent
```

## Usage

```
/beta-wave
```

Or as agent:
```
use beta-wave agent
```

## Output Structure

```
beta-wave/
├── _MAP.md            # Root architecture overview
├── _CONNECTIONS.md    # Dependency graph
├── _PATTERNS.md       # Code patterns observed
├── _DECISIONS.md      # Inferred design decisions
├── connections/       # Per-module deps
├── patterns/          # Pattern details
└── [directory]/
    └── _MAP.md        # Per-directory map
```

## Architecture Diagrams

Beta-Wave creates ASCII diagrams:
```
┌─────────┐     ┌─────────┐
│   API   │────▶│  Core   │
└─────────┘     └─────────┘
      │               │
      ▼               ▼
┌─────────────────────────┐
│        Database         │
└─────────────────────────┘
```

## When to Run

- After Alpha-Wave completes
- After major restructuring
- When architecture feels unclear
- Before large refactors

## Token Efficiency

- Root map: max 30 lines
- Directory maps: max 20 lines
- Uses ASCII diagrams sparingly
- Links to details vs inline

## Integration

Updates `CLAUDE.md` to import:
```markdown
@beta-wave/_MAP.md
@beta-wave/_CONNECTIONS.md
```

## Related Skills

- `alpha-wave` - Must run first
- `rem` - Keeps maps synced
- `brain-wave-init` - Full setup
