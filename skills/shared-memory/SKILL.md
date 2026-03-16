---
name: shared-memory
description: Share Brain-Wave context between Claude instances and team members
version: 1.0.0
author: agentmcmillan
homepage: https://github.com/agentmcmillan/Claude-Brain-Care
user-invocable: true
tags:
  - memory
  - collaboration
  - sharing
  - team
metadata:
  requires:
    bins:
      - git
    config:
      - rem/restoration/PROTOCOL.md
  os:
    - darwin
    - linux
    - windows
---

# Shared Memory: Cross-Instance Context Sharing

Share Brain-Wave context between Claude instances, machines, or team members.

## What It Does

- Exports shareable context snapshots
- Imports context from other instances
- Syncs via git or direct file transfer
- Resolves merge conflicts
- Maintains peer registry

## Usage

### Export Context
```
/shared-memory export
```
Creates `rem/shared/exports/[timestamp].json` with:
- Current session state
- Key discoveries
- Architecture summary
- Active focus areas

### Import Context
```
/shared-memory import [file-or-url]
```
Merges incoming context into local Brain-Wave.

### Sync with Peers
```
/shared-memory sync
```
Push/pull with registered peers via git.

## Directory Structure

```
rem/
├── shared/
│   ├── exports/           # Your shareable snapshots
│   │   └── [timestamp].json
│   └── imports/           # Received from others
│       └── [source].json
└── sync/
    ├── peers.json         # Known peer instances
    └── conflicts.md       # Merge conflict log
```

## Export Format

```json
{
  "version": "1.0",
  "timestamp": "2026-02-11T10:00:00Z",
  "source": {
    "project": "brain-care",
    "instance": "macbook-pro-1",
    "user": "conor"
  },
  "context": {
    "focus": "Adding shared memory feature",
    "recentFiles": ["skills/shared-memory/SKILL.md"],
    "discoveries": [
      {
        "topic": "architecture",
        "insight": "Skills follow OpenClaw SKILL.md format"
      }
    ],
    "openQuestions": []
  },
  "summary": {
    "filesIndexed": 33,
    "directoriesMapped": 6,
    "sessionsCapture": 5
  }
}
```

## Use Cases

### Team Collaboration
```
Developer A: /shared-memory export
  → Commits rem/shared/exports/2026-02-11.json
  → Pushes to shared repo

Developer B: git pull
  → /shared-memory import rem/shared/exports/2026-02-11.json
  → Now has A's context
```

### Machine Sync
```
Laptop: /shared-memory export
  → Syncs via git/dropbox/etc

Desktop: /shared-memory import
  → Continues where laptop left off
```

### Handoff
```
Outgoing dev: /shared-memory export --comprehensive
  → Full context dump

Incoming dev: /shared-memory import [file]
  → Instant onboarding context
```

## Peer Registry

Register peers for automatic sync:

```json
// rem/sync/peers.json
{
  "peers": [
    {
      "name": "team-shared",
      "type": "git",
      "remote": "origin",
      "branch": "brain-wave-sync"
    },
    {
      "name": "my-desktop",
      "type": "file",
      "path": "/Volumes/Shared/brain-wave/"
    }
  ]
}
```

## Conflict Resolution

When imports conflict with local state:

1. **Auto-merge**: Non-conflicting discoveries combined
2. **Newer wins**: Session state uses most recent
3. **Manual review**: Conflicts logged to `rem/sync/conflicts.md`

```markdown
## Conflict: 2026-02-11

### Source: team-shared
Focus: "Adding auth module"

### Local
Focus: "Adding payment module"

### Resolution
[ ] Keep local
[ ] Accept remote
[ ] Merge both
```

## Privacy

Exports include only:
- Session summaries (not full conversations)
- Discoveries (insights, not code)
- Architecture maps (structure, not content)
- File paths (not file contents)

**Never exported**:
- API keys or secrets
- Full file contents
- Personal conversation history
- Credentials from CLAUDE.md

## Commands

| Command | Description |
|---------|-------------|
| `/shared-memory export` | Create shareable snapshot |
| `/shared-memory import [file]` | Import external context |
| `/shared-memory sync` | Sync with all peers |
| `/shared-memory peers` | List registered peers |
| `/shared-memory conflicts` | Show unresolved conflicts |

## Integration

Works with all Brain-Wave agents:
- **REM**: Captures exports in session log
- **Alpha-Wave**: Merges imported file indexes
- **Beta-Wave**: Combines architecture maps

## Related Skills

- `rem` - Source of shareable context
- `brain-wave-init` - Initial setup
- `mcralph-orchestrator` - Routes shared tasks
