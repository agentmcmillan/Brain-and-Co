# Brain-and-Co

A unified platform for AI agent development: MCP infrastructure, persistent memory, autonomous execution, and workflow skills.

![Brain-Wave](https://img.shields.io/badge/Brain--Wave-Memory%20System-blue)
![Ralph](https://img.shields.io/badge/Ralph-Execution-green)
![GSD](https://img.shields.io/badge/GSD-Multi--Agent-orange)
![Memento](https://img.shields.io/badge/Memento-Semantic%20Memory-purple)

## What This Is

Brain-and-Co brings together four systems into one integrated platform:

```
┌──────────────────────────────────────────────────────────────┐
│                  MCP Infrastructure Layer                      │
│  Gateway (9000) + Memento (56332) + Tools (8091) + Wrappers   │
│  PostgreSQL + Redis + Caddy TLS + 7 MCP Wrappers              │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────┴───────────────────────────────────┐
│                    Brain-Wave Memory Layer                     │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐  │
│  │ Alpha-Wave  │  │ Beta-Wave   │  │        REM           │  │
│  │ (Index)     │  │ (Maps)      │  │ (Sessions/Discovery) │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬───────────┘  │
└─────────┼────────────────┼─────────────────────┼──────────────┘
          │                │                     │
          ▼                ▼                     ▼
┌──────────────────────────────────────────────────────────────┐
│   Bart/Ralph    │      GSD        │   Planning-with-Files     │
│   (Stories)     │  (Multi-Agent)  │  (Markdown Persistence)   │
└──────────────────────────────────────────────────────────────┘
```

**Brain-Wave Memory** makes all other agents smarter by providing instant codebase context, eliminating redundant research.

**MCP Infrastructure** provides cross-agent semantic memory (Memento), fleet tools, and connectivity to GitHub, Signal, Docker, Ollama, SSH, and RSS.

**Bart + Ralph** plan features and execute stories autonomously with fresh context per story.

**GSD** orchestrates complex multi-phase work (research, plan, execute, verify) with parallel agents.

## Quick Start

### Option 1: Skills Only (No Infrastructure)

```bash
git clone https://github.com/agentmcmillan/Brain-and-Co.git
cd Brain-and-Co

# Install agents, hooks, rules, and skills into ~/.claude/
./setup.sh

# In Claude Code, initialize Brain-Wave:
# use brain-wave-init agent
```

### Option 2: Full Stack (Skills + Infrastructure)

```bash
git clone https://github.com/agentmcmillan/Brain-and-Co.git
cd Brain-and-Co

# Install skills
./setup.sh

# Configure infrastructure
cp .env.example .env
# Edit .env with your credentials

# Deploy
docker-compose up -d

# Or deploy to NAS
./deploy/deploy.sh
```

### Option 3: Copy to Existing Project

```bash
# Copy just the agent system to your project
cp -r Brain-and-Co/.claude/ /path/to/your/project/.claude/
cp Brain-and-Co/CLAUDE.md /path/to/your/project/

# In your project with Claude Code:
# use brain-wave-init agent
```

## Components

### MCP Infrastructure

| Service | Port | Purpose |
|---------|------|---------|
| Gateway | 9000 | Single-endpoint MCP proxy aggregating all backends |
| Memento | 56332 | Cross-agent semantic memory (PostgreSQL + pgvector + Redis) |
| Tools | 8091 | Fleet status, Signal messaging, config management |
| Caddy | 8843 | Reverse proxy with TLS + mTLS |
| GitHub MCP | - | GitHub API wrapper |
| Signal MCP | - | Signal messaging wrapper |
| Docker MCP | - | Docker management wrapper |
| Ollama MCP | - | Local LLM wrapper |
| SSH MCP | - | SSH management wrapper |
| RSS MCP | - | RSS feed reader |

### Brain-Wave Memory System

Three agents that give Claude persistent memory across sessions:

- **Alpha-Wave**: Indexes every file, creates summaries and topic cross-references
- **Beta-Wave**: Maps architecture, dependencies, patterns, and design decisions
- **REM**: Captures session history, discoveries, and synchronizes state

### Execution System (Bart + Ralph)

Plan features and execute stories autonomously:

```
/bart new              → Capture feature vision
/bart research         → Investigate codebase
/bart create-prd       → Generate prd.json
/ralph                 → Execute each story with fresh context
```

See [`ralph/`](ralph/) for the full execution system and [interactive flowchart](ralph/flowchart/).

![Ralph Flowchart](docs/ralph-flowchart.png)

### Skills Library (30+)

| Category | Skills |
|----------|--------|
| **Memory** | alpha-wave, beta-wave, rem, brain-wave-init, brain-wave-prime, memory-decay, shared-memory |
| **Execution** | bart, ralph, ralph-master, bart-enhanced, ralph-enhanced, gsd-orchestrator, mcralph-orchestrator, planning-enhanced, beads-tasks, prd |
| **Quality** | code-review, premortem, reviewer |
| **Workflow** | forge, inject, planning-with-files |
| **Hardware** | ceo + 13 specialists (bom-review, cost-model, design-review, compliance-check, test-protocol, inventory-pulse, production-retro, ship-logistics, field-quality, voc-analysis, plan-ops-review, unit-economics, supplier-scorecard) |

## Agent Reference

| Agent | Command | Purpose |
|-------|---------|---------|
| brain-wave-init | `use brain-wave-init agent` | Initialize full memory system |
| alpha-wave | `use alpha-wave agent` | Index files and create summaries |
| beta-wave | `use beta-wave agent` | Map architecture and dependencies |
| rem | `use rem agent` | Sync sessions and capture discoveries |
| brain-wave-prime | `use brain-wave-prime agent` | Master coordinator for agent teams |
| bart-enhanced | `/bart` | Feature planning with Brain-Wave context |
| ralph-enhanced | `/ralph` | Story execution with Brain-Wave context |
| mcralph-orchestrator | `use mcralph-orchestrator agent` | Intelligent routing to best system |
| gsd-orchestrator | `use gsd-orchestrator agent` | Multi-phase complex work |
| planning-enhanced | `/planning-with-files` | Research with markdown persistence |
| premortem | `use premortem agent` | Pre-mortem failure analysis |
| reviewer | `use reviewer agent` | Adversarial code review |
| memory-decay | `use memory-decay agent` | Compact old sessions |
| shared-memory | `use shared-memory agent` | Cross-instance context sync |
| beads-tasks | `use beads-tasks agent` | Git-backed task tracking |

## Recommended Workflows

### New Feature
```
use mcralph-orchestrator agent
→ Routes to Bart for planning, Ralph for execution
→ Brain-Wave provides instant codebase context
→ Learnings captured to REM
```

### Major Refactor
```
use gsd-orchestrator agent
→ Research phase (skips what Brain-Wave already knows)
→ Plan with architecture data from Beta-Wave
→ Execute in parallel with pattern compliance
→ Verify against architectural constraints
```

### Investigation
```
use planning-enhanced agent
→ Creates task_plan.md with Brain-Wave context
→ findings.md captures discoveries
→ Findings sync to rem/discoveries/
```

## Auto-Sync Hooks

Install Claude Code hooks for automatic memory synchronization:

```bash
bash integrations/hooks/install.sh
```

| Hook | Trigger | Purpose |
|------|---------|---------|
| auto-sync-rem | Edit, Write | Updates `rem/CHANGELOG.md` and `rem/LAST-RUN.md` |
| auto-index-alpha | Write | Adds new files to `alpha-wave/INDEX.md` |
| session-checkpoint | idle_prompt | Saves session state to `rem/sessions/` |
| discovery-logger | Task | Logs agent insights to `rem/discoveries/` |
| context-hint | Read | Suggests related files from Beta-Wave |
| pre-commit-gate | commit | Validates before git commits |

## Attribution

Built on the shoulders of giants:

- **Geoffrey Huntley** — [Ralph pattern](https://ghuntley.com/ralph/) (master/worker agent architecture)
- **glittercowboy** — [Get Shit Done](https://github.com/glittercowboy/get-shit-done) (multi-agent orchestration)
- **OthmanAdi** — [Planning with Files](https://github.com/OthmanAdi/planning-with-files) (Manus-style persistence)
- **Sylweriusz Szydlik** — [Memory System article](https://medium.com/@nbhyxq/claude-forgot-my-entire-project-so-i-built-a-memory-system-6a872a3cc58f) (persistence architecture)
- **karanb192** — [Claude Code Hooks](https://github.com/karanb192/claude-code-hooks) (hook patterns)

## License

MIT License — See [LICENSE](LICENSE)

---

*Built with Brain-Wave — Because Claude shouldn't forget your project.*
