# CLAUDE.md — Brain-and-Co

Unified platform combining MCP infrastructure, cross-agent memory, local knowledge persistence, and workflow skills.

## Repository Structure

| Directory | Purpose |
|-----------|---------|
| `gateway/` | MCP Gateway — FastMCP proxy aggregating 9 backend servers (port 9000) |
| `memento/` | Memento MCP — Cross-agent semantic memory (PostgreSQL pgvector + Redis) |
| `tools/` | FastMCP Tools — Fleet status, Signal messaging, config management |
| `wrappers/` | Stdio→HTTP wrappers (supergateway) for GitHub, Signal, Docker, Ollama, SSH, RSS, Cloudflare |
| `caddy/` | Reverse proxy with automatic TLS + mTLS |
| `client-configs/` | Client connection configs for Claude Code, Codex, Gemini CLI |
| `deploy/` | Deployment scripts for NAS |
| `brain-wave/` | Agent definitions, hooks, and rules for local knowledge persistence |
| `skills/` | Claude Code skills (forge, inject, code-review, premortem, integration configs) |
| `skills/hardware/` | Physical product company skills — 14 specialist + CEO orchestrator |

## Quick Start

```bash
# Install agents, hooks, rules, and skills into ~/.claude/
./setup.sh

# Deploy infrastructure to NAS
./deploy/deploy.sh
```

## Architecture

- **107 tools** across 9 namespaces: memento(11), tools(9), context7(2), github(26), signal(3), docker(4), ollama(13), ssh(37), rss(2)
- **Brain-Wave**: Alpha-Wave (file indexes) → Beta-Wave (architecture maps) → REM (session checkpoints, auto-sync hooks)
- **Memento**: Cross-agent memory via `remember`/`recall`/`reflect`/`context` tools
- **Gateway**: Single endpoint at `http://CONTAINER_HOST_IP:9000/mcp` (LAN) or `https://YOUR_DOMAIN/gateway/mcp` (remote)

## Key Patterns

- `supergateway`: Wraps stdio MCP servers to streamable HTTP (`--outputTransport streamableHttp --stateful`)
- `create_proxy()` hangs if ANY backend is unreachable — no graceful degradation
- Context7 health probe returns 406 (cosmetic, tools still work)
- Docker-MCP needs Docker CLI binary + socket GID detection
- Ollama-MCP needs `extra_hosts: host.docker.internal:host-gateway`

## Hardware Skills (`/ceo` orchestrator + 13 specialists)

| Skill | Persona | Domain |
|-------|---------|--------|
| `/ceo` | The Founder Who Ships | Master orchestrator — routes to specialists by project phase |
| `/bom-review` | The Sourcing Curmudgeon | BOM audit — single-source risk, lead times, lifecycle |
| `/supplier-scorecard` | The Vendor Skeptic | Supplier grading — OTD, quality, communication, cost |
| `/cost-model` | The Margin Hawk | COGS waterfall, volume sensitivity, margin analysis |
| `/design-review` | The Tooling Veteran | DFM/DFA — tolerances, materials, assembly |
| `/compliance-check` | The Compliance Grizzly | Regulatory — UL/CE/FCC/RoHS matrix, gap analysis |
| `/test-protocol` | The Reliability Pessimist | Test planning — HALT, environmental, life cycle |
| `/inventory-pulse` | The Warehouse Grouch | Inventory health — DOS, dead stock, reorder points |
| `/production-retro` | The Yield Sergeant | Manufacturing retro — yield, defect Pareto, cycle time |
| `/ship-logistics` | The Landed Cost Cynic | Shipping — carrier comparison, customs, landed cost |
| `/field-quality` | The Warranty Accountant | Field failures — MTBF, failure clustering, warranty cost |
| `/voc-analysis` | The Customer Decoder | Voice of customer — sentiment, complaint clustering |
| `/plan-ops-review` | The Operations Pessimist | Ops planning — capacity, make-vs-buy, contingency |
| `/unit-economics` | The True Cost Truthsayer | SKU profitability — absorption vs marginal, breakeven |

## Environment Variables

Required in `.env`:
- `POSTGRES_PASSWORD` — PostgreSQL password for Memento
- `MEMENTO_ACCESS_KEY` — Access key for Memento MCP
- `GITHUB_PERSONAL_ACCESS_TOKEN` — GitHub API token

Optional:
- `OPENAI_API_KEY` — For embedding model (text-embedding-3-small)
- `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID` — Cloudflare MCP
- `OLLAMA_HOST` — Override ollama endpoint (default: host.docker.internal:11434)
- `SSH_KEYS_PATH` — Path to SSH keys directory
