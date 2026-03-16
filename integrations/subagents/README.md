# Brain-Wave Sub-Agent Architecture

Leverage Claude Code's sub-agent system with Brain-Wave memory coordination.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRIME AGENT (McRalph)                       │
│  • Loads Brain-Wave context on start                            │
│  • Routes tasks to specialized sub-agents                       │
│  • Coordinates memory across all agents                         │
│  • Consolidates discoveries to REM                              │
└─────────────────────────────────────────────────────────────────┘
        │
        ├── SubagentStart hook: Load Brain-Wave context
        ├── SubagentStop hook: Sync to REM
        │
        ▼
┌───────────────────────────────────────────────────────────────────┐
│                        SUB-AGENTS                                  │
├─────────────┬─────────────┬─────────────┬─────────────┬───────────┤
│ alpha-wave  │ beta-wave   │ rem         │ bart        │ ralph     │
│ (indexer)   │ (mapper)    │ (sync)      │ (planner)   │ (executor)│
│ model:haiku │ model:haiku │ model:haiku │ model:sonnet│ model:son │
│ tools:Read  │ tools:Read  │ tools:RW    │ tools:Read  │ tools:All │
└─────────────┴─────────────┴─────────────┴─────────────┴───────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PERSISTENT MEMORY                             │
│  memory: project → .claude/agent-memory/<agent>/                 │
│  • Cross-session learning                                        │
│  • MEMORY.md per agent                                           │
│  • Synced to Brain-Wave via REM                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Integration Points

### 1. Prime Agent with Brain-Wave Context

The prime agent (McRalph) loads Brain-Wave before delegating:

```yaml
---
name: brain-wave-prime
description: Master coordinator with full Brain-Wave context. Routes tasks to specialized sub-agents.
tools: Task, Read, Write, Glob, Grep, Bash
model: opus
memory: project
permissionMode: acceptEdits
---

# Brain-Wave Prime Agent

You are the master coordinator with full Brain-Wave memory access.

## On Startup
1. Read rem/restoration/PROTOCOL.md
2. Load alpha-wave/INDEX.md
3. Check rem/tasks/tasks.jsonl for pending work

## Task Routing
- Indexing → alpha-wave sub-agent
- Mapping → beta-wave sub-agent
- Sync → rem sub-agent
- Planning → bart-enhanced sub-agent
- Execution → ralph-enhanced sub-agent
- Tasks → beads-tasks sub-agent

## Memory Coordination
After each sub-agent completes:
1. Capture discoveries to rem/discoveries/
2. Update task status in rem/tasks/
3. Sync agent-memory to Brain-Wave
```

### 2. Sub-Agent Hooks for Memory Sync

Configure hooks in `settings.json`:

```json
{
  "hooks": {
    "SubagentStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "./integrations/subagents/on-start.sh"
          }
        ]
      }
    ],
    "SubagentStop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "./integrations/subagents/on-stop.sh"
          }
        ]
      }
    ]
  }
}
```

### 3. Persistent Memory Per Agent

Each sub-agent has its own memory scope:

```yaml
---
name: alpha-wave
memory: project  # Saves to .claude/agent-memory/alpha-wave/
---
```

Memory syncs to Brain-Wave:
```
.claude/agent-memory/alpha-wave/MEMORY.md
    ↓ (REM sync)
rem/discoveries/alpha-wave-learnings.md
```

## Sub-Agent Definitions

### Memory Agents (Haiku - fast, cheap)

| Agent | Purpose | Tools | Memory |
|-------|---------|-------|--------|
| alpha-wave | Index files | Read, Glob, Grep | project |
| beta-wave | Map architecture | Read, Glob, Grep | project |
| rem | Sync everything | Read, Write | project |
| memory-decay | Compact old sessions | Read, Write | project |

### Workflow Agents (Sonnet - capable)

| Agent | Purpose | Tools | Memory |
|-------|---------|-------|--------|
| bart-enhanced | Feature planning | Read, Glob, Grep, Write | project |
| ralph-enhanced | Story execution | All | project |
| beads-tasks | Task tracking | Read, Write | project |

### Orchestrators (Opus - reasoning)

| Agent | Purpose | Tools | Memory |
|-------|---------|-------|--------|
| brain-wave-prime | Master coordinator | Task, All | project |
| gsd-orchestrator | Multi-phase work | Task, All | project |

## Parallel Agent Execution

Run multiple sub-agents simultaneously:

```
Prime: "Research auth, API, and database modules in parallel"
    │
    ├── alpha-wave (auth) ──────┐
    ├── alpha-wave (api) ───────┼── Results
    └── alpha-wave (db) ────────┘
    │
    ▼
Prime: Synthesizes findings, updates Brain-Wave
```

## Background Agents

For long-running tasks:

```
User: "Index the entire codebase in the background"
Prime: Spawns alpha-wave with run_in_background: true
User: Continues working...
[alpha-wave completes]
Prime: "Indexing complete. 147 files indexed."
```

## Task Dependencies with Beads

Sub-agents check task dependencies before starting:

```json
{"id":"bw-abc12","title":"Add auth model","status":"done"}
{"id":"bw-def34","title":"Add auth service","blocked_by":["bw-abc12"],"status":"open"}
```

Prime routes only unblocked tasks:
```
Prime: "bw-def34 is now ready (bw-abc12 completed)"
Prime: Delegates to ralph-enhanced
```

## Memory Flow

```
1. Prime loads Brain-Wave
2. Sub-agent starts with context injection
3. Sub-agent writes to agent-memory/
4. Sub-agent completes
5. Prime captures to rem/discoveries/
6. REM syncs everything
```

## Example Session

```
User: "Add user authentication"

Prime:
├── Loads Brain-Wave context
├── Checks beads-tasks for blockers
├── Routes to bart-enhanced (planning)
│   └── Creates prd.json with Brain-Wave context
├── Routes to ralph-enhanced (execution)
│   ├── Story 1: Add user model ✓
│   ├── Story 2: Add auth service ✓
│   └── Story 3: Add auth routes ✓
├── Routes to rem (sync)
│   └── Captures session, discoveries
└── Reports completion

Brain-Wave updated with:
- rem/sessions/auth-feature.md
- rem/discoveries/execution.md
- rem/tasks/tasks.jsonl (stories marked done)
```

## Setup

1. Copy sub-agent definitions to `.claude/agents/`
2. Configure hooks in settings.json
3. Initialize Brain-Wave: `use brain-wave-init agent`
4. Use prime agent: `use brain-wave-prime agent`

## Files

```
integrations/subagents/
├── README.md              # This file
├── prime.md               # Prime agent definition
├── on-start.sh            # SubagentStart hook
├── on-stop.sh             # SubagentStop hook
└── settings-hooks.json    # Hook configuration
```
