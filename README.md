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

**Symphony** runs autonomous Claude Code agents at scale — task queuing, heartbeat resumption, PR creation, and CI monitoring.

**gstack** (by Garry Tan) provides the dev lifecycle: plan reviews, code review, ship, QA testing with a headless browser, and retrospectives.

## Install for Claude Code

**One-liner** (clones repo + installs everything to `~/.claude/`):

```bash
curl -fsSL https://raw.githubusercontent.com/agentmcmillan/Brain-and-Co/main/install.sh | bash
```

Then restart Claude Code and run `use brain-wave-init agent` in any project.

### Manual Install

```bash
git clone https://github.com/agentmcmillan/Brain-and-Co.git
cd Brain-and-Co
./setup.sh
```

This installs **15 agents**, **6 rules**, **36 skills**, and **6 hooks** into `~/.claude/`.

### What Gets Installed

| Component | Count | Location | Purpose |
|-----------|-------|----------|---------|
| Agents | 15 | `~/.claude/agents/` | Memory, execution, quality agents |
| Rules | 6 | `~/.claude/rules/` | Auto-loaded context on every session |
| Skills | 36 | `~/.claude/skills/` | Slash commands (`/bart`, `/ralph`, `/ceo`, etc.) |
| Hooks | 6 | `~/.claude/hooks/brain-wave/` | Auto-sync memory on file changes |

### Copy to a Specific Project

If you only want Brain-Wave in one project instead of globally:

```bash
cp -r Brain-and-Co/.claude/ /path/to/your/project/.claude/
cp Brain-and-Co/CLAUDE.md /path/to/your/project/

# In your project with Claude Code:
# use brain-wave-init agent
```

### Full Stack (Skills + MCP Infrastructure)

For the complete platform including Memento semantic memory, MCP Gateway, and all wrappers:

```bash
git clone https://github.com/agentmcmillan/Brain-and-Co.git
cd Brain-and-Co
./setup.sh

# Configure infrastructure
cp .env.example .env
# Edit .env with your credentials (POSTGRES_PASSWORD, MEMENTO_ACCESS_KEY, GITHUB_PERSONAL_ACCESS_TOKEN)

docker-compose up -d
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

### Symphony (Autonomous Orchestrator)

Runs a fleet of Claude Code agents autonomously — queues tasks, spawns agents, resumes via heartbeat, creates PRs, and monitors CI.

```bash
cd symphony && docker-compose up -d    # Deploy on port 9100

# Submit a task
curl -X POST http://localhost:9100/tasks \
  -H "Authorization: Bearer $SYMPHONY_API_TOKEN" \
  -d '{"title":"Fix auth bug","prompt":"...","repo_url":"https://github.com/..."}'
```

- Polls Entropy Reader (iOS app) and Linear for tasks
- Up to 3 concurrent agents with priority queue + dependency resolution
- Heartbeat resumption: tasks can span up to 5 sessions (25 turns each)
- Auto-creates GitHub PRs and monitors CI status on completion

See [`symphony/`](symphony/) for full source and configuration.

### gstack (Dev Lifecycle Skills)

Third-party workflow system by [Garry Tan](https://github.com/garrytan/gstack). Install separately:

```bash
git clone https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
cd ~/.claude/skills/gstack && ./setup
```

| Skill | Purpose |
|-------|---------|
| `/plan-ceo-review` | Founder mode: rethink the problem |
| `/plan-eng-review` | Tech lead mode: architecture + edge cases |
| `/review` | Pre-landing code review |
| `/ship` | Sync, test, review, PR in one command |
| `/browse` | Headless browser for QA testing (~100ms/command) |
| `/qa` | Systematic QA: diff-aware, full, quick, regression |
| `/retro` | Engineering retrospective |

See [`integrations/gstack/`](integrations/gstack/) for integration docs.

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
