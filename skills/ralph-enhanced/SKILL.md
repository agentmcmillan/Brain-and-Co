---
name: ralph-enhanced
description: Brain-Wave enhanced story executor with pattern-aware implementation
version: 1.0.0
author: agentmcmillan
homepage: https://github.com/agentmcmillan/Claude-Brain-Care
user-invocable: true
tags:
  - execution
  - stories
  - implementation
  - workers
metadata:
  requires:
    bins:
      - git
    config:
      - prd.json
      - alpha-wave/INDEX.md
      - beta-wave/_MAP.md
  os:
    - darwin
    - linux
    - windows
---

# Ralph Enhanced: Brain-Wave Story Executor

Execute user stories with full codebase context and pattern awareness.

## What It Does

- Loads Brain-Wave context before execution
- Injects context into worker prompts
- Follows established patterns automatically
- Captures learnings after each story
- Updates REM with discoveries

## Usage

```
/ralph
```

Or as agent:
```
use ralph-enhanced agent
```

Requires `prd.json` from Bart planning.

## Brain-Wave Integration

### Standard Worker Prompt
```
Implement US-001: Add user authentication
```

### Enhanced Worker Prompt
```markdown
## Brain-Wave Context

### Relevant Files (from alpha-wave)
- src/auth/index.ts
- src/auth/middleware.ts

### Architecture (from beta-wave)
Pattern: Repository with dependency injection

### Known Issues (from rem/discoveries)
- JWT refresh needs improvement

---

## Your Task
Implement US-001: Add user authentication
```

## Execution Loop

For each story in `prd.json`:
1. Gather Brain-Wave context for story
2. Build enhanced worker prompt
3. Spawn worker with context
4. Capture worker learnings
5. Update `rem/discoveries/execution.md`

## Learning Capture

After each story:
```markdown
## [timestamp] - Story US-001

### Files Modified
- src/auth/service.ts

### Patterns Applied
- Repository pattern

### Discoveries
- bcrypt timing mitigation added

### For Future Reference
- Rate limiting still needed
```

## Example

```
/ralph

Loading Brain-Wave context...
✓ File index loaded
✓ Connections mapped
✓ 5 patterns noted

Reading prd.json... 3 stories found

Starting US-001: Add authentication
├─ Relevant: src/auth/, src/models/user.ts
├─ Patterns: Repository, DI, async/await
├─ Warnings: JWT refresh care (from discoveries)
└─ Spawning worker with context...

US-001 Complete ✓
├─ Files: 3 changed
├─ Discovery: timing attack mitigation
└─ Updated rem/discoveries/

Recommend: 'use rem agent' to sync
```

## When to Use

- After Bart creates `prd.json`
- Executing planned features
- Pattern-compliant implementation
- Building with context awareness

## Related Skills

- `bart-enhanced` - Creates the PRDs
- `rem` - Captures execution learnings
- `gsd-orchestrator` - Complex multi-phase work
