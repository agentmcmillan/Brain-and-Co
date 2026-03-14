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
