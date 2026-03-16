---
name: beads-tasks
description: Git-backed task tracking with dependency graphs and ready-task detection
version: 1.0.0
author: agentmcmillan
homepage: https://github.com/agentmcmillan/Claude-Brain-Care
user-invocable: true
tags:
  - tasks
  - dependencies
  - tracking
  - beads
metadata:
  requires:
    bins:
      - git
  os:
    - darwin
    - linux
    - windows
---

# Beads Tasks: Dependency-Aware Task Tracking

Git-backed task management inspired by [Beads](https://github.com/steveyegge/beads).

## What It Does

- Hash-based IDs (`bw-a1b2c`) prevent merge conflicts
- Dependency graphs track what blocks what
- Auto-detect "ready" tasks (no open blockers)
- JSONL format for easy git merging

## Usage

```
/tasks              # List all tasks
/tasks ready        # Show tasks ready to work
/tasks add [title]  # Create new task
/tasks done [id]    # Mark complete
/tasks block [id] [blocker]  # Add dependency
```

Or as agent:
```
use beads-tasks agent
```

## Task Format

```json
{
  "id": "bw-a1b2c",
  "title": "Add authentication",
  "status": "open",
  "blocked_by": [],
  "blocks": ["bw-d3e4f"]
}
```

## Ready Detection

A task is **ready** when:
- Status is `open`
- All tasks in `blocked_by` are `done`

```
/tasks ready

Ready to work:
→ bw-a1b2c: Add auth module
→ bw-x1y2z: Update README

Blocked:
→ bw-d3e4f: Add API (waiting on bw-a1b2c)
```

## Dependency Visualization

```
bw-a1b2c (Add auth)
    ↓ blocks
bw-d3e4f (Add API routes)
    ↓ blocks
bw-g5h6i (Add frontend)
```

## Why Hash IDs?

Traditional: `task-001.md`, `task-002.md`
- Merge conflicts when multiple agents create tasks
- Sequential numbers collide

Beads-style: `bw-a1b2c`, `bw-d3e4f`
- Hash-based, globally unique
- No conflicts in multi-agent scenarios
- Short enough for conversation

## Storage

```
rem/tasks/
├── tasks.jsonl      # Active tasks
├── archive.jsonl    # Completed (older)
└── INDEX.md         # Human overview
```

## Integration

Works with Brain-Wave agents:
- **bart-enhanced**: Creates tasks from PRD
- **ralph-enhanced**: Marks tasks done
- **planning-enhanced**: Tracks research tasks

## Example Workflow

```
# Plan creates tasks
/bart create-prd
→ Created bw-a1b2c: Add user model
→ Created bw-d3e4f: Add auth service (blocked by bw-a1b2c)
→ Created bw-g5h6i: Add auth routes (blocked by bw-d3e4f)

# Check what's ready
/tasks ready
→ bw-a1b2c: Add user model

# Complete and check again
/tasks done bw-a1b2c
→ Completed bw-a1b2c
→ Unblocked: bw-d3e4f

/tasks ready
→ bw-d3e4f: Add auth service
```

## Related Skills

- `bart-enhanced` - Creates tasks
- `ralph-enhanced` - Executes tasks
- `memory-decay` - Archives old tasks
