# CLAUDE.md — Brain-and-Co

Unified platform: MCP infrastructure + cross-agent memory + local knowledge persistence + workflow skills + autonomous execution agents.

## Repository Structure

| Directory | Purpose |
|-----------|---------|
| `gateway/` | MCP Gateway — FastMCP proxy aggregating backend servers (port 9000) |
| `memento/` | Memento MCP — Cross-agent semantic memory (PostgreSQL + pgvector + Redis) |
| `tools/` | FastMCP Tools — Fleet status, Signal messaging, config management |
| `wrappers/` | Stdio-to-HTTP wrappers for GitHub, Signal, Docker, Ollama, SSH, RSS, Cloudflare |
| `caddy/` | Reverse proxy with automatic TLS + mTLS |
| `client-configs/` | Client connection configs for Claude Code |
| `deploy/` | Deployment scripts for NAS |
| `.claude/agents/` | 15 agent definitions (memory, execution, quality) |
| `.claude/rules/` | 6 auto-loaded context rules |
| `skills/` | 30+ Claude Code skills (memory, execution, hardware, review) |
| `integrations/` | Hooks, agent-teams, ClawHub, Gastown, gstack, prompts |
| `ralph/` | Autonomous execution system (Bart + Ralph + GSD) |
| `symphony/` | Autonomous agent orchestrator (task queuing, heartbeat, PR creation) |
| `docs/` | Reference images and diagrams |

## Quick Start

```bash
# Install agents, hooks, rules, and skills into ~/.claude/
./setup.sh

# Deploy infrastructure to NAS (optional)
./deploy/deploy.sh
```

## Brain-Wave Memory System

@alpha-wave/INDEX.md
@beta-wave/_MAP.md
@rem/restoration/PROTOCOL.md

Initialize with: `use brain-wave-init agent`

## Execution System (Bart + Ralph)

```
/bart new               # Plan a feature
/bart research          # Research codebase
/bart create-prd        # Generate prd.json
/ralph                  # Execute stories from prd.json
./ralph/ralph-runner.sh # CI automation
```

## Agent Reference

### Brain-Wave Core
| Agent | Command | Purpose |
|-------|---------|---------|
| alpha-wave | `use alpha-wave agent` | Index files and create summaries |
| beta-wave | `use beta-wave agent` | Map architecture and dependencies |
| rem | `use rem agent` | Sync sessions and capture discoveries |
| brain-wave-init | `use brain-wave-init agent` | Initialize full memory system |
| brain-wave-prime | `use brain-wave-prime agent` | Master coordinator for teams |

### Execution
| Agent | Command | Purpose |
|-------|---------|---------|
| bart-enhanced | `/bart` | Feature planning with Brain-Wave context |
| ralph-enhanced | `/ralph` | Story execution with Brain-Wave context |
| gsd-orchestrator | `use gsd-orchestrator agent` | Multi-phase complex work |
| mcralph-orchestrator | `use mcralph-orchestrator agent` | Intelligent routing |
| planning-enhanced | `/planning-with-files` | Research with persistence |

### Quality
| Agent | Command | Purpose |
|-------|---------|---------|
| premortem | `use premortem agent` | Pre-mortem failure analysis |
| reviewer | `use reviewer agent` | Adversarial code review |

### Utility
| Agent | Command | Purpose |
|-------|---------|---------|
| memory-decay | `use memory-decay agent` | Compact old sessions |
| shared-memory | `use shared-memory agent` | Cross-instance sync |
| beads-tasks | `use beads-tasks agent` | Git-backed task tracking |

## Symphony (Autonomous Orchestrator)

Manages a fleet of Claude Code agents with task queuing, heartbeat resumption, and post-completion hooks.

```bash
cd symphony && docker-compose up -d    # Deploy (port 9100)
curl http://localhost:9100/tasks        # List tasks
curl -X POST http://localhost:9100/tasks -d '{"title":"Fix bug","prompt":"...","repo_url":"..."}'
```

Polls Entropy Reader and Linear for tasks. See `symphony/` for full docs.

## gstack (Dev Workflow Skills)

Third-party tool by Garry Tan. Install separately:

```bash
git clone https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
cd ~/.claude/skills/gstack && ./setup
```

Provides: `/plan-ceo-review`, `/plan-eng-review`, `/review`, `/ship`, `/browse`, `/qa`, `/retro`

See `integrations/gstack/` for integration docs.

## Architecture

- **107+ tools** across 9+ namespaces
- **Brain-Wave**: Alpha-Wave (indexes) -> Beta-Wave (maps) -> REM (sessions)
- **Memento**: Cross-agent memory via `remember`/`recall`/`reflect`/`context`
- **Gateway**: Single endpoint aggregating all backend MCP servers

## Environment Variables

Required in `.env` (for infrastructure):
- `POSTGRES_PASSWORD` — PostgreSQL password for Memento
- `MEMENTO_ACCESS_KEY` — Access key for Memento MCP
- `GITHUB_PERSONAL_ACCESS_TOKEN` — GitHub API token

Optional:
- `OPENAI_API_KEY` — Embedding model (text-embedding-3-small)
- `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID` — Cloudflare MCP
- `OLLAMA_HOST` — Override ollama endpoint
- `SSH_KEYS_PATH` — Path to SSH keys directory

## Hardware Skills

`/ceo` orchestrator routes to 13 specialist skills for physical product companies. See `skills/hardware/`.
