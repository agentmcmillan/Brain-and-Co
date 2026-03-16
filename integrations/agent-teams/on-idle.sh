#!/bin/bash
# Brain-Wave: TeammateIdle hook for agent teams
# Addresses Reddit findings: polling → push notifications, fair claiming
# See: integrations/agent-teams/COMPARISON.md

INPUT=$(cat)
TEAMMATE=$(echo "$INPUT" | jq -r '.teammate_name // "unknown"')
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo "[brain-wave] Teammate idle: $TEAMMATE"

# Ensure directories exist
mkdir -p rem/tasks rem/progress

# ============================================================
# FIX #1: Check Notifications (push instead of poll)
# Read from notification file written by on-task-complete.sh
# This solves the "Gamma got zero tasks" problem from Reddit
# ============================================================
NOTIFY_FILE="rem/tasks/.notifications"
if [ -f "$NOTIFY_FILE" ]; then
  # Get notifications since last check
  LAST_CHECK_FILE="rem/tasks/.last_check_$TEAMMATE"
  if [ -f "$LAST_CHECK_FILE" ]; then
    LAST_CHECK=$(cat "$LAST_CHECK_FILE")
  else
    LAST_CHECK="1970-01-01T00:00:00Z"
  fi

  # Find new notifications
  NEW_NOTIFS=$(awk -F'|' -v last="$LAST_CHECK" '$1 > last && $2 == "UNBLOCKED"' "$NOTIFY_FILE" 2>/dev/null)
  if [ -n "$NEW_NOTIFS" ]; then
    echo "[brain-wave] === NEW NOTIFICATIONS ==="
    echo "$NEW_NOTIFS" | while IFS='|' read -r ts type task_id info; do
      echo "[brain-wave] Task $task_id is now READY ($info)"
    done
    echo "[brain-wave] =========================="
  fi

  # Update last check time
  echo "$TIMESTAMP" > "$LAST_CHECK_FILE"
fi

# ============================================================
# FIX #2: Fair Task Claiming (prevents one agent dominating)
# Check activity to recommend fair distribution
# ============================================================
ACTIVITY_FILE="rem/tasks/.activity"
if [ -f "$ACTIVITY_FILE" ]; then
  # Count completions per teammate
  echo "[brain-wave] Recent activity:"
  awk -F'|' '{count[$2]++} END {for(t in count) print "  " t ": " count[t] " tasks"}' "$ACTIVITY_FILE" | tail -5

  # Suggest if this teammate has been less active
  MY_COUNT=$(grep "|$TEAMMATE|" "$ACTIVITY_FILE" | wc -l | tr -d ' ')
  TOTAL_COUNT=$(wc -l < "$ACTIVITY_FILE" | tr -d ' ')
  if [ "$TOTAL_COUNT" -gt 0 ]; then
    TEAMMATE_COUNT=$(grep -c "|$TEAMMATE|" "$ACTIVITY_FILE" 2>/dev/null || echo "0")
    OTHER_AVG=$((($TOTAL_COUNT - $MY_COUNT) / 3))  # Assume ~3 teammates
    if [ "$MY_COUNT" -lt "$OTHER_AVG" ] 2>/dev/null; then
      echo "[brain-wave] $TEAMMATE has done fewer tasks - prioritize for next claim"
    fi
  fi
fi

# ============================================================
# FIX #3: Show Available Tasks with Context
# Include learnings from progress file for continuity
# ============================================================
if [ -f "rem/tasks/tasks.jsonl" ]; then
  # Find truly available tasks (open, unassigned, unblocked)
  READY_TASKS=$(jq -r 'select(
    .status == "open" and
    (.assignee == null or .assignee == "") and
    ((.blocked_by | length) == 0 or .blocked_by == null or
     (reduce .blocked_by[] as $b (true; . and (
       [inputs | select(.id == $b and .status == "done")] | length > 0
     ))))
  ) | "\(.id): \(.title)"' rem/tasks/tasks.jsonl 2>/dev/null)

  if [ -n "$READY_TASKS" ]; then
    READY_COUNT=$(echo "$READY_TASKS" | wc -l | tr -d ' ')
    echo "[brain-wave] $READY_COUNT task(s) available:"
    echo "$READY_TASKS" | head -5 | sed 's/^/  /'

    # Show relevant learnings for available tasks
    PROGRESS_FILE="rem/progress/learnings.md"
    if [ -f "$PROGRESS_FILE" ]; then
      RECENT_LEARNINGS=$(tail -30 "$PROGRESS_FILE" | grep -A2 "^## " | head -10)
      if [ -n "$RECENT_LEARNINGS" ]; then
        echo ""
        echo "[brain-wave] Recent learnings (context for next task):"
        echo "$RECENT_LEARNINGS" | sed 's/^/  /'
      fi
    fi
  else
    echo "[brain-wave] No unclaimed tasks available"

    # Check if there are blocked tasks waiting
    BLOCKED_COUNT=$(jq -r 'select(.status == "open" and .blocked_by != null and (.blocked_by | length) > 0)' rem/tasks/tasks.jsonl 2>/dev/null | wc -l | tr -d ' ')
    if [ "$BLOCKED_COUNT" -gt 0 ]; then
      echo "[brain-wave] $BLOCKED_COUNT task(s) waiting on dependencies"
      echo "[brain-wave] Watch rem/tasks/.notifications for unblock events"
    fi
  fi
fi

# ============================================================
# FIX #4: Prompt for Learning Capture
# Remind teammate to log learnings before going fully idle
# ============================================================
echo ""
echo "[brain-wave] Before going idle, consider logging learnings:"
echo "  - What patterns did you discover?"
echo "  - What gotchas should others know?"
echo "  - What context would help the next task?"
echo ""
echo "[brain-wave] Write to rem/progress/learnings.md or include in task completion"

# Log idle event for activity tracking
echo "$TIMESTAMP|$TEAMMATE|idle|" >> "$ACTIVITY_FILE" 2>/dev/null

exit 0
