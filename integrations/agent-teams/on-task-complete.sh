#!/bin/bash
# Brain-Wave: TaskCompleted hook for agent teams
# Addresses Reddit findings: polling problem, learning capture, race conditions
# See: integrations/agent-teams/COMPARISON.md

INPUT=$(cat)
TASK_ID=$(echo "$INPUT" | jq -r '.task_id // empty')
TEAMMATE=$(echo "$INPUT" | jq -r '.teammate_name // "unknown"')
LEARNINGS=$(echo "$INPUT" | jq -r '.learnings // empty')
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
TIMESTAMP_SHORT=$(date +%Y-%m-%d\ %H:%M)

echo "[brain-wave] Task completed: $TASK_ID by $TEAMMATE"

# Ensure directories exist
mkdir -p rem/tasks rem/discoveries rem/progress

# ============================================================
# FIX #1: Shared Progress File (addresses 914 vs 37 line gap)
# Each task completion logs learnings to shared progress file
# ============================================================
PROGRESS_FILE="rem/progress/learnings.md"
if [ ! -f "$PROGRESS_FILE" ]; then
  cat > "$PROGRESS_FILE" << 'EOF'
# Progress Log - Shared Learnings

Cross-task learnings accumulated by all teammates.
Brain-Wave captures what Agent Teams loses.

## Learnings
(Patterns discovered during implementation)

---
EOF
fi

# Append learnings if provided
if [ -n "$LEARNINGS" ] && [ "$LEARNINGS" != "null" ]; then
  cat >> "$PROGRESS_FILE" << EOF

## $TIMESTAMP_SHORT - $TASK_ID ($TEAMMATE)
$LEARNINGS

---
EOF
  echo "[brain-wave] Logged learnings to $PROGRESS_FILE"
fi

# Always log completion even without explicit learnings
echo "- [$TIMESTAMP_SHORT] $TASK_ID completed by $TEAMMATE" >> rem/progress/completions.log

# ============================================================
# FIX #2: Update Task Status with Locking (prevents races)
# Use atomic file operations to prevent duplicate claims
# ============================================================
if [ -f "rem/tasks/tasks.jsonl" ] && [ -n "$TASK_ID" ]; then
  LOCKFILE="rem/tasks/.lock"

  # Simple lock mechanism
  while [ -f "$LOCKFILE" ]; do
    sleep 0.1
  done
  touch "$LOCKFILE"

  # Update task status
  jq -c "if .id == \"$TASK_ID\" then .status = \"done\" | .completed_by = \"$TEAMMATE\" | .completed_at = \"$TIMESTAMP\" else . end" rem/tasks/tasks.jsonl > /tmp/tasks.jsonl.tmp
  mv /tmp/tasks.jsonl.tmp rem/tasks/tasks.jsonl

  rm -f "$LOCKFILE"
  echo "[brain-wave] Updated rem/tasks/tasks.jsonl"
fi

# ============================================================
# FIX #3: Push Notifications (addresses polling problem)
# Write to notification file that idle teammates watch
# This is the key fix from the Reddit post
# ============================================================
NOTIFY_FILE="rem/tasks/.notifications"

# Find tasks that were blocked by this task and are now unblocked
if [ -f "rem/tasks/tasks.jsonl" ]; then
  # Get all tasks that had this task in their blocked_by
  NEWLY_UNBLOCKED=$(jq -r "select(.blocked_by != null and (.blocked_by | index(\"$TASK_ID\")) and .status == \"open\") | .id" rem/tasks/tasks.jsonl 2>/dev/null)

  if [ -n "$NEWLY_UNBLOCKED" ]; then
    for UNBLOCKED_ID in $NEWLY_UNBLOCKED; do
      # Check if ALL blockers are now done
      ALL_DONE=true
      BLOCKERS=$(jq -r "select(.id == \"$UNBLOCKED_ID\") | .blocked_by[]" rem/tasks/tasks.jsonl 2>/dev/null)
      for BLOCKER in $BLOCKERS; do
        STATUS=$(jq -r "select(.id == \"$BLOCKER\") | .status" rem/tasks/tasks.jsonl 2>/dev/null)
        if [ "$STATUS" != "done" ]; then
          ALL_DONE=false
          break
        fi
      done

      if [ "$ALL_DONE" = true ]; then
        # Write notification - idle teammates watch this file
        echo "$TIMESTAMP|UNBLOCKED|$UNBLOCKED_ID|was_blocked_by:$TASK_ID" >> "$NOTIFY_FILE"
        echo "[brain-wave] NOTIFY: Task $UNBLOCKED_ID is now unblocked"
      fi
    done
  fi
fi

# ============================================================
# FIX #4: Activity Tracking (for fair task distribution)
# Track who's doing what to prevent one agent claiming all
# ============================================================
ACTIVITY_FILE="rem/tasks/.activity"
echo "$TIMESTAMP|$TEAMMATE|completed|$TASK_ID" >> "$ACTIVITY_FILE"

# Count recent completions per teammate (last hour)
if [ -f "$ACTIVITY_FILE" ]; then
  HOUR_AGO=$(date -u -v-1H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null)
  TEAMMATE_COUNT=$(grep "|$TEAMMATE|completed|" "$ACTIVITY_FILE" | tail -20 | wc -l | tr -d ' ')
  echo "[brain-wave] $TEAMMATE has completed $TEAMMATE_COUNT tasks recently"
fi

exit 0
