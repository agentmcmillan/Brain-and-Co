---
paths:
  - "**/*"
---

# Brain-Wave Startup Check

On session start, silently verify these exist:
- `alpha-wave/INDEX.md`, `alpha-wave/TOPICS.md`
- `beta-wave/_MAP.md`, `beta-wave/_CONNECTIONS.md`
- `rem/restoration/PROTOCOL.md`, `rem/sessions/` (at least one file)
- `.claude/agents/alpha-wave.md`, `.claude/agents/beta-wave.md`, `.claude/agents/rem.md`

If ALL present: proceed silently.
If ANY missing: report which components are missing and suggest `use brain-wave-init agent`.
If AGENTS missing but this IS the Brain-and-Co repo: check git status.

Run Brain-Wave agents in background (`run_in_background: true`) so the user can keep working.

## File Size Limits

All Brain-Wave output files must stay small:

| File Type | Target | Maximum |
|-----------|--------|---------|
| Index/Topic/Summary files | 50 lines | 100 lines |
| Maps | 100 lines | 200 lines |
| Sessions | 30 lines | 50 lines |

When files exceed limits: split into subdirectory with `_INDEX.md`, archive old content.
