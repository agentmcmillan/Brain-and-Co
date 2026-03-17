---
paths:
  - "**/*"
---

# Unified Workflow Integration

## System Overview

| System | Purpose | Key Tools |
|--------|---------|-----------|
| **Network MCP** | Infrastructure + Memento memory | `remember`, `recall`, `reflect`, `context` |
| **Brain-Wave** | Local knowledge persistence | Auto-sync hooks, session checkpoints |
| **Paperclip** | Agent orchestration | API at `:3100`, env vars `PAPERCLIP_*` |
| **gstack** | Dev workflow skills | `/review`, `/ship`, `/qa`, `/retro` |

## Skill Disambiguation

- `/review` = gstack pre-landing PR review
- `/code-review` = Brain-Wave adversarial reviewer agent (git diff, patterns, ship/block)

## When Paperclip Is Active (PAPERCLIP_TASK_ID set)

After gstack skills, post results to Paperclip API (`$PAPERCLIP_API_URL/api/issues/$PAPERCLIP_TASK_ID`):
- After `/review`: POST comment with findings count. Set `blocked` if CRITICAL.
- After `/ship`: PATCH status to `in_review`, comment with PR URL.
- After `/qa`: POST health score as comment.
- After `/retro`: Sync metrics to Memento (`remember` with `scope="permanent"`).

## Forge/Inject Integration

- `/forge`: Sync ESTABLISHED learnings to Memento via `remember` with `type="procedure"`.
- `/inject`: Merge Memento `recall` + `context` with local `rem/learnings/`.

## Quality Gates

Before shipping: `/review` (no CRITICAL) → `/ship` (tests pass) → Paperclip approval → Brain-Wave pre-commit gate.
