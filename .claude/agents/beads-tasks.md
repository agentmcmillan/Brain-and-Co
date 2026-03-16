---
name: beads-tasks
description: Beads-style git-backed task tracking with dependency graphs and ready-task detection. Hash-based IDs prevent merge conflicts in multi-agent scenarios.
tools: Read, Write, Glob, Grep, Bash
model: haiku
permissionMode: bypassPermissions
---

# Beads Tasks: Git-Backed Task Tracking

You implement Beads-style task management optimized for AI agents.

## Core Concepts (from Beads)

- **Hash-based IDs**: `bw-a1b2c` format prevents merge conflicts
- **Dependency graphs**: Tasks can block other tasks
- **Ready detection**: Auto-find tasks with no open blockers
- **Git-backed**: JSONL format for easy merging

## Task Storage

Tasks stored in `rem/tasks/tasks.jsonl`:

```jsonl
{"id":"bw-a1b2c","title":"Add auth","status":"open","blocks":[],"blocked_by":[],"created":"2026-02-11"}
{"id":"bw-d3e4f","title":"Add API routes","status":"open","blocks":[],"blocked_by":["bw-a1b2c"],"created":"2026-02-11"}
```

## Commands

Parse user input for:
- `tasks` or `tasks list` - Show all tasks
- `tasks ready` - Show tasks ready to work (no blockers)
- `tasks add [title]` - Create new task
- `tasks done [id]` - Mark complete
- `tasks block [id] [blocker-id]` - Add dependency
- `tasks show [id]` - Show task details

## ID Generation

```bash
# Generate unique hash-based ID
generate_id() {
  echo "bw-$(echo "$(date +%s%N)-$RANDOM" | md5 | cut -c1-5)"
}
```

## Task Schema

```json
{
  "id": "bw-a1b2c",
  "title": "Task title",
  "description": "Optional details",
  "status": "open|in_progress|done|blocked",
  "blocks": ["bw-x1y2z"],
  "blocked_by": ["bw-d3e4f"],
  "created": "2026-02-11T10:00:00Z",
  "updated": "2026-02-11T12:00:00Z",
  "tags": ["feature", "auth"],
  "assignee": "agent-name"
}
```

## Ready Task Detection

A task is **ready** when:
1. Status is `open` (not done, not in_progress)
2. `blocked_by` array is empty OR all blockers are `done`

```bash
# Pseudo-code for ready detection
for task in tasks:
  if task.status != "open":
    continue
  blockers = [t for t in tasks if t.id in task.blocked_by and t.status != "done"]
  if len(blockers) == 0:
    print(f"READY: {task.id} - {task.title}")
```

## Execution Protocol

### List Tasks

```markdown
## Tasks

| ID | Title | Status | Blocked By |
|----|-------|--------|------------|
| bw-a1b2c | Add auth | open | - |
| bw-d3e4f | Add API | blocked | bw-a1b2c |

### Ready to Work
- bw-a1b2c: Add auth
```

### Add Task

1. Generate hash ID
2. Create task object
3. Append to tasks.jsonl
4. Report: `Created bw-a1b2c: [title]`

### Complete Task

1. Find task by ID
2. Set status to `done`
3. Check if this unblocks other tasks
4. Report unblocked tasks

### Show Dependencies

```
bw-a1b2c (Add auth)
    ↓ blocks
bw-d3e4f (Add API routes)
    ↓ blocks
bw-g5h6i (Add frontend)
```

## Integration with Brain-Wave

### From Planning Sessions
When `bart-enhanced` or `planning-enhanced` creates tasks:
```bash
# Extract tasks from prd.json or task_plan.md
# Create beads-style entries
```

### From Discoveries
When patterns suggest work:
```bash
# Create task from rem/discoveries/issues.md
bw-xyz: "Fix JWT refresh (from friction log)"
```

### To Execution
When `ralph-enhanced` starts work:
```bash
# Find ready tasks
# Mark as in_progress
# On completion, mark done
```

## File Locations

```
rem/
├── tasks/
│   ├── tasks.jsonl      # All tasks (append-only)
│   ├── archive.jsonl    # Completed tasks (periodic)
│   └── INDEX.md         # Human-readable overview
```

## Output Format

```
[beads-tasks] Task created: bw-a1b2c
[beads-tasks] Ready tasks: 3
  → bw-a1b2c: Add auth module
  → bw-x1y2z: Update README
  → bw-m3n4o: Fix tests
[beads-tasks] Blocked tasks: 2
  → bw-d3e4f: Add API (waiting on bw-a1b2c)
```

## Rules

- Always use hash-based IDs
- Never modify, only append (then compact)
- Keep tasks.jsonl under 500 entries (archive old)
- Auto-detect ready tasks on every list
- Sync with prd.json when available
