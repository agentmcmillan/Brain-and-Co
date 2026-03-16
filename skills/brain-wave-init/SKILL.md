---
name: brain-wave-init
description: Initialize the complete Brain-Wave memory system for persistent AI context
version: 1.0.0
author: agentmcmillan
homepage: https://github.com/agentmcmillan/Claude-Brain-Care
user-invocable: true
tags:
  - memory
  - context
  - initialization
  - productivity
metadata:
  requires:
    bins:
      - git
    config:
      - .claude/settings.json
  os:
    - darwin
    - linux
    - windows
---

# Brain-Wave Initializer

Initialize the complete Brain-Wave memory system for persistent AI context across sessions.

## What It Does

Sets up a three-agent memory pipeline:
1. **Alpha-Wave** - Indexes all files, creates summaries
2. **Beta-Wave** - Maps architecture and dependencies
3. **REM** - Monitors changes, maintains sessions

## Usage

```
/brain-wave-init
```

Or invoke as agent:
```
use brain-wave-init agent
```

## Options

| Option | Description |
|--------|-------------|
| `fresh` | Remove existing Brain-Wave folders and start clean |
| `repair` | Fix incomplete installation |

## Permission Modes

During setup, choose how agents handle permissions:

| Mode | Behavior |
|------|----------|
| `bypassPermissions` | No prompts - fully autonomous |
| `acceptEdits` | Auto-accept files, prompt for bash |
| `default` | Prompt for everything |

## Output Structure

```
project/
├── alpha-wave/      # File index and summaries
├── beta-wave/       # Architecture maps
├── rem/             # Session tracking
└── .claude/
    ├── agents/      # Agent definitions
    └── rules/       # Auto-loaded context
```

## Progress Indicators

The initializer outputs progress:
```
[brain-wave-init] Phase 2/7: Alpha-Wave
  → Indexing files...
  ✓ Created alpha-wave/INDEX.md
```

## After Installation

Context auto-loads on every session via `.claude/rules/` memory hooks.

Run `use rem agent` periodically to keep everything synced.

## Requirements

- Git repository (recommended)
- Claude Code CLI
- Write access to project directory

## Related Skills

- `alpha-wave` - Manual indexing
- `beta-wave` - Manual mapping
- `rem` - Manual sync
