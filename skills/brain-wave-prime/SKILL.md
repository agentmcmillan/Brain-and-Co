---
name: brain-wave-prime
description: Master coordinator for sub-agents and agent teams with Brain-Wave memory
version: 1.0.0
author: agentmcmillan
homepage: https://github.com/agentmcmillan/Claude-Brain-Care
user-invocable: true
tags:
  - orchestration
  - coordination
  - prime
  - teams
metadata:
  requires:
    bins:
      - git
    config:
      - alpha-wave/INDEX.md
      - beta-wave/_MAP.md
      - rem/restoration/PROTOCOL.md
  os:
    - darwin
    - linux
    - windows
---

# Brain-Wave Prime: Master Coordinator

Coordinate multiple agents with shared Brain-Wave memory.

## What It Does

- Loads full Brain-Wave context on startup
- Routes tasks to specialized sub-agents
- Leads agent teams for collaborative work
- Consolidates all discoveries to REM
- Maintains unified memory across agents

## Usage

As prime agent:
```
use brain-wave-prime agent
```

For sub-agent orchestration:
```
/prime "add user authentication"
→ Routes to bart (planning) → ralph (execution) → rem (sync)
```

For agent team:
```
/prime team "design payment system"
→ Creates team with specialized teammates
→ Coordinates via shared task list
```

## Coordination Modes

### Sub-Agent Mode
```
Prime
├── alpha-wave (index) ─────┐
├── beta-wave (map) ────────┼── Results to Prime
├── bart (plan) ────────────┤
└── ralph (execute) ────────┘
        │
        ▼
    rem (consolidate)
```

### Agent Team Mode
```
Prime (Lead)
├── Teammate A ←──────────┐
├── Teammate B ←──────────┼── Message each other
└── Teammate C ←──────────┘
        │
        ▼
    Shared Task List (rem/tasks/)
```

## When to Use Each

| Scenario | Mode |
|----------|------|
| Index codebase | Sub-agents |
| Plan feature | Sub-agents |
| Execute stories | Sub-agents |
| Complex research | Agent Team |
| Cross-layer work | Agent Team |
| Architecture design | Agent Team |

## Context Injection

Prime injects Brain-Wave context into all agents:

```markdown
## Brain-Wave Context
- Index: @alpha-wave/INDEX.md
- Architecture: @beta-wave/_MAP.md
- Patterns: @beta-wave/_PATTERNS.md
- Tasks: @rem/tasks/tasks.jsonl
```

## Task List Integration

Uses beads-style task tracking:
```jsonl
{"id":"bw-abc12","title":"Design auth","status":"open"}
{"id":"bw-def34","title":"Implement auth","blocked_by":["bw-abc12"]}
```

Prime routes unblocked tasks to appropriate agents.

## Discovery Consolidation

After work completes:
1. Collect discoveries from agents
2. Write to `rem/discoveries/`
3. Update `rem/sessions/`
4. Note files needing re-index

## Example

```
/prime "add payment integration with Stripe"

[brain-wave-prime] Loading context...
  ✓ 47 files indexed
  ✓ Architecture mapped
  ✓ No existing payment code

[brain-wave-prime] Analysis:
  - Scope: New feature
  - Complexity: Medium-High
  - Route: Bart → Ralph → REM

[brain-wave-prime] Spawning bart-enhanced...
  → PRD created with 5 stories

[brain-wave-prime] Spawning ralph-enhanced...
  → Story 1/5: Add payment model ✓
  → Story 2/5: Add Stripe service ✓
  ...

[brain-wave-prime] Spawning rem...
  → Session captured
  → Discoveries logged

[brain-wave-prime] Complete
  Files changed: 8
  Discoveries: 3
  Run 'use rem agent' to verify sync
```

## Related Skills

- `mcralph-orchestrator` - Alternative routing
- `gsd-orchestrator` - Multi-phase projects
- `shared-memory` - Cross-instance sync
