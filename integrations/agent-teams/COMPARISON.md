# Brain-Wave vs Agent Teams: Solving the Gaps

Based on findings from a 14-task PRD comparison between "Ralph bash loop" and "Agent Teams" approaches.

## The Problem Summary

| Issue | Agent Teams Behavior | Impact |
|-------|---------------------|--------|
| Polling | Idle agents must actively check for work | "Gamma got zero tasks" |
| Learning Loss | 37 lines captured vs 914 in Ralph | Lost cross-task context |
| Race Conditions | ~14% duplicate task claims | Wasted compute |
| Unfair Distribution | Aggressive pollers dominate | Uneven workload |

## How Brain-Wave Hooks Address Each Issue

### 1. Polling → Push Notifications

**Problem**: Agent Teams uses pull-based task checking. Idle agents poll TaskList repeatedly, missing newly-unblocked tasks.

**Solution**: `on-task-complete.sh` writes to `rem/tasks/.notifications` when tasks unblock.

```
# When task completes, notify watchers
echo "$TIMESTAMP|UNBLOCKED|$TASK_ID|info" >> rem/tasks/.notifications
```

`on-idle.sh` reads notifications since last check:

```
# Check for new notifications (not polling all tasks)
NEW_NOTIFS=$(awk -F'|' -v last="$LAST_CHECK" '$1 > last' .notifications)
```

**Result**: Idle agents see exactly which tasks became available, when.

---

### 2. Learning Loss (914 vs 37 lines)

**Problem**: Each Agent Teams teammate runs in isolation. When tasks complete, learnings stay in that session's context.

**Solution**: `on-task-complete.sh` appends to shared `rem/progress/learnings.md`:

```markdown
## 2026-02-11 14:32 - task-007 (gamma)
- Found that the API requires auth header even for public endpoints
- Pattern: always include X-Request-ID for tracing
```

**Result**: Cross-task learnings accumulate in one file, readable by all teammates.

---

### 3. Race Conditions (~14% duplicate work)

**Problem**: Multiple agents claim the same task simultaneously, do duplicate work.

**Solution**: File locking in `on-task-complete.sh`:

```bash
LOCKFILE="rem/tasks/.lock"
while [ -f "$LOCKFILE" ]; do sleep 0.1; done
touch "$LOCKFILE"
# ... atomic update ...
rm -f "$LOCKFILE"
```

**Result**: Task status updates are serialized, preventing duplicate claims.

---

### 4. Unfair Task Distribution

**Problem**: Faster-polling agents claim more tasks. One agent did 60% of work in tests.

**Solution**: Activity tracking in both hooks:

```bash
# on-task-complete.sh logs completions
echo "$TIMESTAMP|$TEAMMATE|completed|$TASK_ID" >> rem/tasks/.activity

# on-idle.sh analyzes distribution
MY_COUNT=$(grep "|$TEAMMATE|" .activity | wc -l)
if [ "$MY_COUNT" -lt "$OTHER_AVG" ]; then
  echo "[brain-wave] $TEAMMATE has done fewer tasks - prioritize"
fi
```

**Result**: Team Lead can see activity distribution, suggest fair claiming.

---

## Architecture Comparison

```
Agent Teams (default)          Brain-Wave Enhanced
─────────────────────          ────────────────────

Team Lead                      Team Lead
    │                              │
    ├─→ TaskList ←─┐               ├─→ TaskList ←─────┐
    │              │               │                  │
    ▼              ▼               ▼                  ▼
┌───────┐    ┌───────┐        ┌───────┐         ┌───────┐
│ Alpha │    │ Beta  │        │ Alpha │         │ Beta  │
└───────┘    └───────┘        └───┬───┘         └───┬───┘
    │              │              │                  │
    │   (polling)  │              │                  │
    ▼              ▼              ▼                  ▼
   ???            ???         ┌─────────────────────────┐
                              │   rem/tasks/            │
                              │   ├── .notifications    │
                              │   ├── .activity         │
                              │   └── .lock             │
                              └─────────────────────────┘
                                         │
                                         ▼
                              ┌─────────────────────────┐
                              │   rem/progress/         │
                              │   └── learnings.md      │
                              └─────────────────────────┘
```

## File Reference

| File | Purpose | Written By | Read By |
|------|---------|------------|---------|
| `rem/tasks/.notifications` | Push notifications for unblocked tasks | on-task-complete | on-idle |
| `rem/tasks/.activity` | Activity tracking per teammate | on-task-complete, on-idle | on-idle, Team Lead |
| `rem/tasks/.lock` | Mutex for atomic updates | on-task-complete | on-task-complete |
| `rem/progress/learnings.md` | Shared cross-task learnings | on-task-complete | All teammates |
| `rem/tasks/.last_check_$TEAMMATE` | Last notification check time | on-idle | on-idle |

## Hook Configuration

In your Claude Code settings or `.claude/hooks.json`:

```json
{
  "hooks": {
    "TaskCompleted": ["./integrations/agent-teams/on-task-complete.sh"],
    "TeammateIdle": ["./integrations/agent-teams/on-idle.sh"]
  }
}
```

## Trade-offs

| Aspect | Without Brain-Wave | With Brain-Wave |
|--------|-------------------|-----------------|
| Setup Complexity | Simple | Requires hooks config |
| Disk I/O | Minimal | Moderate (file writes) |
| Cross-task Learning | Lost | Preserved |
| Task Visibility | Poll-based | Event-driven |
| Race Prevention | None | File locking |
| Fairness | Random | Tracked |

## When to Use

**Use Brain-Wave hooks when:**
- Running multi-task PRDs with dependencies
- Need cross-task learning capture
- Want fair workload distribution
- Tasks have complex blocking relationships

**Skip Brain-Wave hooks when:**
- Simple independent tasks
- Single-agent execution
- Speed is critical over learning capture

## Related

- `integrations/hooks/` - General Brain-Wave hooks architecture
- `rem/progress/` - Where learnings accumulate
- `skills/ralph-enhanced/` - Brain-Wave enhanced Ralph execution
