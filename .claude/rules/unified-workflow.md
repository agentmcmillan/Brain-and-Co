---
paths:
  - "**/*"
---

# Unified Workflow Integration

This environment integrates four systems. Follow these rules when they interact.

## System Overview

| System | Purpose | Key Tools |
|--------|---------|-----------|
| **Network MCP** | Infrastructure + Memento cross-agent memory | `remember`, `recall`, `reflect`, `context`, `signal_send` |
| **Brain-Wave** | Local knowledge persistence (alpha/beta/REM) | Auto-sync hooks, session checkpoints |
| **Paperclip** | Agent orchestration + task management | API at `:3100`, env vars `PAPERCLIP_*` |
| **gstack** | Workflow skills for dev lifecycle | `/plan-*-review`, `/review`, `/ship`, `/qa`, `/retro` |

## Skill Disambiguation

- `/review` = gstack pre-landing PR review (SQL safety, LLM trust, Greptile, two-pass checklist)
- `/code-review` = Brain-Wave adversarial reviewer agent (git diff, patterns, ship/block verdict)
- Both are valid — use `/review` for PR-focused work, `/code-review` for broader code analysis

## When Paperclip Is Active (PAPERCLIP_TASK_ID is set)

After completing gstack skills, post results to the Paperclip task:

### After `/review`
Post a comment summarizing findings:
```bash
curl -s -X POST "$PAPERCLIP_API_URL/api/issues/$PAPERCLIP_TASK_ID/comments" \
  -H "Authorization: Bearer $PAPERCLIP_API_KEY" \
  -H "X-Paperclip-Run-Id: $PAPERCLIP_RUN_ID" \
  -H "Content-Type: application/json" \
  -d '{"body": "Pre-landing review complete. [N] CRITICAL, [N] INFORMATIONAL findings."}'
```
If CRITICAL findings block shipping, update task status to `blocked`.

### After `/ship`
Update task status to `in_review` and comment with PR URL:
```bash
curl -s -X PATCH "$PAPERCLIP_API_URL/api/issues/$PAPERCLIP_TASK_ID" \
  -H "Authorization: Bearer $PAPERCLIP_API_KEY" \
  -H "X-Paperclip-Run-Id: $PAPERCLIP_RUN_ID" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_review"}'
```

### After `/qa`
Post health score and top issues as a comment.

### After `/retro`
Remember key metrics to Memento for trend tracking:
```
remember(topic="retro", type="fact", content="Retro [date]: [N] commits, [N]% test ratio, [N]-day streak", importance=0.7, scope="permanent")
```

## When Forging Learnings (`/forge`)

After writing to `rem/learnings/`, also sync top learnings to Memento:
- For each ESTABLISHED or CONFIRMED learning, call `remember` with `type="procedure"`, `scope="permanent"`
- Topic should match the learning's topic category
- This enables cross-agent knowledge sharing via Memento `recall`

## When Injecting Knowledge (`/inject`)

After loading `rem/learnings/INDEX.md`, also:
- Call Memento `recall` with relevant project topics to surface cross-agent knowledge
- Call Memento `context` to load core memory (preferences, errors, procedures)
- Merge Memento results with local Brain-Wave learnings, deduplicating by content

## Session Start Sequence

When a Paperclip heartbeat starts (PAPERCLIP_TASK_ID is set):
1. Load Brain-Wave context (REM checkpoint, Alpha INDEX, Beta MAP)
2. Call Memento `context` for cross-session knowledge
3. Checkout the Paperclip task (`POST /api/issues/{id}/checkout`)
4. Read task ancestors and comments for full context
5. Begin work

## Quality Gate Flow

Before shipping, ensure all gates pass:
1. gstack `/review` — no unresolved CRITICAL findings
2. gstack `/ship` — tests pass, evals pass (if applicable)
3. Paperclip approval gate — if required by governance
4. Brain-Wave pre-commit gate — no indexed file overwrites
