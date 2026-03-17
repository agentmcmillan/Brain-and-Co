# CLAUDE.md — Brain-and-Co

Unified platform: MCP infrastructure + cross-agent memory + local knowledge persistence + workflow skills + autonomous execution agents.

## Repository Structure

| Directory | Purpose |
|-----------|---------|
| `gateway/` | MCP Gateway — FastMCP proxy aggregating backend servers (port 9000) |
| `memento/` | Memento MCP — Cross-agent semantic memory (PostgreSQL + pgvector + Redis) |
| `tools/` | FastMCP Tools — Fleet status, Signal messaging, config management |
| `wrappers/` | Stdio-to-HTTP wrappers for GitHub, Signal, Docker, Ollama, SSH, RSS, Cloudflare, MiroFish |
| `caddy/` | Reverse proxy with automatic TLS + mTLS |
| `client-configs/` | Client connection configs for Claude Code |
| `deploy/` | Deployment scripts for container host |
| `.claude/agents/` | 15 agent definitions (memory, execution, quality) |
| `.claude/rules/` | 6 auto-loaded context rules |
| `skills/` | 35+ Claude Code skills (memory, execution, hardware, review, research, prediction) |
| `gstack/` | Dev workflow skills: browse, QA, review, ship, plan reviews, retro |
| `integrations/` | Hooks, agent-teams, ClawHub, Gastown, prompts |
| `ralph/` | Autonomous execution system (Bart + Ralph + GSD) |
| `symphony/` | Autonomous agent orchestrator (task queuing, heartbeat, PR creation) |
| `docs/` | Reference images, diagrams, and external tool docs |

## Quick Start

```bash
# Install agents, hooks, rules, and skills into ~/.claude/
./setup.sh

# Deploy infrastructure to container host (optional)
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

Bundled from [garrytan/gstack](https://github.com/garrytan/gstack) (MIT). Installed by `./setup.sh`.

Provides: `/plan-ceo-review`, `/plan-eng-review`, `/review`, `/ship`, `/browse`, `/qa`, `/retro`

Requires [Bun](https://bun.sh) to build the headless browser binary. See `gstack/` for source.

## Architecture

- **115+ tools** across 12+ namespaces
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
- `OPENROUTER_API_KEY` — LLM Council multi-model queries
- `MIROFISH_URL` — MiroFish prediction engine (default: `http://CONTAINER_HOST_IP:5001`)

## Karpathy Tools & External Integrations

| Skill | Command | Source | Purpose |
|-------|---------|--------|---------|
| autoresearch | `/autoresearch` | [karpathy/autoresearch](https://github.com/karpathy/autoresearch) | Autonomous experimentation loops |
| council | `/council` | [karpathy/llm-council](https://github.com/karpathy/llm-council) | Multi-LLM consensus decisions |
| rendergit | `/rendergit` | [karpathy/rendergit](https://github.com/karpathy/rendergit) | Flatten repos for LLM consumption |
| tokenize | `/tokenize` | [karpathy/minbpe](https://github.com/karpathy/minbpe) | Token counting and cost estimation |
| arxiv | `/arxiv` | [karpathy/arxiv-sanity-lite](https://github.com/karpathy/arxiv-sanity-lite) | AI paper discovery and recommendations |
| predict | `/predict` | [666ghj/MiroFish](https://github.com/666ghj/MiroFish) | Swarm intelligence predictions |

Deploy services: `docker compose -f deploy/docker-compose.mirofish.yml up -d`

See also: `docs/nanochat-reference.md` for LLM training pipeline reference.

## Hardware Skills

`/ceo` orchestrator routes to 13 specialist skills for physical product companies. See `skills/hardware/`.
