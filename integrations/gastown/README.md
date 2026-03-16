# Gastown Integration: Parallel Agent Sessions

Git worktree isolation for running multiple Brain-Wave agents in parallel.

## Concept (from [Gastown](https://github.com/steveyegge/gastown))

Traditional problem: Agents lose context when they restart or when multiple agents work simultaneously.

Gastown solution: Use **git worktrees** to give each agent an isolated workspace that persists across sessions.

## How It Works

```
main/                    # Primary workspace (Mayor/coordinator)
├── .git/
├── brain-care/
└── ...

.worktrees/
├── agent-alpha/         # Isolated workspace for Agent Alpha
│   ├── brain-care/      # Full repo copy
│   └── rem/sessions/    # Agent-specific sessions
├── agent-beta/          # Isolated workspace for Agent Beta
│   └── ...
└── agent-gamma/
    └── ...
```

## Setup

### Create Worktree for Agent

```bash
# Create isolated workspace for an agent
git worktree add .worktrees/agent-alpha -b brain-wave/agent-alpha

# Agent works in isolated directory
cd .worktrees/agent-alpha
```

### Agent Session Isolation

Each agent maintains its own:
- `rem/sessions/` - Session state
- `rem/discoveries/` - Agent-specific insights
- Working branch

### Merge Back to Main

```bash
# From main workspace
git merge brain-wave/agent-alpha --no-ff -m "Merge agent-alpha work"

# Or cherry-pick specific commits
git cherry-pick <commit-hash>
```

## Brain-Wave Integration

### Per-Agent Memory

Each worktree agent has isolated Brain-Wave state:

```
.worktrees/agent-alpha/
├── alpha-wave/          # Agent's index (synced from main)
├── beta-wave/           # Agent's maps (synced from main)
└── rem/
    ├── sessions/        # Agent-specific sessions
    ├── discoveries/     # Agent-specific discoveries
    └── agent-id.json    # Agent identity
```

### Agent Identity

```json
// rem/agent-id.json
{
  "id": "agent-alpha",
  "worktree": ".worktrees/agent-alpha",
  "created": "2026-02-11",
  "role": "feature-development",
  "parent": "main"
}
```

### Sync Protocol

```bash
# Pull latest from main
git pull origin main

# Agent does work...

# Push agent branch
git push origin brain-wave/agent-alpha

# Coordinator merges when ready
```

## Use Cases

### Parallel Feature Development

```
Main (Coordinator)
├── Agent-Auth (working on authentication)
├── Agent-API (working on API routes)
└── Agent-UI (working on frontend)
```

Each agent has full Brain-Wave context but isolated sessions.

### Long-Running Research

```
Main
└── Agent-Research (multi-day investigation)
    └── rem/sessions/research-*.md
```

Research persists even if agent restarts.

### CI/CD Integration

```yaml
# .github/workflows/agent-work.yml
jobs:
  agent-task:
    steps:
      - uses: actions/checkout@v3
      - run: git worktree add .agent -b ci/agent-${{ github.run_id }}
      - run: cd .agent && claude-code "complete task"
      - run: git push origin ci/agent-${{ github.run_id }}
```

## Commands

### Create Agent Worktree
```bash
./scripts/create-agent.sh <agent-name> [role]
```

### List Active Agents
```bash
git worktree list
```

### Remove Agent Worktree
```bash
git worktree remove .worktrees/<agent-name>
git branch -d brain-wave/<agent-name>
```

## Best Practices

1. **Name agents by role**: `agent-auth`, `agent-api`, not `agent-1`
2. **Sync before major work**: Pull main into agent branch
3. **Small, focused branches**: One feature per agent
4. **Merge frequently**: Avoid divergence
5. **Clean up**: Remove worktrees when done

## Gastown Terminology

| Gastown Term | Brain-Wave Equivalent |
|--------------|----------------------|
| Mayor | Main coordinator session |
| Polecat | Worker agent in worktree |
| Hook | Git worktree persistence |
| Rig | Project container |
| Convoy | Work batch across agents |

## Limitations

- Worktrees share `.git` directory (can't push simultaneously)
- Large repos = large worktrees (use sparse checkout)
- Merge conflicts require manual resolution

## Related

- [Gastown](https://github.com/steveyegge/gastown) - Original multi-agent system
- [Beads](https://github.com/steveyegge/beads) - Task tracking for agents
- `shared-memory` skill - Context sharing between agents
