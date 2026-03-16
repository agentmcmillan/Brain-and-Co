---
name: gsd-orchestrator
description: Get-Shit-Done orchestrator with Brain-Wave integration for complex projects
version: 1.0.0
author: agentmcmillan
homepage: https://github.com/agentmcmillan/Claude-Brain-Care
user-invocable: true
tags:
  - orchestration
  - execution
  - multi-phase
  - parallel
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

# GSD Orchestrator: Brain-Wave Enhanced

Coordinate complex multi-phase development with full codebase context.

## What It Does

- Loads Brain-Wave context before any work
- Runs delta research (only unknown areas)
- Sizes tasks using known complexity
- Executes with pattern compliance
- Verifies against architecture
- Consolidates all learnings to REM

## Usage

```
/gsd "migrate from REST to GraphQL"
```

Or as agent:
```
use gsd-orchestrator agent
```

## Pipeline Comparison

### Standard GSD
```
Research → Plan → Execute → Verify
(each starts cold)
```

### Brain-Wave Enhanced
```
Load Brain-Wave → Delta Research → Informed Planning →
Context-Rich Execution → Pattern Verification → REM Sync
```

## Agent Enhancement

### Research (Delta Only)
```markdown
## Pre-loaded (from Brain-Wave)
- Files: [skip scanning these]
- Architecture: [skip analyzing this]
- Patterns: [verify these hold]

## Research Focus
Only investigate what's NOT in Brain-Wave
```

### Planning (Informed)
```markdown
## Brain-Wave Planning Context

### File Complexity (from summaries)
| File | Lines | Complexity |
|------|-------|------------|

### Architectural Constraints
- [from _DECISIONS.md]

### High-Risk Areas
- [files with many dependents]
```

### Execution (Pattern-Aware)
```markdown
## Brain-Wave Execution Context

### Files to Modify
[specific paths with summaries]

### Patterns to Follow
- [pattern 1]: [how to apply]

### Watch Out For
- [known gotchas]
```

## Example

```
/gsd "add payment system with Stripe"

=== GSD Orchestrator with Brain-Wave ===

Loading context...
✓ 47 files indexed
✓ Architecture mapped
✓ 5 prior discoveries

Brain-Wave indicates:
- No existing payment code
- API pattern: REST + Express
- DB pattern: Prisma ORM
- Known: Rate limiting needed

Phase 1: Delta Research
├─ Skip: General architecture
├─ Research: Payment patterns
└─ Research: PCI compliance

Phase 2: Informed Planning
├─ Complexity from summaries
├─ Integration from connections
└─ Constraints from decisions

Phase 3: Context-Rich Execution
├─ Task 1: Payment model (Prisma pattern)
├─ Task 2: Payment service (DI pattern)
├─ Task 3: Payment routes (REST pattern)

Phase 4: Verification
├─ Pattern compliance: ✓
├─ Architecture compliance: ✓
└─ Dependencies checked: ✓

=== Complete ===
Discoveries captured: 4
Recommend: 'use rem agent' to sync
```

## When to Use

- Complex, multi-phase projects
- System-wide refactors
- Heavy research requirements
- Parallel execution beneficial
- Migration projects

## Related Skills

- `bart-enhanced` - Simpler feature planning
- `ralph-enhanced` - Story execution
- `mcralph-orchestrator` - Intelligent routing
