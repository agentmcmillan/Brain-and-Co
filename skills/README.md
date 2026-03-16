# Brain-Wave Skills

OpenClaw/ClawHub compatible skills for the Brain-Wave memory system.

## Quick Install

```bash
# Install the collection
clawhub install brain-wave

# Or install individually
clawhub install brain-wave-init
```

## Available Skills

### Core Memory System

| Skill | Description | Command |
|-------|-------------|---------|
| `brain-wave-init` | Initialize full system | `/brain-wave-init` |
| `alpha-wave` | Index files & summaries | `/alpha-wave` |
| `beta-wave` | Map architecture | `/beta-wave` |
| `rem` | Sync & sessions | `/rem` |

### Enhanced Workflows

| Skill | Description | Command |
|-------|-------------|---------|
| `bart-enhanced` | Feature planning | `/bart new` |
| `ralph-enhanced` | Story execution | `/ralph` |
| `gsd-orchestrator` | Multi-phase work | `/gsd` |
| `mcralph-orchestrator` | Intelligent routing | `/mcralph` |
| `planning-enhanced` | Research planning | `/planning-with-files` |

### Collaboration

| Skill | Description | Command |
|-------|-------------|---------|
| `shared-memory` | Cross-instance sharing | `/shared-memory export` |

## Dependency Graph

```
brain-wave-init (standalone entry point)
        │
        ▼
   alpha-wave (indexes files)
        │
        ▼
    beta-wave (maps architecture)
        │
        ▼
       rem (syncs everything)
        │
        ├──────────────────────────┬──────────────────┐
        ▼                          ▼                  ▼
bart-enhanced              planning-enhanced    shared-memory
        │                                        (collaboration)
        ▼
ralph-enhanced
        │
        ├──────────────────┐
        ▼                  ▼
gsd-orchestrator    mcralph-orchestrator
```

## SKILL.md Format

Each skill follows the OpenClaw Agent Skill convention:

```yaml
---
name: skill-name
description: What it does
version: 1.0.0
author: agentmcmillan
user-invocable: true
tags: [memory, productivity]
metadata:
  requires:
    bins: [git]
    config: [alpha-wave/INDEX.md]
---

# Instructions for the agent...
```

## Local Development

```bash
# Test a skill locally
clawhub validate skills/brain-wave-init/

# Install locally without publishing
clawhub install ./skills/brain-wave-init --local
```

## Publishing

See [integrations/clawhub/PUBLISHING.md](../integrations/clawhub/PUBLISHING.md) for the full publishing workflow.

## Security

All skills are designed to:
- Only read/write within project directory
- Not make network requests
- Not access credentials
- Require explicit permissions

Review skill source before enabling in sensitive environments.

## Contributing

1. Fork the repository
2. Create skill in `skills/[name]/SKILL.md`
3. Follow the format convention
4. Test locally
5. Submit PR

## License

MIT - See repository LICENSE file.
