---
name: bart-enhanced
description: Brain-Wave enhanced feature planner with codebase context
version: 1.0.0
author: agentmcmillan
homepage: https://github.com/agentmcmillan/Claude-Brain-Care
user-invocable: true
tags:
  - planning
  - features
  - prd
  - stories
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

# Bart Enhanced: Brain-Wave Feature Planner

Plan features with full codebase context from Brain-Wave memory.

## What It Does

- Loads Brain-Wave context before research
- Skips re-scanning indexed files
- References existing patterns and architecture
- Creates PRDs with Brain-Wave context embedded
- Feeds discoveries back to REM

## Usage

```
/bart new           # Start new feature planning
/bart research      # Research with indexed context
/bart requirements  # Define requirements
/bart create-prd    # Generate PRD with context
```

Or as agent:
```
use bart-enhanced agent
```

## Brain-Wave Integration

### Before (Standard Bart)
- Scans entire codebase from scratch
- No pattern awareness
- Fresh research every time

### After (Enhanced)
- Loads `alpha-wave/INDEX.md` - knows all files
- Reads `beta-wave/_PATTERNS.md` - follows conventions
- Checks `rem/discoveries/` - learns from history
- Only researches what's NEW

## PRD Enhancement

Stories include Brain-Wave context:
```json
{
  "id": "US-001",
  "brainWaveContext": {
    "relevantMaps": ["beta-wave/src/_MAP.md"],
    "knownPatterns": ["Repository pattern"],
    "warnings": ["Rate limiting needed"]
  }
}
```

## Discovery Capture

After planning, Bart writes to:
- `rem/discoveries/planning.md` - insights gained
- `rem/sessions/bart-[timestamp].md` - session state

## Example

```
/bart new

Loading Brain-Wave context...
✓ 47 files indexed
✓ Architecture mapped
✓ 3 prior insights loaded

I see this is a TypeScript/Express project using:
- Prisma ORM (src/db/)
- REST API (src/api/)
- Repository pattern throughout

Prior discoveries note:
- Auth module needs refactoring

What feature would you like to plan?
```

## When to Use

- Starting new features
- Planning with architecture awareness
- Creating informed user stories
- Building context-rich PRDs

## Related Skills

- `ralph-enhanced` - Executes Bart's PRDs
- `brain-wave-init` - Provides the context
- `rem` - Captures planning discoveries
