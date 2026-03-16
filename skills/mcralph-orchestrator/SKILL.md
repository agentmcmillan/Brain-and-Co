---
name: mcralph-orchestrator
description: Master orchestrator that routes tasks to optimal Brain-Wave workflows
version: 1.0.0
author: agentmcmillan
homepage: https://github.com/agentmcmillan/Claude-Brain-Care
user-invocable: true
tags:
  - orchestration
  - routing
  - master
  - unified
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

# McRalph: Unified Brain-Wave Command Center

Intelligently routes tasks to the optimal Brain-Wave workflow.

## What It Does

- Analyzes task requirements
- Routes to best workflow (Bart/Ralph, GSD, Planning)
- Maintains unified memory across systems
- Chains workflows for complex tasks
- Reports Brain-Wave integration status

## Usage

Describe your task and McRalph routes it:
```
/mcralph "add user authentication"
```

Or as agent:
```
use mcralph-orchestrator agent
```

## Available Systems

| System | Best For |
|--------|----------|
| **Bart/Ralph** | Story-based features |
| **GSD** | Complex multi-phase projects |
| **Planning** | Research and exploration |
| **Brain-Wave** | Memory refresh |

## Routing Logic

### → Bart/Ralph
- "Add a feature..."
- "Build me..."
- "Implement..."
- Clear scope, definable stories

### → GSD
- "Refactor the entire..."
- "Migrate from X to Y..."
- Heavy research, parallel execution

### → Planning
- "Figure out why..."
- "Investigate..."
- "Explore..."
- Unknown scope, research-heavy

### → Brain-Wave
- "What do you know about..."
- "Refresh your memory..."
- Context seems stale

## Workflow Patterns

### Pattern 1: Feature Development
```
Bart (plan) → Ralph (execute) → REM (sync)
```

### Pattern 2: Major Refactor
```
GSD Research → GSD Planning → GSD Execution → REM
```

### Pattern 3: Investigation
```
Planning → (findings) → Bart/Ralph (if solution)
```

### Pattern 4: Chained
```
Planning (investigate) → Bart (plan) → Ralph (execute) → REM
```

## Example

```
User: Add payment system with Stripe

=== McRalph Orchestrator ===

Loading Brain-Wave...
✓ 47 files indexed
✓ Architecture mapped
✓ 5 discoveries

Task Assessment:
- Scope: New feature (multiple components)
- Clarity: Medium (needs requirements)
- Complexity: Medium-High (external API)
- Best fit: Bart/Ralph with GSD research

Recommended Workflow:
┌─────────────────────────────────────┐
│ 1. GSD Research (Stripe patterns)  │
│ 2. Bart Planning (with research)   │
│ 3. Ralph Execution (with context)  │
│ 4. REM Sync (capture learnings)    │
└─────────────────────────────────────┘

Brain-Wave context available:
- API patterns: REST + Express
- DB patterns: Prisma ORM
- Known: Rate limiting needed

Proceed with this workflow?
```

## Memory-Aware Sizing

McRalph uses Brain-Wave for accurate task sizing:

```markdown
## Complexity Assessment

From alpha-wave/summaries/:
- [file]: [lines], [complexity]

From beta-wave/_CONNECTIONS.md:
- [file]: [N] dependents (high impact)

From rem/discoveries/issues.md:
- Known issue in [area] (add buffer)

Estimated: M
Recommended: Bart/Ralph
```

## When to Use

- Unsure which workflow fits
- Complex tasks needing routing
- Want intelligent orchestration
- Need unified memory across systems

## Related Skills

- `bart-enhanced` - Feature planning
- `ralph-enhanced` - Story execution
- `gsd-orchestrator` - Multi-phase work
- `planning-enhanced` - Research tasks
