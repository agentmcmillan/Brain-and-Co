# Brain-Wave Agent Teams Integration

Coordinate multiple Claude Code instances with shared Brain-Wave memory.

## Overview

Agent Teams provide:
- **Independent context windows** per teammate
- **Direct messaging** between teammates
- **Shared task list** (using beads-tasks format)
- **Self-coordination** without bottlenecking on lead

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TEAM LEAD (Brain-Wave Prime)                  │
│  • Loads Brain-Wave context on startup                          │
│  • Creates team via shared task list                            │
│  • Coordinates work, synthesizes findings                       │
│  • Consolidates discoveries to REM                              │
└─────────────────────────────────────────────────────────────────┘
        │
        │ spawn with CLAUDE.md (Brain-Wave auto-loads)
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                        TEAMMATES                                 │
│  Each teammate:                                                  │
│  • Reads CLAUDE.md → Brain-Wave context loads                   │
│  • Has independent context window                               │
│  • Messages other teammates directly                            │
│  • Claims tasks from shared list                                │
│  • Updates rem/tasks/tasks.jsonl                                │
└─────────────────────────────────────────────────────────────────┘
        │
        │ read/write
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SHARED BRAIN-WAVE                             │
│  • rem/tasks/tasks.jsonl (beads-style task list)                │
│  • rem/discoveries/ (shared insights)                           │
│  • alpha-wave/INDEX.md (file context)                           │
│  • beta-wave/_MAP.md (architecture context)                     │
└─────────────────────────────────────────────────────────────────┘
```

## Setup

### 1. Enable Agent Teams

Add to `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### 2. Ensure Brain-Wave is Initialized

```
use brain-wave-init agent
```

This creates the shared context that all teammates will read.

### 3. Create Team with Brain-Wave Context

```
Create an agent team for [task]. Each teammate should:
1. Read CLAUDE.md to load Brain-Wave context
2. Check rem/tasks/tasks.jsonl for their assigned work
3. Update rem/discoveries/ with findings
4. Message teammates when they find relevant information
```

## Task List Integration

Agent teams use the same beads-tasks system:

```jsonl
{"id":"bw-abc12","title":"Design auth flow","status":"open","assignee":"security"}
{"id":"bw-def34","title":"Implement JWT","status":"open","blocked_by":["bw-abc12"],"assignee":"backend"}
{"id":"bw-ghi56","title":"Add login UI","status":"open","blocked_by":["bw-def34"],"assignee":"frontend"}
```

Teammates:
- Claim tasks by setting `assignee` to their name
- Update `status` as they work
- Blocked tasks auto-unblock when dependencies complete

## Teammate Roles

### Research Team
```
Create an agent team to research [topic]:
- Researcher: Deep-dive into options
- Analyst: Compare trade-offs
- Critic: Challenge assumptions
Have them update rem/discoveries/research.md with findings.
```

### Feature Team
```
Create an agent team for [feature]:
- Frontend: React components, UI/UX
- Backend: API routes, services
- Database: Schema, migrations
Have them coordinate via rem/tasks/tasks.jsonl.
```

### Review Team
```
Create an agent team to review [PR/module]:
- Security: Vulnerabilities, auth issues
- Performance: Bottlenecks, optimization
- Quality: Tests, maintainability
Have them challenge each other's findings.
```

## Brain-Wave Context Injection

Each teammate reads Brain-Wave via CLAUDE.md imports:

```markdown
# CLAUDE.md

## Auto-Loaded Context
@alpha-wave/INDEX.md
@beta-wave/_MAP.md
@rem/restoration/PROTOCOL.md

## Team Task List
Check `rem/tasks/tasks.jsonl` for your assigned work.

## Discoveries
Add findings to `rem/discoveries/[topic].md`
```

## Hooks Integration

Configure team hooks in `settings.json`:

```json
{
  "hooks": {
    "TaskCompleted": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "./integrations/agent-teams/on-task-complete.sh"
          }
        ]
      }
    ],
    "TeammateIdle": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "./integrations/agent-teams/on-idle.sh"
          }
        ]
      }
    ]
  }
}
```

### on-task-complete.sh

Enhanced to address Reddit findings:

1. **Shared Progress File** - Logs learnings to `rem/progress/learnings.md`
2. **Task Locking** - Prevents race conditions with atomic updates
3. **Push Notifications** - Writes to `.notifications` when tasks unblock
4. **Activity Tracking** - Records completions for fair distribution

```bash
# Teammate provides learnings in hook input
{"task_id": "bw-001", "teammate_name": "backend", "learnings": "JWT refresh tokens need..."}

# Hook logs to shared file, notifies waiting teammates
[brain-wave] Logged learnings to rem/progress/learnings.md
[brain-wave] NOTIFY: Task bw-002 is now unblocked
```

### on-idle.sh

Enhanced to implement push-based notification checking:

1. **Notification Check** - Reads `.notifications` instead of polling all tasks
2. **Fair Claiming** - Analyzes activity to suggest balanced distribution
3. **Context Display** - Shows recent learnings for task continuity
4. **Learning Prompt** - Reminds teammates to capture knowledge

```bash
# When teammate goes idle, hook outputs:
[brain-wave] === NEW NOTIFICATIONS ===
[brain-wave] Task bw-002 is now READY (was_blocked_by:bw-001)
[brain-wave] ===========================
[brain-wave] Recent activity:
  backend: 3 tasks
  frontend: 1 tasks
[brain-wave] frontend has done fewer tasks - prioritize for next claim
```

## Example: Feature Development Team

```
User: Create an agent team to build user authentication:
- Security teammate: Design token strategy, review for vulnerabilities
- Backend teammate: Implement API routes and services
- Frontend teammate: Build login/signup UI
- Tests teammate: Write integration and unit tests

Use rem/tasks/tasks.jsonl for coordination.
Update rem/discoveries/ with findings.

Lead:
├── Creates team
├── Populates rem/tasks/tasks.jsonl:
│   ├── bw-001: Design auth flow (security)
│   ├── bw-002: Implement JWT service (backend, blocked by bw-001)
│   ├── bw-003: Add auth routes (backend, blocked by bw-002)
│   ├── bw-004: Build login form (frontend, blocked by bw-003)
│   └── bw-005: Write auth tests (tests, blocked by bw-003)
├── Spawns teammates
└── Teammates self-coordinate

Security:
├── Claims bw-001
├── Researches JWT vs sessions
├── Messages Backend: "Use short-lived JWT with refresh tokens"
├── Updates rem/discoveries/auth-design.md
└── Marks bw-001 done → unblocks bw-002

Backend:
├── Waits for bw-001
├── Claims bw-002 when unblocked
├── Implements JWT service
├── Messages Frontend: "Token in httpOnly cookie"
└── Continues with bw-003

[Team self-coordinates until all tasks complete]

Lead:
├── Synthesizes findings
├── Updates rem/sessions/auth-team.md
└── Cleans up team
```

## Display Modes

### In-Process (default)
All teammates in main terminal.
- Shift+Up/Down to select teammate
- Type to message directly
- Ctrl+T to toggle task list

### Split Panes (tmux/iTerm2)
Each teammate gets own pane.
- Click pane to interact
- See all output at once

Configure in settings:
```json
{
  "teammateMode": "tmux"
}
```

## Best Practices

### 1. Give Teammates Brain-Wave Context

```
Spawn a backend teammate with the prompt:
"Read CLAUDE.md to load Brain-Wave context.
Check alpha-wave/INDEX.md for file locations.
Check beta-wave/_PATTERNS.md for code conventions.
Your task: Implement the auth service."
```

### 2. Use Beads Task Dependencies

```jsonl
{"id":"bw-001","title":"Design","blocked_by":[]}
{"id":"bw-002","title":"Implement","blocked_by":["bw-001"]}
{"id":"bw-003","title":"Test","blocked_by":["bw-002"]}
```

### 3. Consolidate Discoveries

Each teammate writes to `rem/discoveries/[topic].md`.
Lead synthesizes at the end.

### 4. Avoid File Conflicts

Assign each teammate different directories:
- Frontend → src/ui/
- Backend → src/api/
- Database → src/db/

## Brain-Wave Enhancements

The hooks in this integration address known Agent Teams issues:

| Issue | Solution | File |
|-------|----------|------|
| Polling causes starvation | Push notifications via `.notifications` | on-idle.sh |
| Lost cross-task learnings | Shared `rem/progress/learnings.md` | on-task-complete.sh |
| Race conditions (~14% dupes) | File locking mechanism | on-task-complete.sh |
| Unfair task distribution | Activity tracking in `.activity` | both hooks |

**See [COMPARISON.md](./COMPARISON.md)** for detailed analysis of how these solve the problems identified in real-world testing.

## Limitations

- Experimental feature
- No session resumption for teammates
- One team per session
- Higher token cost than sub-agents

## Files

```
integrations/agent-teams/
├── README.md              # This file
├── COMPARISON.md          # Brain-Wave vs vanilla Agent Teams
├── on-task-complete.sh    # TaskCompleted hook (with fixes)
├── on-idle.sh             # TeammateIdle hook (with fixes)
└── team-examples/
    ├── research-team.md
    ├── feature-team.md
    └── review-team.md
```
